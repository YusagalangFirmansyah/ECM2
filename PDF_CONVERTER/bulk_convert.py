import os
import requests
import zipfile
import io
import logging

# --- PENGATURAN KUNCI API ---
ILOVEPDF_PUBLIC_KEY = 'project_public_96c84000342cbde51a445fe318383932_YnzVC9292f7766900bfb116a566205146365e'
CONVERTAPI_API_TOKEN = 'Zs0wcSpKbGgBtevk1dVfFoiTchS1rgFp'

# --- PENGATURAN FOLDER ---
INPUT_FOLDER = './input_files'
OUTPUT_FOLDER = './pdf_result'

# --- LOGGING ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)


# ==========================================
# FUNGSI KONVERSI
# ==========================================

def get_ilovepdf_token():
    """Meminta token autentikasi dari iLovePDF"""
    print("Meminta token akses dari iLovePDF...")
    try:
        resp = requests.post(
            "https://api.ilovepdf.com/v1/auth",
            json={"public_key": ILOVEPDF_PUBLIC_KEY},
            timeout=30
        )
        if resp.status_code == 200:
            print("✅ Token iLovePDF berhasil didapat.")
            return resp.json()['token']
        else:
            print(f"❌ Gagal mendapatkan token iLovePDF (HTTP {resp.status_code}): {resp.text[:200]}")
            return None
    except requests.exceptions.Timeout:
        print("❌ Timeout saat menghubungi server iLovePDF.")
        return None
    except Exception as e:
        print(f"❌ Error koneksi iLovePDF: {e}")
        return None


def convert_excel_ilovepdf(file_path, filename, output_filename, token):
    """Proses konversi Excel menggunakan iLovePDF"""
    headers = {"Authorization": f"Bearer {token}"}

    try:
        # Step 1: Start task
        start_req = requests.get(
            "https://api.ilovepdf.com/v1/start/officepdf",
            headers=headers, timeout=30
        )
        if start_req.status_code != 200:
            return f"Gagal membuat task (HTTP {start_req.status_code}): {start_req.text[:200]}"

        server_url = f"https://{start_req.json()['server']}"
        task_id = start_req.json()['task']
        logger.info(f"  Task dibuat: {task_id}")

        # Step 2: Upload
        with open(file_path, 'rb') as f:
            upload_resp = requests.post(
                f"{server_url}/v1/upload",
                headers=headers,
                data={'task': task_id},
                files={'file': (filename, f)},
                timeout=120
            )
        if upload_resp.status_code not in [200, 201]:
            return f"Gagal upload (HTTP {upload_resp.status_code}): {upload_resp.text[:200]}"

        server_filename = upload_resp.json()['server_filename']
        logger.info(f"  Upload OK: {server_filename}")

        # Step 3: Process
        process_resp = requests.post(
            f"{server_url}/v1/process",
            headers=headers,
            json={
                "task": task_id,
                "tool": "officepdf",
                "files": [{"server_filename": server_filename, "filename": output_filename}]
            },
            timeout=120
        )
        if process_resp.status_code != 200:
            return f"Gagal proses (HTTP {process_resp.status_code}): {process_resp.text[:200]}"

        # Step 4: Download
        download_resp = requests.get(
            f"{server_url}/v1/download/{task_id}",
            headers=headers, timeout=120
        )
        if download_resp.status_code != 200:
            return f"Gagal download (HTTP {download_resp.status_code}): {download_resp.text[:200]}"

        # Handle ZIP (kadang iLovePDF balut hasil dalam ZIP)
        out_path = os.path.join(OUTPUT_FOLDER, output_filename)
        content_type = download_resp.headers.get('Content-Type', '')
        if 'zip' in content_type or download_resp.content[:2] == b'PK':
            with zipfile.ZipFile(io.BytesIO(download_resp.content)) as zf:
                pdf_files = [n for n in zf.namelist() if n.lower().endswith('.pdf')]
                if not pdf_files:
                    return "ZIP dari iLovePDF tidak mengandung file PDF"
                with zf.open(pdf_files[0]) as pf:
                    with open(out_path, 'wb') as out:
                        out.write(pf.read())
        else:
            with open(out_path, 'wb') as f:
                f.write(download_resp.content)

        size_kb = os.path.getsize(out_path) // 1024
        logger.info(f"  Ukuran output: {size_kb} KB")
        return "SUCCESS"

    except requests.exceptions.Timeout:
        return "Timeout — file terlalu besar atau server iLovePDF lambat"
    except Exception as e:
        logger.exception("  Exception di convert_excel_ilovepdf")
        return f"Error sistem: {e}"


def convert_dwg_convertapi(file_path, output_filename):
    """Proses konversi DWG menggunakan ConvertAPI"""
    try:
        # PERBAIKAN: Gunakan Bearer Token Auth (cara baru ConvertAPI v2)
        url = "https://v2.convertapi.com/convert/dwg/to/pdf"
        headers = {"Authorization": f"Bearer {CONVERTAPI_API_TOKEN}"}
        logger.info(f"  Mengirim ke ConvertAPI...")

        with open(file_path, 'rb') as f:
            response = requests.post(
                url,
                headers=headers,
                data={
                    'SpaceToConvert': 'all',
                    'StoreFile': 'true',
                    'AutoFit': 'true',
                },
                files={'File': (os.path.basename(file_path), f, 'application/octet-stream')},
                timeout=180
            )

        logger.info(f"  HTTP response: {response.status_code}")

        if response.status_code == 200:
            resp_json = response.json()
            logger.info(f"  Response: {str(resp_json)[:500]}")

            if 'Files' not in resp_json or not resp_json['Files']:
                return f"ConvertAPI tidak mengembalikan Files. Response: {str(resp_json)[:300]}"

            file_obj = resp_json['Files'][0]
            logger.info(f"  File keys: {list(file_obj.keys())}")

            download_url = (
                file_obj.get('Url') or
                file_obj.get('url') or
                file_obj.get('FileUrl') or
                file_obj.get('DownloadUrl')
            )

            if download_url:
                pdf_resp = requests.get(download_url, timeout=60)
                if pdf_resp.status_code != 200:
                    return f"Gagal download PDF (HTTP {pdf_resp.status_code})"
                pdf_content = pdf_resp.content
            elif file_obj.get('FileData'):
                import base64
                pdf_content = base64.b64decode(file_obj['FileData'])
            else:
                return f"Tidak ada URL/data di response. Keys: {list(file_obj.keys())}"

            out_path = os.path.join(OUTPUT_FOLDER, output_filename)
            with open(out_path, 'wb') as f:
                f.write(pdf_content)

            size_kb = os.path.getsize(out_path) // 1024
            logger.info(f"  Ukuran output: {size_kb} KB")
            return "SUCCESS"

        else:
            # Parse pesan error dari ConvertAPI
            try:
                err_json = response.json()
                code = err_json.get('Code', response.status_code)
                msg = err_json.get('Message') or err_json.get('error') or str(err_json)
                return f"ConvertAPI Error {code}: {msg[:300]}"
            except Exception:
                return f"ConvertAPI HTTP {response.status_code}: {response.text[:300]}"

    except requests.exceptions.Timeout:
        return "Timeout (>180 detik) — file DWG terlalu besar atau ConvertAPI lambat"
    except Exception as e:
        logger.exception("  Exception di convert_dwg_convertapi")
        return f"Error sistem: {e}"


# ==========================================
# MAIN
# ==========================================

def main():
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    if not os.path.exists(INPUT_FOLDER):
        os.makedirs(INPUT_FOLDER)
        print(f"📁 Folder '{INPUT_FOLDER}' dibuat. Masukkan file lalu jalankan ulang script.")
        return

    all_files = os.listdir(INPUT_FOLDER)
    files_to_process = [f for f in all_files if f.lower().endswith(('.xls', '.xlsx', '.dwg'))]

    if not files_to_process:
        print(f"⚠️  Tidak ada file Excel/DWG di folder '{INPUT_FOLDER}'.")
        return

    print(f"\n{'='*50}")
    print(f"  DocConvert CLI — Bulk Converter")
    print(f"{'='*50}")
    print(f"  Ditemukan {len(files_to_process)} file untuk diproses.\n")

    # Ambil token iLovePDF sekali jika ada Excel
    ilovepdf_token = None
    has_excel = any(f.lower().endswith(('.xls', '.xlsx')) for f in files_to_process)
    if has_excel:
        ilovepdf_token = get_ilovepdf_token()
        if not ilovepdf_token:
            print("⚠️  Konversi Excel akan dilewati (gagal mendapat token iLovePDF).\n")

    print(f"{'-'*50}")

    results = []
    for filename in files_to_process:
        file_path = os.path.join(INPUT_FOLDER, filename)
        base_name = filename.rsplit('.', 1)[0]
        ext = filename.split('.')[-1].lower()
        # Tambahkan ekstensi asli ke output agar tidak saling timpa
        output_filename = f"{base_name}_{ext}.pdf"

        if ext in ['xls', 'xlsx']:
            if not ilovepdf_token:
                print(f"⏭️  Melewati : {filename} (tidak ada token iLovePDF)")
                results.append((filename, "SKIP"))
                continue
            print(f"📗 [Excel → iLovePDF] {filename}")
            result = convert_excel_ilovepdf(file_path, filename, output_filename, ilovepdf_token)

        elif ext == 'dwg':
            print(f"📐 [DWG → ConvertAPI] {filename}")
            result = convert_dwg_convertapi(file_path, output_filename)

        else:
            result = f"Format '.{ext}' tidak didukung"

        if result == "SUCCESS":
            print(f"   ✅ Berhasil → {output_filename}\n")
        else:
            print(f"   ❌ Gagal: {result}\n")

        results.append((filename, result))

    # Ringkasan akhir
    print(f"{'='*50}")
    success = sum(1 for _, r in results if r == "SUCCESS")
    failed  = sum(1 for _, r in results if r not in ("SUCCESS", "SKIP"))
    skipped = sum(1 for _, r in results if r == "SKIP")
    print(f"  Selesai! Total: {len(results)} | ✅ {success} | ❌ {failed} | ⏭️  {skipped}")
    print(f"  Output tersimpan di: {os.path.abspath(OUTPUT_FOLDER)}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
