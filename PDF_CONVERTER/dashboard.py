import os
import requests
import zipfile
import io
import logging
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Flask, request, render_template_string, send_from_directory, send_file, jsonify

# --- PENGATURAN KUNCI API ---
ILOVEPDF_PUBLIC_KEY = 'project_public_96c84000342cbde51a445fe318383932_YnzVC9292f7766900bfb116a566205146365e'
CONVERTAPI_API_TOKEN = 'jzDdrKx5jzgpKpxRm4DGSWTlcSDCbEW4'

# --- INISIALISASI FLASK APP ---
app = Flask(__name__)
app.config['INPUT_FOLDER']  = './input_files'
app.config['OUTPUT_FOLDER'] = './pdf_result'
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)

os.makedirs(app.config['INPUT_FOLDER'],  exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

HISTORY_FILE = './conversion_history.json'

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(batch):
    history = load_history()
    history.insert(0, batch)
    history = history[:50]
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def get_output_files():
    folder = app.config['OUTPUT_FOLDER']
    files = []
    for fname in os.listdir(folder):
        if fname.lower().endswith('.pdf'):
            fpath = os.path.join(folder, fname)
            stat = os.stat(fpath)
            files.append({
                'name': fname,
                'size_kb': stat.st_size // 1024,
                'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%d %b %Y, %H:%M')
            })
    files.sort(key=lambda x: x['modified'], reverse=True)
    return files


# ==========================================
# FUNGSI KONVERSI
# ==========================================

def get_ilovepdf_token():
    try:
        resp = requests.post(
            "https://api.ilovepdf.com/v1/auth",
            json={"public_key": ILOVEPDF_PUBLIC_KEY},
            timeout=30
        )
        if resp.status_code == 200:
            logger.info("[iLovePDF] Token OK")
            return resp.json()['token'], None
        err = f"Auth gagal (HTTP {resp.status_code}): {resp.text[:300]}"
        logger.error(err)
        return None, err
    except requests.exceptions.Timeout:
        return None, "Timeout (30s) menghubungi iLovePDF"
    except Exception as e:
        return None, f"Error koneksi iLovePDF: {e}"


def convert_excel_ilovepdf(file_path, filename, output_filename, token):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        start_req = requests.get(
            "https://api.ilovepdf.com/v1/start/officepdf",
            headers=headers, timeout=30
        )
        if start_req.status_code != 200:
            return False, f"Gagal membuat task (HTTP {start_req.status_code}): {start_req.text[:200]}"

        data = start_req.json()
        server_url = f"https://{data['server']}"
        task_id = data['task']
        logger.info(f"[Excel] Task {task_id}")

        with open(file_path, 'rb') as f:
            upload_resp = requests.post(
                f"{server_url}/v1/upload",
                headers=headers,
                data={'task': task_id},
                files={'file': (filename, f)},
                timeout=120
            )
        if upload_resp.status_code not in [200, 201]:
            return False, f"Upload gagal (HTTP {upload_resp.status_code}): {upload_resp.text[:200]}"

        server_filename = upload_resp.json()['server_filename']
        logger.info(f"[Excel] Upload OK: {server_filename}")

        process_resp = requests.post(
            f"{server_url}/v1/process",
            headers=headers,
            json={
                "task": task_id, "tool": "officepdf",
                "files": [{"server_filename": server_filename, "filename": output_filename}]
            },
            timeout=120
        )
        if process_resp.status_code != 200:
            return False, f"Proses gagal (HTTP {process_resp.status_code}): {process_resp.text[:200]}"

        download_resp = requests.get(
            f"{server_url}/v1/download/{task_id}",
            headers=headers, timeout=120
        )
        if download_resp.status_code != 200:
            return False, f"Download gagal (HTTP {download_resp.status_code}): {download_resp.text[:200]}"

        out_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        content_type = download_resp.headers.get('Content-Type', '')
        if 'zip' in content_type or download_resp.content[:2] == b'PK':
            with zipfile.ZipFile(io.BytesIO(download_resp.content)) as zf:
                pdf_files = [n for n in zf.namelist() if n.lower().endswith('.pdf')]
                if not pdf_files:
                    return False, "ZIP dari iLovePDF tidak mengandung PDF"
                with zf.open(pdf_files[0]) as pf:
                    with open(out_path, 'wb') as out:
                        out.write(pf.read())
        else:
            with open(out_path, 'wb') as f:
                f.write(download_resp.content)

        size_kb = os.path.getsize(out_path) // 1024
        logger.info(f"[Excel] Selesai: {output_filename} ({size_kb} KB)")
        return True, None

    except requests.exceptions.Timeout:
        return False, "Timeout — file terlalu besar atau server iLovePDF lambat"
    except Exception as e:
        logger.exception("[Excel] Exception")
        return False, f"Error sistem: {e}"


def convert_dwg_convertapi(file_path, output_filename):
    try:
        # PERBAIKAN: Gunakan Bearer Token Auth (cara baru ConvertAPI v2)
        url = "https://v2.convertapi.com/convert/dwg/to/pdf"
        headers = {"Authorization": f"Bearer {CONVERTAPI_API_TOKEN}"}
        logger.info(f"[DWG] Mengirim: {os.path.basename(file_path)}")

        with open(file_path, 'rb') as f:
            response = requests.post(
                url,
                headers=headers,
                data={
                    'SpaceToConvert': 'all',
                    'StoreFile':      'true',
                    'AutoFit':        'true',
                    'ColorSpace':     'monochrome',   # ? tambah di sini
                },
                files={'File': (os.path.basename(file_path), f, 'application/octet-stream')},
                timeout=180
            )

        logger.info(f"[DWG] HTTP {response.status_code}")

        if response.status_code == 200:
            resp_json = response.json()
            logger.info(f"[DWG] Response: {str(resp_json)[:500]}")

            if 'Files' not in resp_json or not resp_json['Files']:
                return False, f"ConvertAPI tidak mengembalikan Files. Response: {str(resp_json)[:300]}"

            file_obj = resp_json['Files'][0]
            logger.info(f"[DWG] File keys tersedia: {list(file_obj.keys())}")

            # Handle berbagai kemungkinan key URL dari ConvertAPI
            download_url = (
                file_obj.get('Url') or
                file_obj.get('url') or
                file_obj.get('FileUrl') or
                file_obj.get('DownloadUrl')
            )

            if download_url:
                # Ada URL — download dari sana
                pdf_resp = requests.get(download_url, timeout=60)
                if pdf_resp.status_code != 200:
                    return False, f"Gagal download PDF (HTTP {pdf_resp.status_code})"
                pdf_content = pdf_resp.content
            elif file_obj.get('FileData'):
                # Base64 encoded — decode langsung
                import base64
                pdf_content = base64.b64decode(file_obj['FileData'])
            else:
                return False, f"Tidak ada URL/data di response. Keys: {list(file_obj.keys())}"

            out_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
            with open(out_path, 'wb') as f:
                f.write(pdf_content)
            size_kb = os.path.getsize(out_path) // 1024
            logger.info(f"[DWG] Selesai: {output_filename} ({size_kb} KB)")
            return True, None

        else:
            try:
                err_json = response.json()
                code = err_json.get('Code', response.status_code)
                msg = err_json.get('Message') or err_json.get('error') or str(err_json)
                return False, f"ConvertAPI Error {code}: {msg[:300]}"
            except Exception:
                return False, f"ConvertAPI HTTP {response.status_code}: {response.text[:300]}"

    except requests.exceptions.Timeout:
        return False, "Timeout (>180 detik) — file DWG terlalu besar atau ConvertAPI lambat"
    except Exception as e:
        logger.exception("[DWG] Exception")
        return False, f"Error sistem: {e}"


# ==========================================
# HTML TEMPLATE
# ==========================================
HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DocConvert Pro — PWID</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        :root {
            --bg:      #080a0f;
            --bg2:     #0d1117;
            --surface: #111827;
            --surf2:   #1a2236;
            --border:  #1e2d45;
            --border2: #243352;
            --accent:  #3b82f6;
            --accent2: #60a5fa;
            --glow:    rgba(59,130,246,0.18);
            --ok:      #10b981;
            --err:     #f43f5e;
            --text:    #e2e8f0;
            --muted:   #64748b;
            --muted2:  #94a3b8;
            --mono:    'JetBrains Mono', monospace;
            --sans:    'Syne', sans-serif;
        }
        html { scroll-behavior: smooth; }
        body {
            background: var(--bg);
            color: var(--text);
            font-family: var(--sans);
            min-height: 100vh;
            overflow-x: hidden;
        }
        body::before {
            content: '';
            position: fixed; inset: 0;
            background-image:
                linear-gradient(rgba(59,130,246,0.025) 1px, transparent 1px),
                linear-gradient(90deg, rgba(59,130,246,0.025) 1px, transparent 1px);
            background-size: 48px 48px;
            pointer-events: none; z-index: 0;
        }
        body::after {
            content: '';
            position: fixed;
            top: -300px; left: 50%; transform: translateX(-50%);
            width: 900px; height: 700px;
            background: radial-gradient(ellipse, rgba(59,130,246,0.07) 0%, transparent 65%);
            pointer-events: none; z-index: 0;
        }

        /* LAYOUT */
        .shell { display: grid; grid-template-columns: 256px 1fr; min-height: 100vh; position: relative; z-index: 1; }

        /* SIDEBAR */
        .sidebar {
            background: var(--bg2); border-right: 1px solid var(--border);
            display: flex; flex-direction: column;
            position: sticky; top: 0; height: 100vh; overflow-y: auto;
        }
        .sb-brand { padding: 24px 20px; border-bottom: 1px solid var(--border); }
        .sb-logo { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
        .sb-icon {
            width: 38px; height: 38px;
            background: linear-gradient(135deg, var(--accent), #818cf8);
            border-radius: 10px; display: flex; align-items: center; justify-content: center;
            font-size: 18px; box-shadow: 0 0 24px var(--glow);
        }
        .sb-name { font-size: 17px; font-weight: 800; letter-spacing: -0.04em; }
        .sb-name em { font-style: normal; color: var(--accent2); }
        .sb-ver { font-family: var(--mono); font-size: 10px; color: var(--muted); letter-spacing: 0.08em; }

        .sb-nav { padding: 16px 12px; flex: 1; }
        .sb-group {
            font-family: var(--mono); font-size: 9px; color: var(--muted);
            letter-spacing: 0.14em; text-transform: uppercase;
            padding: 0 8px; margin: 16px 0 6px;
        }
        .sb-group:first-child { margin-top: 0; }
        .sb-item {
            display: flex; align-items: center; gap: 10px;
            padding: 9px 10px; border-radius: 9px;
            font-size: 13px; font-weight: 600; color: var(--muted2);
            cursor: pointer; transition: all 0.18s; margin-bottom: 2px;
            border: 1px solid transparent; text-decoration: none;
        }
        .sb-item:hover { background: var(--surface); color: var(--text); border-color: var(--border); }
        .sb-item.on { background: rgba(59,130,246,0.1); color: var(--accent2); border-color: rgba(59,130,246,0.22); }
        .sb-item .ico { font-size: 15px; width: 18px; text-align: center; flex-shrink: 0; }
        .sb-badge {
            margin-left: auto; font-family: var(--mono); font-size: 10px;
            background: var(--surf2); border: 1px solid var(--border2);
            border-radius: 5px; padding: 1px 6px; color: var(--muted2);
        }
        .sb-badge.green { color: var(--ok); border-color: rgba(16,185,129,0.3); background: rgba(16,185,129,0.06); }
        .sb-badge.blue  { color: var(--accent2); border-color: rgba(96,165,250,0.3); background: rgba(59,130,246,0.06); }

        .sb-footer { padding: 14px 20px; border-top: 1px solid var(--border); }
        .sb-status { display: flex; align-items: center; gap: 7px; font-family: var(--mono); font-size: 10px; color: var(--muted); margin-bottom: 4px; }
        .dot { width: 6px; height: 6px; border-radius: 50%; background: var(--ok); box-shadow: 0 0 6px var(--ok); animation: blink 2s infinite; flex-shrink: 0; }
        @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.25} }

        /* RIGHT */
        .right { display: flex; flex-direction: column; }
        .topbar {
            background: rgba(8,10,15,0.85); backdrop-filter: blur(14px);
            border-bottom: 1px solid var(--border);
            padding: 14px 28px; display: flex; align-items: center; justify-content: space-between;
            position: sticky; top: 0; z-index: 20;
        }
        .tb-title { font-size: 15px; font-weight: 700; }
        .tb-sub { font-size: 11px; color: var(--muted); font-family: var(--mono); margin-top: 1px; }
        .tb-clock { font-family: var(--mono); font-size: 12px; color: var(--muted2); background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 6px 12px; }

        /* MAIN */
        .main { padding: 28px 32px 60px; }

        /* TABS */
        .tabs { display: flex; gap: 3px; background: var(--surface); border: 1px solid var(--border); border-radius: 11px; padding: 3px; width: fit-content; margin-bottom: 28px; }
        .tab { padding: 7px 18px; border-radius: 8px; border: none; cursor: pointer; font-family: var(--sans); font-size: 13px; font-weight: 700; color: var(--muted2); background: transparent; transition: all 0.2s; }
        .tab.on { background: var(--accent); color: white; box-shadow: 0 4px 14px var(--glow); }
        .tab:hover:not(.on) { color: var(--text); }
        .panel { display: none; }
        .panel.on { display: block; }

        /* CARD */
        .card { background: var(--surface); border: 1px solid var(--border); border-radius: 18px; padding: 28px; margin-bottom: 20px; }
        .card-hd {
            font-family: var(--mono); font-size: 10px; font-weight: 600;
            color: var(--muted); text-transform: uppercase; letter-spacing: 0.12em;
            margin-bottom: 18px; display: flex; align-items: center; gap: 10px;
        }
        .card-hd::after { content:''; flex:1; height:1px; background: var(--border); }

        /* DROPZONE */
        .dropzone { border: 1.5px dashed var(--border2); border-radius: 14px; padding: 48px 28px; text-align: center; position: relative; cursor: pointer; transition: all 0.22s; background: var(--bg2); }
        .dropzone:hover, .dropzone.over { border-color: var(--accent); background: rgba(59,130,246,0.04); }
        .dropzone input { position: absolute; inset: 0; opacity: 0; cursor: pointer; width: 100%; height: 100%; }
        .dz-icon { width: 60px; height: 60px; border-radius: 16px; background: var(--surf2); border: 1px solid var(--border2); display: flex; align-items: center; justify-content: center; font-size: 26px; margin: 0 auto 16px; transition: all 0.3s; }
        .dropzone:hover .dz-icon, .dropzone.over .dz-icon { background: rgba(59,130,246,0.1); border-color: rgba(59,130,246,0.35); transform: translateY(-5px); box-shadow: 0 14px 28px var(--glow); }
        .dz-title { font-size: 17px; font-weight: 700; margin-bottom: 6px; }
        .dz-sub { font-size: 13px; color: var(--muted); margin-bottom: 14px; }
        .dz-pills { display: flex; justify-content: center; gap: 7px; flex-wrap: wrap; }
        .pill { font-family: var(--mono); font-size: 11px; font-weight: 500; border-radius: 6px; padding: 3px 9px; }
        .pill-xls { background: rgba(16,185,129,0.1); color: #10b981; border: 1px solid rgba(16,185,129,0.22); }
        .pill-dwg { background: rgba(59,130,246,0.1); color: #60a5fa; border: 1px solid rgba(59,130,246,0.22); }

        /* FILE QUEUE */
        .queue { margin-top: 14px; display: flex; flex-direction: column; gap: 7px; }
        .qrow { display: flex; align-items: center; gap: 10px; background: var(--bg2); border: 1px solid var(--border); border-radius: 9px; padding: 9px 13px; animation: fadein 0.2s ease; }
        @keyframes fadein { from{opacity:0;transform:translateY(-5px)} to{opacity:1;transform:none} }
        .qi { width: 30px; height: 30px; border-radius: 7px; display: flex; align-items: center; justify-content: center; font-size: 13px; flex-shrink: 0; }
        .qi-xls { background: rgba(16,185,129,0.1); }
        .qi-dwg { background: rgba(59,130,246,0.1); }
        .qname { flex: 1; min-width: 0; font-size: 13px; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .qext { font-family: var(--mono); font-size: 10px; padding: 2px 6px; border-radius: 4px; font-weight: 500; flex-shrink: 0; }
        .qsize { font-family: var(--mono); font-size: 11px; color: var(--muted); flex-shrink: 0; }

        /* BUTTON */
        .btn-go { width: 100%; margin-top: 18px; background: var(--accent); color: white; border: none; border-radius: 13px; padding: 15px 20px; font-family: var(--sans); font-size: 15px; font-weight: 700; cursor: pointer; transition: all 0.2s; position: relative; overflow: hidden; letter-spacing: -0.01em; }
        .btn-go::after { content:''; position:absolute; inset:0; background:linear-gradient(to bottom,rgba(255,255,255,0.07),transparent); }
        .btn-go:hover { background: #2563eb; transform: translateY(-2px); box-shadow: 0 14px 36px var(--glow); }
        .btn-go:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }

        /* PROGRESS */
        .prog { display: none; margin-top: 14px; }
        .prog.show { display: block; }
        .prog-track { height: 3px; background: var(--border); border-radius: 99px; overflow: hidden; }
        .prog-fill { height: 100%; border-radius: 99px; background: linear-gradient(90deg, var(--accent), #818cf8); animation: sweep 2s ease-in-out infinite; }
        @keyframes sweep { 0%{width:0%} 50%{width:70%} 100%{width:92%} }
        .prog-msg { margin-top: 8px; font-family: var(--mono); font-size: 11px; color: var(--muted); display: flex; align-items: center; gap: 6px; }
        .prog-dot { width: 5px; height: 5px; border-radius: 50%; background: var(--accent); animation: blink 1s infinite; }

        /* STATS */
        .stats3 { display: grid; grid-template-columns: repeat(3,1fr); gap: 12px; margin-bottom: 20px; }
        .scard { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 18px; text-align: center; }
        .scard-val { font-size: 38px; font-weight: 800; letter-spacing: -0.05em; line-height: 1; margin-bottom: 5px; }
        .scard-lbl { font-family: var(--mono); font-size: 11px; color: var(--muted); }
        .scard.t .scard-val { color: var(--accent2); }
        .scard.ok .scard-val { color: var(--ok); }
        .scard.er .scard-val { color: var(--err); }

        /* RESULT ROWS */
        .res-toolbar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
        .btn-zip { background: var(--surf2); border: 1px solid var(--border2); color: var(--text); border-radius: 9px; padding: 8px 15px; font-family: var(--sans); font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.2s; display: flex; align-items: center; gap: 6px; }
        .btn-zip:hover { border-color: var(--accent); color: var(--accent2); background: rgba(59,130,246,0.05); }
        .rrow { display: flex; align-items: flex-start; gap: 13px; background: var(--surface); border: 1px solid var(--border); border-radius: 13px; padding: 15px 17px; margin-bottom: 9px; transition: border-color 0.2s; }
        .rrow:hover { border-color: var(--border2); }
        .rrow.ok { border-left: 3px solid var(--ok); }
        .rrow.er { border-left: 3px solid var(--err); }
        .rico { font-size: 18px; flex-shrink: 0; padding-top: 2px; }
        .rbody { flex: 1; min-width: 0; }
        .rname { font-size: 14px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 3px; }
        .rmeta { font-family: var(--mono); font-size: 11px; color: var(--muted); }
        .rerr { margin-top: 8px; font-family: var(--mono); font-size: 11px; line-height: 1.6; color: #fb7185; background: rgba(244,63,94,0.06); border: 1px solid rgba(244,63,94,0.18); border-radius: 8px; padding: 8px 11px; word-break: break-word; }
        .rerr::before { content: '⚠  '; }
        .btn-dl { flex-shrink: 0; display: flex; align-items: center; gap: 5px; background: rgba(16,185,129,0.1); color: var(--ok); border: 1px solid rgba(16,185,129,0.22); border-radius: 9px; padding: 7px 13px; font-family: var(--sans); font-size: 13px; font-weight: 600; text-decoration: none; transition: all 0.2s; white-space: nowrap; }
        .btn-dl:hover { background: rgba(16,185,129,0.18); transform: translateY(-1px); }

        /* DASHBOARD */
        .dash-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-bottom: 18px; }
        .dc { background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 22px; }
        .dc.wide { grid-column: 1 / -1; }
        .dc-title { font-family: var(--mono); font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; color: var(--muted); margin-bottom: 14px; }
        .metric { font-size: 46px; font-weight: 800; letter-spacing: -0.05em; line-height: 1; }
        .metric-sub { font-size: 12px; color: var(--muted); margin-top: 6px; font-family: var(--mono); }
        .flist-row { display: flex; align-items: center; gap: 11px; padding: 10px 0; border-bottom: 1px solid var(--border); }
        .flist-row:last-child { border-bottom: none; padding-bottom: 0; }
        .flist-icon { width: 32px; height: 32px; background: rgba(59,130,246,0.09); border-radius: 7px; display: flex; align-items: center; justify-content: center; font-size: 13px; flex-shrink: 0; }
        .flist-name { flex: 1; min-width: 0; font-size: 13px; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .flist-sz { font-family: var(--mono); font-size: 11px; color: var(--muted); flex-shrink: 0; }
        .flist-dt { font-family: var(--mono); font-size: 10px; color: var(--muted); flex-shrink: 0; min-width: 120px; text-align: right; }
        .flist-dl { text-decoration: none; font-size: 14px; color: var(--muted); transition: color 0.2s; }
        .flist-dl:hover { color: var(--accent2); }
        .hist-row { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--border); }
        .hist-row:last-child { border-bottom: none; }
        .hist-ts { font-family: var(--mono); font-size: 11px; color: var(--muted2); min-width: 150px; }
        .hist-counts { display: flex; gap: 8px; font-family: var(--mono); font-size: 11px; }
        .hc-ok { color: var(--ok); } .hc-er { color: var(--err); }
        .no-files { text-align: center; padding: 36px; font-family: var(--mono); font-size: 12px; color: var(--muted); }

        @media (max-width: 860px) {
            .shell { grid-template-columns: 1fr; }
            .sidebar { display: none; }
            .main { padding: 16px; }
            .dash-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
<div class="shell">

<!-- SIDEBAR -->
<aside class="sidebar">
    <div class="sb-brand">
        <div class="sb-logo">
            <div class="sb-icon">📄</div>
            <div>
                <div class="sb-name">Doc<em>Convert</em></div>
            </div>
        </div>
        <div class="sb-ver">v3.0 · PT. Kayumebel Indonesia</div>
    </div>
    <nav class="sb-nav">
        <div class="sb-group">Menu Utama</div>
        <a href="#" class="sb-item on" id="sb-convert" onclick="switchTab('convert');return false;"><span class="ico">🚀</span> Konversi</a>
        <a href="#" class="sb-item" id="sb-dashboard" onclick="switchTab('dashboard');return false;"><span class="ico">📊</span> Dashboard <span class="sb-badge" id="sbCount">{{ output_files|length }}</span></a>

        <div class="sb-group">Format Didukung</div>
        <div class="sb-item" style="cursor:default"><span class="ico">📗</span> Excel XLS / XLSX <span class="sb-badge green">iLovePDF</span></div>
        <div class="sb-item" style="cursor:default"><span class="ico">📐</span> AutoCAD DWG <span class="sb-badge blue">ConvertAPI</span></div>

        <div class="sb-group">Status API</div>
        <div class="sb-item" style="cursor:default;font-family:var(--mono);font-size:12px;"><span class="ico">💙</span> iLovePDF API <span class="sb-badge green">● Online</span></div>
        <div class="sb-item" style="cursor:default;font-family:var(--mono);font-size:12px;"><span class="ico">⚙️</span> ConvertAPI <span class="sb-badge green">● Online</span></div>
    </nav>
    <div class="sb-footer">
        <div class="sb-status"><div class="dot"></div> All systems operational</div>
        <div style="font-family:var(--mono);font-size:10px;color:var(--muted)">Max upload: 200 MB per file</div>
    </div>
</aside>

<!-- RIGHT -->
<div class="right">
    <div class="topbar">
        <div>
            <div class="tb-title" id="tbTitle">Konversi Dokumen</div>
            <div class="tb-sub">Excel & CAD → PDF beresolusi tinggi</div>
        </div>
        <div class="tb-clock" id="clock">—</div>
    </div>

    <div class="main">
        <div class="tabs">
            <button class="tab on" id="tab-convert" onclick="switchTab('convert')">🚀 Konversi</button>
            <button class="tab" id="tab-dashboard" onclick="switchTab('dashboard')">📊 Dashboard</button>
        </div>

        <!-- PANEL: CONVERT -->
        <div class="panel on" id="panel-convert">
            <div class="card">
                <div class="card-hd">Upload & Konversi File</div>
                <form action="/process" method="POST" enctype="multipart/form-data" id="uploadForm">
                    <div class="dropzone" id="dz">
                        <input type="file" name="files[]" multiple accept=".xls,.xlsx,.dwg" id="fileInput" required>
                        <div class="dz-icon">📂</div>
                        <div class="dz-title">Seret file ke sini</div>
                        <div class="dz-sub">atau klik untuk memilih</div>
                        <div class="dz-pills">
                            <span class="pill pill-xls">.XLS</span>
                            <span class="pill pill-xls">.XLSX</span>
                            <span class="pill pill-dwg">.DWG</span>
                        </div>
                    </div>
                    <div class="queue" id="queue"></div>
                    <button type="submit" class="btn-go" id="btnGo">🚀 &nbsp;Mulai Konversi</button>
                </form>
                <div class="prog" id="prog">
                    <div class="prog-track"><div class="prog-fill"></div></div>
                    <div class="prog-msg"><div class="prog-dot"></div><span id="progMsg">Mengirim ke server...</span></div>
                </div>
            </div>

            {% if results %}
            {% set sc = results | selectattr('status','equalto','success') | list | length %}
            {% set fc = results | selectattr('status','equalto','failed')  | list | length %}
            {% set sf = results | selectattr('status','equalto','success') | map(attribute='output_file') | list %}

            <div class="stats3">
                <div class="scard t"><div class="scard-val">{{ results|length }}</div><div class="scard-lbl">total</div></div>
                <div class="scard ok"><div class="scard-val">{{ sc }}</div><div class="scard-lbl">berhasil</div></div>
                <div class="scard er"><div class="scard-val">{{ fc }}</div><div class="scard-lbl">gagal</div></div>
            </div>

            <div class="res-toolbar">
                <div class="card-hd" style="margin:0;flex:1">Hasil Konversi</div>
                {% if sf|length > 1 %}
                <form action="/download_zip" method="POST" style="margin:0">
                    <input type="hidden" name="filenames" value="{{ sf|join(',') }}">
                    <button type="submit" class="btn-zip">📦 Download Semua .ZIP</button>
                </form>
                {% endif %}
            </div>

            {% for res in results %}
            <div class="rrow {{ 'ok' if res.status=='success' else 'er' }}">
                <div class="rico">{{ '✅' if res.status=='success' else '❌' }}</div>
                <div class="rbody">
                    <div class="rname">{{ res.filename }}</div>
                    <div class="rmeta">
                        {% if res.filename.lower().endswith(('.xls','.xlsx')) %}Excel → PDF via iLovePDF{% else %}DWG → PDF via ConvertAPI{% endif %}
                        {% if res.size_kb %} · {{ res.size_kb }} KB{% endif %}
                    </div>
                    {% if res.status=='failed' and res.error %}
                    <div class="rerr">{{ res.error }}</div>
                    {% endif %}
                </div>
                {% if res.status=='success' %}
                <a href="/download/{{ res.output_file }}" class="btn-dl">↓ Unduh</a>
                {% endif %}
            </div>
            {% endfor %}
            {% endif %}
        </div>

        <!-- PANEL: DASHBOARD -->
        <div class="panel" id="panel-dashboard">
            <div class="dash-grid">
                <div class="dc">
                    <div class="dc-title">Total File PDF</div>
                    <div class="metric">{{ output_files|length }}</div>
                    <div class="metric-sub">tersimpan di pdf_result/</div>
                </div>
                <div class="dc">
                    <div class="dc-title">Total Ukuran</div>
                    <div class="metric">{{ ((output_files|sum(attribute='size_kb'))/1024)|round(1) }} <span style="font-size:22px;color:var(--muted)">MB</span></div>
                    <div class="metric-sub">kapasitas terpakai</div>
                </div>

                <div class="dc wide">
                    <div class="dc-title">File PDF Tersimpan ({{ output_files|length }})</div>
                    {% if output_files %}
                    {% for f in output_files %}
                    <div class="flist-row">
                        <div class="flist-icon">📄</div>
                        <div class="flist-name">{{ f.name }}</div>
                        <div class="flist-sz">{{ f.size_kb }} KB</div>
                        <div class="flist-dt">{{ f.modified }}</div>
                        <a href="/download/{{ f.name }}" class="flist-dl" title="Download">↓</a>
                    </div>
                    {% endfor %}
                    {% else %}
                    <div class="no-files">📭 Belum ada file PDF. Lakukan konversi terlebih dahulu.</div>
                    {% endif %}
                </div>

                <div class="dc wide">
                    <div class="dc-title">Riwayat Konversi ({{ history_data|length }} batch)</div>
                    {% if history_data %}
                    {% for h in history_data[:15] %}
                    <div class="hist-row">
                        <div class="hist-ts">{{ h.timestamp }}</div>
                        <div style="flex:1;font-size:13px;font-weight:600;">{{ h.total }} file diproses</div>
                        <div class="hist-counts">
                            <span class="hc-ok">✅ {{ h.success }} berhasil</span>
                            <span class="hc-er">❌ {{ h.failed }} gagal</span>
                        </div>
                    </div>
                    {% endfor %}
                    {% else %}
                    <div class="no-files">Belum ada riwayat konversi.</div>
                    {% endif %}
                </div>
            </div>
        </div>

    </div>
</div>
</div>

<script>
(function tick(){
    const n = new Date();
    document.getElementById('clock').textContent = n.toLocaleTimeString('id-ID',{hour:'2-digit',minute:'2-digit',second:'2-digit'});
    setTimeout(tick,1000);
})();

const titles = { convert:'Konversi Dokumen', dashboard:'Dashboard & Riwayat' };
function switchTab(name) {
    document.querySelectorAll('.panel').forEach(p=>p.classList.remove('on'));
    document.querySelectorAll('.tab').forEach(b=>b.classList.remove('on'));
    document.querySelectorAll('.sb-item[id]').forEach(i=>i.classList.remove('on'));
    document.getElementById('panel-'+name).classList.add('on');
    document.getElementById('tab-'+name).classList.add('on');
    const sb = document.getElementById('sb-'+name);
    if(sb) sb.classList.add('on');
    document.getElementById('tbTitle').textContent = titles[name]||name;
}

const fileInput=document.getElementById('fileInput'), queue=document.getElementById('queue'),
      dz=document.getElementById('dz'), form=document.getElementById('uploadForm'),
      btnGo=document.getElementById('btnGo'), prog=document.getElementById('prog'),
      progMsg=document.getElementById('progMsg');

function fmtBytes(b){ return b<1024?b+' B':b<1048576?(b/1024).toFixed(1)+' KB':(b/1048576).toFixed(1)+' MB'; }
function typeOf(name){
    const ext=name.split('.').pop().toLowerCase();
    if(['xls','xlsx'].includes(ext)) return {cls:'qi-xls',ico:'📗',col:'#10b981',lbl:ext.toUpperCase()};
    if(ext==='dwg') return {cls:'qi-dwg',ico:'📐',col:'#60a5fa',lbl:'DWG'};
    return {cls:'',ico:'📄',col:'#64748b',lbl:ext.toUpperCase()};
}
function renderQueue(files){
    queue.innerHTML='';
    Array.from(files).forEach(f=>{
        const t=typeOf(f.name), row=document.createElement('div');
        row.className='qrow';
        row.innerHTML=`<div class="qi ${t.cls}">${t.ico}</div><div class="qname">${f.name}</div><span class="qext" style="background:${t.col}18;color:${t.col};border:1px solid ${t.col}28">${t.lbl}</span><div class="qsize">${fmtBytes(f.size)}</div>`;
        queue.appendChild(row);
    });
}
fileInput.addEventListener('change',function(){ if(this.files.length) renderQueue(this.files); else queue.innerHTML=''; });
dz.addEventListener('dragover',e=>{e.preventDefault();dz.classList.add('over');});
dz.addEventListener('dragleave',()=>dz.classList.remove('over'));
dz.addEventListener('drop',e=>{dz.classList.remove('over');if(e.dataTransfer.files.length) renderQueue(e.dataTransfer.files);});

const steps=['Mengautentikasi ke iLovePDF...','Mengunggah file ke server...','Memproses konversi...','Mengunduh hasil PDF...','Hampir selesai...'];
let si=0,timer;
form.addEventListener('submit',function(){
    btnGo.disabled=true; btnGo.textContent='⏳  Memproses...';
    prog.classList.add('show'); si=0; progMsg.textContent=steps[0];
    timer=setInterval(()=>{si=Math.min(si+1,steps.length-1);progMsg.textContent=steps[si];},3500);
});
{% if results %}
window.addEventListener('load',()=>{document.querySelector('.stats3')?.scrollIntoView({behavior:'smooth',block:'start'});});
{% endif %}
</script>
</body>
</html>"""


# ==========================================
# ROUTING
# ==========================================
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, results=None, output_files=get_output_files(), history_data=load_history())


@app.route('/process', methods=['POST'])
def process_files():
    uploaded_files = request.files.getlist("files[]")
    results = []

    ilovepdf_token = None
    token_error = None
    has_excel = any(f.filename.lower().endswith(('.xls', '.xlsx')) for f in uploaded_files if f)
    if has_excel:
        ilovepdf_token, token_error = get_ilovepdf_token()

    for file in uploaded_files:
        if not file or file.filename == '':
            continue

        original_name = file.filename
        safe_name = secure_filename(original_name)
        if not safe_name:
            safe_name = f"file_{len(results)}.tmp"

        file_path = os.path.join(app.config['INPUT_FOLDER'], safe_name)
        file.save(file_path)

        base_name = safe_name.rsplit('.', 1)[0]
        ext = safe_name.split('.')[-1].lower()
        output_filename = f"{base_name}_{ext}.pdf"

        status = False
        error_msg = None
        size_kb = None

        if ext in ['xls', 'xlsx']:
            if ilovepdf_token:
                status, error_msg = convert_excel_ilovepdf(file_path, safe_name, output_filename, ilovepdf_token)
            else:
                error_msg = token_error or "Tidak bisa mendapatkan token iLovePDF"
        elif ext == 'dwg':
            status, error_msg = convert_dwg_convertapi(file_path, output_filename)
        else:
            error_msg = f"Format '.{ext}' tidak didukung"

        if status:
            out_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
            if os.path.exists(out_path):
                size_kb = os.path.getsize(out_path) // 1024

        results.append({
            'filename': original_name,
            'output_file': output_filename,
            'status': 'success' if status else 'failed',
            'error': error_msg,
            'size_kb': size_kb,
        })

    save_history({
        'timestamp': datetime.now().strftime('%d %b %Y, %H:%M:%S'),
        'total': len(results),
        'success': sum(1 for r in results if r['status'] == 'success'),
        'failed': sum(1 for r in results if r['status'] == 'failed'),
        'files': [{'name': r['filename'], 'status': r['status']} for r in results]
    })

    return render_template_string(HTML_TEMPLATE, results=results, output_files=get_output_files(), history_data=load_history())


@app.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)


@app.route('/download_zip', methods=['POST'])
def download_zip():
    filenames_str = request.form.get('filenames', '')
    if not filenames_str:
        return "Tidak ada file.", 400
    filenames = [f.strip() for f in filenames_str.split(',') if f.strip()]
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for fn in filenames:
            fp = os.path.join(app.config['OUTPUT_FOLDER'], fn)
            if os.path.exists(fp):
                zf.write(fp, arcname=fn)
    memory_file.seek(0)
    return send_file(memory_file, download_name='Hasil_Konversi_Dokumen.zip', as_attachment=True, mimetype='application/zip')


@app.route('/api/files')
def api_files():
    return jsonify(get_output_files())


@app.route('/api/history')
def api_history():
    return jsonify(load_history())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)
