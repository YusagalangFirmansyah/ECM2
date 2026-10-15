#!/usr/bin/env python3
"""
convert_watcher.py – File to PDF Auto-Converter (Polling Mode)
===============================================================
Konversi file di folder PROD ke PDF. Script ini tidak tahu DEV sama sekali
– tugasnya hanya konversi apapun yang sudah ada di PROD.

  PROD/Enggineering/EXCEL/  .xls/.xlsx  -> PDF via iLovePDF,   hapus sumber
                                           KECUALI prefix TDS_ -> pindah as-is
  PROD/Enggineering/DWG/    .dwg        -> PDF via ConvertAPI,  hapus sumber

Logika TDS:
  File Excel dengan prefix TDS_ tidak dikonversi ke PDF.
  SAP DMS Document Type TDS menyimpan file Excel asli (Default Appl = XLS).
  File cukup dipindah ke output dir as-is, lalu sap_mover.py ambil seperti biasa.

  Pembedaan dilakukan dari nama file saja — tidak perlu folder terpisah:
    BOM_[MATNR]_[DESC].BOM.xlsx  -> convert ke PDF  (Engineering biasa)
    TDS_[MATNR]_[DESC].TDS.xlsx  -> skip convert, pindah as-is

Alur kerja bersama script lain:
  watcher.py       : DEV -> PROD  (routing + Draft Old)
  convert_watcher  : PROD -> PDF  (konversi, script ini)
  sap_mover.py     : PROD -> sap_upload  (pemindahan final)

CHANGE LOG:
  v1 - Initial release
  v2 - Update path ke subfolder Enggineering/
  v3 - Tambah entry PROD/CNC/DWG/ untuk konversi DWG CNC (dihapus di v4)
       Tambah field label untuk log yang lebih jelas.
  v4 - Hapus pipeline CNC (tidak jadi digunakan).
  v5 - Skip konversi untuk file Excel dengan prefix SSC_.
       File SSC dipindah as-is ke output dir tanpa konversi PDF.
       Pembedaan via nama file, bukan folder — tidak ada perubahan di
       watcher.py maupun sap_mover.py.
  v6 - Rename prefix SSC_ -> TDS_ sesuai rename Document Type SSC -> TDS.
       SKIP_CONVERT_PREFIXES diupdate dari ['SSC_'] ke ['TDS_'].
"""

import os
import sys
import time
import logging
import zipfile
import io
import base64
import requests

# ══════════════════════════════════════════════════════
#  KONFIGURASI
# ══════════════════════════════════════════════════════

WATCH_DIRECTORIES = [
    # ── Engineering ───────────────────────────────────────────────────────
    {
        "path":       "/mnt/dropbox/PRODUCTS ENGINEERING (PROD)/Enggineering/EXCEL",
        "extensions": [".xls", ".xlsx"],
        "mode":       "convert_excel",
        "label":      "ENG-EXCEL",
    },
    {
        "path":       "/mnt/dropbox/PRODUCTS ENGINEERING (PROD)/Enggineering/DWG",
        "extensions": [".dwg"],
        "mode":       "convert_dwg",
        "label":      "ENG-DWG",
    },
]

ILOVEPDF_PUBLIC_KEY  = "project_public_96c84000342cbde51a445fe318383932_YnzVC9292f7766900bfb116a566205146365e"
CONVERTAPI_API_TOKEN = "jzDdrKx5jzgpKpxRm4DGSWTlcSDCbEW4"

DELETE_ON_SUCCESS = True
POLL_INTERVAL     = 10
API_TIMEOUT       = 30
FILE_TIMEOUT      = 300
SKIP_PATTERNS     = ['~$', '.', 'tmp']

# Prefix nama file Excel yang tidak perlu dikonversi ke PDF.
# File ini dipindah as-is ke output dir (format asli dipertahankan).
# Tambahkan prefix baru di sini jika ada tipe dokumen serupa di masa depan.
SKIP_CONVERT_PREFIXES = ['TDS_']

# ══════════════════════════════════════════════════════
#  LOGGING
# ══════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════
#  ILOVEPDF API – konversi Excel
# ══════════════════════════════════════════════════════

def get_ilovepdf_token():
    try:
        resp = requests.post(
            "https://api.ilovepdf.com/v1/auth",
            json={"public_key": ILOVEPDF_PUBLIC_KEY},
            timeout=API_TIMEOUT,
        )
        if resp.status_code == 200:
            return resp.json().get("token")
        log.error("Gagal mendapatkan token iLovePDF: %s - %s", resp.status_code, resp.text)
    except Exception as e:
        log.error("Error saat ambil token iLovePDF: %s", e)
    return None


def convert_excel_to_pdf(file_path, output_dir):
    """Konversi file Excel ke PDF via iLovePDF."""
    filename     = os.path.basename(file_path)
    base_name    = filename.rsplit(".", 1)[0]
    output_fname = f"{base_name}.pdf"
    output_path  = os.path.join(output_dir, output_fname)

    token = get_ilovepdf_token()
    if not token:
        log.error("[%s] Gagal mendapatkan token iLovePDF", filename)
        return False, None

    headers = {"Authorization": f"Bearer {token}"}
    try:
        log.info("[%s] Konversi Excel -> PDF via iLovePDF...", filename)

        r = requests.get(
            "https://api.ilovepdf.com/v1/start/officepdf",
            headers=headers, timeout=API_TIMEOUT,
        )
        if r.status_code != 200:
            log.error("[%s] Gagal start task: %s", filename, r.status_code)
            return False, None

        server_url = f"https://{r.json()['server']}"
        task_id    = r.json()["task"]

        log.info("[%s] Upload...", filename)
        with open(file_path, "rb") as f:
            up = requests.post(
                f"{server_url}/v1/upload",
                headers=headers,
                data={"task": task_id},
                files={"file": (filename, f)},
                timeout=FILE_TIMEOUT,
            )
        if up.status_code not in [200, 201]:
            log.error("[%s] Upload gagal: %s", filename, up.status_code)
            return False, None

        server_filename = up.json()["server_filename"]

        log.info("[%s] Process...", filename)
        pr = requests.post(
            f"{server_url}/v1/process",
            headers=headers,
            json={
                "task": task_id,
                "tool": "officepdf",
                "files": [{"server_filename": server_filename, "filename": output_fname}],
            },
            timeout=FILE_TIMEOUT,
        )
        if pr.status_code != 200:
            log.error("[%s] Proses gagal: %s", filename, pr.status_code)
            return False, None

        log.info("[%s] Download...", filename)
        dl = requests.get(
            f"{server_url}/v1/download/{task_id}",
            headers=headers, timeout=FILE_TIMEOUT,
        )
        if dl.status_code != 200:
            log.error("[%s] Download gagal: %s", filename, dl.status_code)
            return False, None

        os.makedirs(output_dir, exist_ok=True)
        content_type = dl.headers.get("Content-Type", "")
        if "zip" in content_type or dl.content[:2] == b"PK":
            with zipfile.ZipFile(io.BytesIO(dl.content)) as zf:
                pdf_files = [n for n in zf.namelist() if n.lower().endswith(".pdf")]
                if not pdf_files:
                    log.error("[%s] ZIP tidak mengandung PDF", filename)
                    return False, None
                with zf.open(pdf_files[0]) as pf:
                    with open(output_path, "wb") as out:
                        out.write(pf.read())
        else:
            with open(output_path, "wb") as f:
                f.write(dl.content)

        size_kb = os.path.getsize(output_path) // 1024
        log.info("[%s] Tersimpan -> %s (%d KB)", filename, output_path, size_kb)
        return True, output_path

    except requests.exceptions.Timeout:
        log.error("[%s] Timeout saat konversi via iLovePDF", filename)
        return False, None
    except Exception as e:
        log.error("[%s] Error konversi Excel: %s", filename, e)
        return False, None


# ══════════════════════════════════════════════════════
#  CONVERTAPI – konversi DWG
# ══════════════════════════════════════════════════════

def convert_dwg_to_pdf(file_path, output_dir):
    """Konversi DWG ke PDF via ConvertAPI."""
    filename     = os.path.basename(file_path)
    base_name    = filename.rsplit(".", 1)[0]
    output_fname = f"{base_name}.pdf"
    output_path  = os.path.join(output_dir, output_fname)

    headers = {"Authorization": f"Bearer {CONVERTAPI_API_TOKEN}"}

    try:
        log.info("[%s] Konversi DWG -> PDF via ConvertAPI...", filename)

        with open(file_path, "rb") as f:
            response = requests.post(
                "https://v2.convertapi.com/convert/dwg/to/pdf",
                headers=headers,
                data={
                    "SpaceToConvert": "all",
                    "StoreFile":      "true",
                    "AutoFit":        "true",
                    "ColorSpace":     "monochrome",
                },
                files={"File": (filename, f, "application/octet-stream")},
                timeout=FILE_TIMEOUT,
            )

        log.info("[%s] ConvertAPI HTTP %s", filename, response.status_code)

        if response.status_code != 200:
            try:
                err  = response.json()
                code = err.get("Code", response.status_code)
                msg  = err.get("Message") or err.get("error") or str(err)
                log.error("[%s] ConvertAPI Error %s: %s", filename, code, msg[:300])
            except Exception:
                log.error("[%s] ConvertAPI HTTP %s: %s", filename, response.status_code, response.text[:300])
            return False, None

        resp_json = response.json()

        if "Files" not in resp_json or not resp_json["Files"]:
            log.error("[%s] Tidak ada Files di response: %s", filename, str(resp_json)[:300])
            return False, None

        file_obj = resp_json["Files"][0]

        download_url = (
            file_obj.get("Url") or
            file_obj.get("url") or
            file_obj.get("FileUrl") or
            file_obj.get("DownloadUrl")
        )

        if download_url:
            log.info("[%s] Download dari URL...", filename)
            pdf_resp = requests.get(download_url, timeout=FILE_TIMEOUT)
            if pdf_resp.status_code != 200:
                log.error("[%s] Gagal download PDF (HTTP %s)", filename, pdf_resp.status_code)
                return False, None
            pdf_content = pdf_resp.content
        elif file_obj.get("FileData"):
            log.info("[%s] Decode FileData (base64)...", filename)
            pdf_content = base64.b64decode(file_obj["FileData"])
        else:
            log.error("[%s] Tidak ada URL/FileData. Keys: %s", filename, list(file_obj.keys()))
            return False, None

        os.makedirs(output_dir, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(pdf_content)

        size_kb = os.path.getsize(output_path) // 1024
        log.info("[%s] Tersimpan -> %s (%d KB)", filename, output_path, size_kb)
        return True, output_path

    except requests.exceptions.Timeout:
        log.error("[%s] Timeout (>%ds) saat konversi DWG", filename, FILE_TIMEOUT)
        return False, None
    except Exception as e:
        log.error("[%s] Error konversi DWG: %s", filename, e)
        return False, None


# ══════════════════════════════════════════════════════
#  FILE UTILITIES
# ══════════════════════════════════════════════════════

def should_skip(filename):
    return any(filename.startswith(p) for p in SKIP_PATTERNS)


def is_file_stable(file_path, wait=3):
    try:
        s1 = os.path.getsize(file_path)
        time.sleep(wait)
        s2 = os.path.getsize(file_path)
        return s1 == s2 and s1 > 0
    except OSError:
        return False


def delete_source(file_path, filename):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            log.info("[%s] File sumber dihapus OK", filename)
    except PermissionError:
        log.error("[%s] Permission denied saat menghapus sumber", filename)
    except Exception as e:
        log.error("[%s] Gagal hapus sumber: %s", filename, e)


# ══════════════════════════════════════════════════════
#  PROSES
# ══════════════════════════════════════════════════════

def process_excel(file_path):
    filename     = os.path.basename(file_path)
    output_dir   = os.path.dirname(file_path)

    # TDS (dan prefix lain di SKIP_CONVERT_PREFIXES): tidak dikonversi ke PDF.
    # File dipindah as-is karena SAP DMS menyimpan format Excel asli.
    if any(filename.upper().startswith(p.upper()) for p in SKIP_CONVERT_PREFIXES):
        log.info("[%s] Skip konversi (prefix TDS) — pindah as-is", filename)
        if DELETE_ON_SUCCESS:
            # File sudah ada di output_dir, tidak perlu move — hanya log
            # (watcher.py sudah menaruh file di folder ini)
            log.info("[%s] SELESAI as-is (TDS)", filename)
        return

    existing_pdf = os.path.join(output_dir, f"{filename.rsplit('.', 1)[0]}.pdf")

    if os.path.exists(existing_pdf):
        try:
            os.remove(existing_pdf)
            log.info("[%s] PDF lama dihapus OK", filename)
        except Exception as e:
            log.error("[%s] Gagal hapus PDF lama: %s", filename, e)

    success, _ = convert_excel_to_pdf(file_path, output_dir)
    if success:
        if DELETE_ON_SUCCESS:
            delete_source(file_path, filename)
        log.info("[%s] SELESAI (Excel)", filename)
    else:
        log.error("[%s] GAGAL (Excel)", filename)


def process_dwg(file_path):
    filename     = os.path.basename(file_path)
    output_dir   = os.path.dirname(file_path)
    existing_pdf = os.path.join(output_dir, f"{filename.rsplit('.', 1)[0]}.pdf")

    if os.path.exists(existing_pdf):
        try:
            os.remove(existing_pdf)
            log.info("[%s] PDF lama dihapus OK", filename)
        except Exception as e:
            log.error("[%s] Gagal hapus PDF lama: %s", filename, e)

    success, _ = convert_dwg_to_pdf(file_path, output_dir)
    if success:
        if DELETE_ON_SUCCESS:
            delete_source(file_path, filename)
        log.info("[%s] SELESAI (DWG)", filename)
    else:
        log.error("[%s] GAGAL (DWG) – tidak dihapus, akan dicoba lagi", filename)


# ══════════════════════════════════════════════════════
#  SCAN & PROSES
# ══════════════════════════════════════════════════════

def scan_and_process():
    for watch_config in WATCH_DIRECTORIES:
        watch_dir   = watch_config["path"]
        allowed_ext = [e.lower() for e in watch_config["extensions"]]
        mode        = watch_config.get("mode", "convert_excel")
        label       = watch_config.get("label", mode)

        if not os.path.isdir(watch_dir):
            log.warning("[%s] Direktori tidak ditemukan: %s", label, watch_dir)
            continue

        try:
            for root, _, files in os.walk(watch_dir):
                for filename in files:
                    ext = os.path.splitext(filename)[1].lower()
                    if ext not in allowed_ext:
                        continue
                    if should_skip(filename):
                        continue

                    file_path = os.path.join(root, filename)
                    log.info("-" * 50)
                    log.info("[%s] FILE BARU: %s", label, filename)

                    if not is_file_stable(file_path):
                        log.warning("[%s] [%s] Belum stabil, dicoba lagi nanti", label, filename)
                        continue

                    if mode == "convert_excel":
                        process_excel(file_path)
                    elif mode == "convert_dwg":
                        process_dwg(file_path)

        except Exception as e:
            log.error("[%s] Error scan: %s", label, e)


# ══════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════

def main():
    log.info("=" * 55)
    log.info("convert-watcher v6 dimulai (Polling Mode)")
    log.info("Scan interval : setiap %ds", POLL_INTERVAL)
    log.info("-" * 55)
    for w in WATCH_DIRECTORIES:
        status = "OK" if os.path.isdir(w["path"]) else "TIDAK ADA"
        log.info(
            "  [%-10s] [%-8s] [%-16s] %s",
            w.get("label", w["mode"]),
            status,
            ", ".join(w["extensions"]),
            w["path"],
        )
    log.info("-" * 55)
    log.info("Excel : iLovePDF API")
    log.info("DWG   : ConvertAPI v2 (SpaceToConvert=all, ColorSpace=monochrome)")
    log.info("TDS_* : Skip konversi — pindah as-is (prefix: %s)", SKIP_CONVERT_PREFIXES)
    log.info("=" * 55)

    try:
        while True:
            scan_and_process()
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        log.info("convert-watcher dihentikan.")


if __name__ == "__main__":
    main()
