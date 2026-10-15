"""
sap_mover.py - Background SAP Upload Mover
===========================================
Ambil file dari PROD dan pindahkan ke /mnt/sap_upload.
Script ini tidak tahu DEV sama sekali - hanya ambil dari PROD.

Arsitektur folder tujuan:
  /mnt/sap_upload/
    +-- engineering/   <- PDF dari PROD/Enggineering/EXCEL & DWG
        +-- error/        (ZUPLOAD_CS_AUTO, p_dir = /mnt/sap_upload/engineering/)

Alur kerja bersama script lain:
  watcher.py       : DEV -> PROD (routing + Draft Old)
  convert_watcher  : PROD -> PDF (konversi)
  sap_mover.py     : PROD PDF -> sap_upload (script ini)

Harus dijalankan sebagai root (User=root di systemd)
karena /mnt/sap_upload mount CIFS dengan uid=1002.

CHANGE LOG:
  v2 - Hapus logika suffix _xls.
  v3 - Tambah sanitasi nama file + cleanup_existing() saat startup.
  v4 - Pisah tujuan ke subfolder engineering/ dan cnc/.
       Gunakan tabel ROUTING - tambah pipeline baru cukup tambah entry.
       ensure_dirs(): buat subfolder + error/ otomatis saat startup.
       cleanup_existing(): scan semua subfolder tujuan.
  v5 - Hapus pipeline CNC (tidak jadi digunakan).
  v6 - Tambah route TDS-EXCEL: ambil .xls/.xlsx dari PROD/Enggineering/EXCEL/
       ke engineering/. File TDS tidak dikonversi ke PDF di convert_watcher
       (prefix TDS_ di-skip), diambil as-is oleh sap_mover.
"""

import re
import shutil
import logging
import time
import sys
from pathlib import Path

# ======================================================
#  CONFIG
# ======================================================

BASE_DEST = Path("/mnt/sap_upload")
PROD_ROOT = Path("/mnt/dropbox/PRODUCTS ENGINEERING (PROD)")

ROUTING = [
    # -- Engineering PDF -> engineering/ ----------------------------------
    {
        "source": PROD_ROOT / "Enggineering" / "EXCEL",
        "exts":   (".pdf",),
        "dest":   BASE_DEST / "engineering",
        "label":  "ENG-EXCEL",
    },
    {
        "source": PROD_ROOT / "Enggineering" / "DWG",
        "exts":   (".pdf",),
        "dest":   BASE_DEST / "engineering",
        "label":  "ENG-DWG",
    },

    # -- TDS Excel -> engineering/ (tanpa konversi PDF) -------------------
    # File .xlsx TDS tidak dikonversi di convert_watcher (prefix TDS_ di-skip).
    # Diambil as-is dari folder EXCEL yang sama dan dikirim ke sap_upload.
    # FILTER PENTING: hanya file dengan prefix TDS_ yang diambil,
    # agar tidak race condition dengan file BOM Excel yang sedang
    # diproses konversi oleh convert_watcher.
    {
        "source":     PROD_ROOT / "Enggineering" / "EXCEL",
        "exts":       (".xls", ".xlsx"),
        "prefix":     "TDS_",
        "dest":       BASE_DEST / "engineering",
        "label":      "TDS-EXCEL",
    },
]

POLL_SECONDS = 60

# ======================================================
#  LOGGING
# ======================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("sap-mover")


# ======================================================
#  HELPERS
# ======================================================

def sanitize_filename(name: str) -> str:
    name = name.replace('\r', '').replace('\n', '')
    name = re.sub(r'\s+', ' ', name).strip()
    return name


def ensure_dirs():
    dest_dirs = {r["dest"] for r in ROUTING}
    for d in dest_dirs:
        d.mkdir(parents=True, exist_ok=True)
        (d / "error").mkdir(parents=True, exist_ok=True)
        log.info("Dir siap   : %s", d)


def cleanup_existing():
    dest_dirs = {r["dest"] for r in ROUTING}
    for dest_dir in dest_dirs:
        if not dest_dir.exists():
            continue
        fixed = 0
        for f in dest_dir.iterdir():
            if not f.is_file():
                continue
            clean_name = sanitize_filename(f.name)
            if clean_name != f.name:
                try:
                    f.rename(dest_dir / clean_name)
                    log.info("  Renamed corrupt -> %s", clean_name)
                    fixed += 1
                except Exception as e:
                    log.error("  Gagal rename %r: %s", f.name, e)
        if fixed:
            log.info("Cleanup [%s]: %d file diperbaiki", dest_dir.name, fixed)
        else:
            log.info("Cleanup [%s]: tidak ada file corrupt", dest_dir.name)


# ======================================================
#  CORE
# ======================================================

def move_files():
    for route in ROUTING:
        source_dir = route["source"]
        dest_dir   = route["dest"]
        exts       = route["exts"]
        label      = route["label"]
        prefix     = route.get("prefix", "")   # opsional, default = ambil semua

        if not source_dir.exists():
            log.warning("[%s] Source tidak ditemukan: %s", label, source_dir)
            continue

        matched = [
            f for f in source_dir.iterdir()
            if f.is_file()
            and f.suffix.lower() in exts
            and (not prefix or f.name.upper().startswith(prefix.upper()))
        ]

        if not matched:
            continue

        log.info("[%s] Ditemukan %d file", label, len(matched))

        for src in matched:
            clean_name = sanitize_filename(src.name)
            dest       = dest_dir / clean_name

            if clean_name != src.name:
                log.warning("  [%s] Nama disanitasi: %r -> %s", label, src.name, clean_name)

            try:
                shutil.move(str(src), str(dest))
                log.info("  OK [%s] %s", label, clean_name)
            except Exception as exc:
                log.error("  GAGAL [%s] %s: %s", label, clean_name, exc)


# ======================================================
#  MAIN
# ======================================================

def main():
    log.info("=" * 55)
    log.info("sap-mover v6 dimulai")
    log.info("Base dest  : %s", BASE_DEST)
    log.info("Interval   : %ds", POLL_SECONDS)
    log.info("-" * 55)

    for route in ROUTING:
        src_status = "OK" if route["source"].exists() else "TIDAK ADA"
        log.info(
            "Route [%-10s]: %-9s %s  ->  %s",
            route["label"],
            src_status,
            route["source"],
            route["dest"].name,
        )

    log.info("-" * 55)
    ensure_dirs()
    log.info("-" * 55)
    log.info("Startup cleanup ...")
    cleanup_existing()
    log.info("=" * 55)

    while True:
        try:
            move_files()
        except Exception as exc:
            log.error("Error tidak terduga: %s", exc)
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
