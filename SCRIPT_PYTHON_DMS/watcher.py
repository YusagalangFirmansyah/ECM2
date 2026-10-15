"""
watcher.py – Background file watcher (Pure Polling)
=====================================================
Satu-satunya script yang memantau folder DEV (pintu masuk dari Dropbox).
Menangani pipeline: Engineering.

PIPELINE ENGINEERING
  Sumber : PRODUCTS_ENGINEERING_DEV/**
  Proses :
    1. Tunggu SETTLE_SECONDS (file selesai sync)
    2. Copy ke PROD/Enggineering/EXCEL (.xls/.xlsx)
       atau PROD/Enggineering/DWG (.dwg/.pdf)
    3. Copy ke Draft Old di folder asal (prefix tanggal+jam)
    4. Hapus file asli

Tanggung jawab masing-masing script:
  watcher.py        : scan DEV, routing, Draft Old

CHANGE LOG:
  v1 - Initial release, polling mode murni, engineering only
  v2 - Update path PROD ke subfolder Enggineering/
  v3 - Tambah pipeline CNC (dihapus di v4)
       Refactor: pisah konfigurasi DEV_SOURCES agar mudah ditambah pipeline baru
  v4 - Hapus pipeline CNC (tidak jadi digunakan)
       Tambah skip_dirs: "Folder Trash (Tidak Terdeteksi Sistem)"
"""

import shutil
import logging
import time
import re
import sys
from datetime import datetime
from pathlib import Path

# ══════════════════════════════════════════════════════
#  KONFIGURASI
# ══════════════════════════════════════════════════════

PROD_ROOT     = Path("/mnt/dropbox/PRODUCTS ENGINEERING (PROD)")
SAP_UPLOAD    = Path("/mnt/sap_upload")
DRAFT_OLD     = "Draft Old"
SETTLE_SECS   = 10
POLL_INTERVAL = 60

# Definisi setiap pipeline DEV.
# Setiap entry menjelaskan satu folder DEV yang dipantau beserta
# aturan routing file-nya.
#
# Struktur setiap pipeline:
#   root      : folder DEV yang di-scan (rglob)
#   exts      : ekstensi yang diproses
#   skip_dirs : nama subfolder yang diabaikan (Draft Old, dll)
#   routes    : list aturan routing, dicocokkan dari atas ke bawah
#               - exts  : tuple ekstensi yang cocok
#               - dest  : Path tujuan
#               Jika tidak ada yang cocok, file dilewati

DEV_SOURCES = [
    # ── Engineering ───────────────────────────────────────────────────────
    {
        "name":      "ENGINEERING",
        "root":      Path("/mnt/dropbox/PRODUCTS_ENGINEERING_DEV"),
        "exts":      {".xls", ".xlsx", ".dwg", ".pdf"},
        "skip_dirs": {DRAFT_OLD, "Folder Sampah (Tidak Terdeteksi Sistem)", "Progammer"},
        "skip_re":   r"^\d{4}-\d{2}-\d{2} \d{2}\.\d{2} - ",  # sudah diarsip
        "draft_old": True,
        "routes": [
            {
                "exts": (".xls", ".xlsx"),
                "dest": PROD_ROOT / "Enggineering" / "EXCEL",
            },
            {
                "exts": (".dwg", ".pdf"),
                "dest": PROD_ROOT / "Enggineering" / "DWG",
            },
        ],
    },
]

# ══════════════════════════════════════════════════════
#  LOGGING
# ══════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("doc-watcher")

# ══════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════

def is_eligible(path: Path, pipeline: dict) -> bool:
    """Cek apakah file eligible untuk diproses dalam pipeline ini."""
    if not path.is_file():
        return False
    if path.suffix.lower() not in pipeline["exts"]:
        return False
    # Skip subfolder tertentu (Draft Old, Folder Trash, dll)
    if any(d in path.parts for d in pipeline["skip_dirs"]):
        return False
    # Skip file yang sudah punya prefix tanggal (sudah diarsip)
    if re.match(pipeline["skip_re"], path.name):
        return False
    return True


def get_eligible_files(pipeline: dict) -> list[Path]:
    """Scan folder DEV pipeline dan kembalikan semua file yang eligible."""
    root = pipeline["root"]
    try:
        return [p for p in root.rglob("*") if is_eligible(p, pipeline)]
    except Exception as e:
        log.error("[%s] Error saat scan: %s", pipeline["name"], e)
        return []


def get_dest(path: Path, pipeline: dict) -> Path | None:
    """Tentukan folder tujuan berdasarkan ekstensi file dan routing pipeline."""
    ext = path.suffix.lower()
    for route in pipeline["routes"]:
        if ext in route["exts"]:
            return route["dest"]
    return None


def process_file(src: Path, pipeline: dict):
    """
    Proses satu file:
      1. Tentukan tujuan berdasarkan routing pipeline
      2. Copy ke Draft Old (jika pipeline punya draft_old=True)
      3. Pindah (move) ke tujuan
      4. Hapus file asli (sudah di-handle shutil.move)
    """
    if not src.exists():
        log.warning("[%s] File sudah tidak ada: %s", pipeline["name"], src.name)
        return

    name  = pipeline["name"]
    today = datetime.now().strftime("%Y-%m-%d %H.%M")

    # 1. Tentukan tujuan
    dest_dir = get_dest(src, pipeline)
    if dest_dir is None:
        log.warning("[%s] Tidak ada route untuk ekstensi %s: %s", name, src.suffix, src.name)
        return

    log.info("[%s] Memproses: %s", name, src.name)

    # 2. Copy ke Draft Old
    if pipeline.get("draft_old"):
        try:
            draft_dir = src.parent / DRAFT_OLD
            draft_dir.mkdir(parents=True, exist_ok=True)
            draft_dest = draft_dir / f"{today} - {src.name}"
            shutil.copy2(src, draft_dest)
            log.info("  OK Draft Old: %s", draft_dest.name)
        except Exception as e:
            log.error("  GAGAL copy ke Draft Old: %s", e)
            return  # batalkan, jangan hapus asli

    # 3. Move ke tujuan (sekaligus hapus asli)
    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dest_dir / src.name))
        log.info("  OK -> %s/%s", dest_dir.name, src.name)
    except Exception as e:
        log.error("  GAGAL move ke %s: %s", dest_dir.name, e)


# ══════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════

def main():
    # Validasi semua DEV root saat startup
    for pipeline in DEV_SOURCES:
        if not pipeline["root"].exists():
            log.warning(
                "[%s] DEV root tidak ditemukan: %s",
                pipeline["name"], pipeline["root"],
            )

    log.info("=" * 55)
    log.info("doc-watcher v4 dimulai (Pure Polling Mode)")
    log.info("Settle   : %ds  |  Poll : %ds", SETTLE_SECS, POLL_INTERVAL)
    log.info("-" * 55)
    for pipeline in DEV_SOURCES:
        status = "OK" if pipeline["root"].exists() else "TIDAK ADA"
        log.info("[%-12s] %-9s %s", pipeline["name"], status, pipeline["root"])
        for route in pipeline["routes"]:
            log.info(
                "  %-28s -> %s",
                str(route["exts"]),
                route["dest"].relative_to(route["dest"].anchor),
            )
    log.info("=" * 55)

    # pending = { (pipeline_name, path): waktu_pertama_terdeteksi }
    pending: dict[tuple[str, Path], float] = {}

    # Scan awal – file yang sudah ada sebelum service start
    for pipeline in DEV_SOURCES:
        existing = get_eligible_files(pipeline)
        if existing:
            log.info(
                "[%s] %d file existing ditemukan, langsung diproses...",
                pipeline["name"], len(existing),
            )
            for path in existing:
                key = (pipeline["name"], path)
                pending[key] = time.monotonic() - SETTLE_SECS
        else:
            log.info("[%s] Tidak ada file existing, standby...", pipeline["name"])

    try:
        while True:
            # Scan semua pipeline, tambah file baru ke pending
            for pipeline in DEV_SOURCES:
                for path in get_eligible_files(pipeline):
                    key = (pipeline["name"], path)
                    if key not in pending:
                        log.info(
                            "[%s] Terdeteksi: %s – menunggu %ds...",
                            pipeline["name"], path.name, SETTLE_SECS,
                        )
                        pending[key] = time.monotonic()

            # Proses file yang sudah melewati SETTLE_SECS
            now   = time.monotonic()
            ready = [k for k, t in pending.items() if now - t >= SETTLE_SECS]
            for key in ready:
                pipeline_name, path = key
                del pending[key]
                # Cari pipeline yang sesuai
                pipeline = next(
                    (p for p in DEV_SOURCES if p["name"] == pipeline_name), None
                )
                if pipeline:
                    process_file(path, pipeline)

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        log.info("doc-watcher dihentikan.")


if __name__ == "__main__":
    main()
