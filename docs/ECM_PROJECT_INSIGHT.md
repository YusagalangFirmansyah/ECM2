# ECM/ECR Project — Comprehensive Insight Document
## Untuk Sharing Antar AI (Hermes ↔ Claude)
**Company:** PT. Kayu Mebel Indonesia (KMI)
**Developer:** Arya Prayogi Utama (ABAP Developer)
**System:** SAP S/4HANA 1809, SAP_BASIS 753 SP03
**BSP App:** ZBSP_ECM_APP
**Last Updated:** 04 Juli 2026

---

## 1. PROJECT OVERVIEW

### Apa itu ECM?
ECM (Engineering Change Management) adalah aplikasi BSP di SAP untuk mengelola **permintaan perubahan engineering** di perusahaan manufaktur furnitur. Aplikasi ini mengelola siklus hidup dari **ECR** (Engineering Change Request) hingga **ECO** (Engineering Change Order) dan finalisasi.

### Bisnis Context
- KMI bergerak di bidang **wood working / furnitur**
- Ada 3 divisi: **Wood** (DRW), **Box** (DBX), **Metal** (DMT)
- Ditambah **TDS** (Technical Data Sheet) untuk material HALB
- ECR diajukan oleh drafter, di-approve oleh admin, di-review oleh approver
- Setelah ECR di-approve, drafter membuat ECO (upload dokumen DMS: drawing, BOM, assembly instruction)

### Teknologi
- **Frontend:** SAP BSP (Pages with Flow Logic, .htm files)
- **Backend:** ABAP (event handler di OnInit, OnInputProcessing)
- **Styling:** Tailwind CSS + Chart.js + SweetAlert2 + Font Awesome
- **Database:** Z-tables (ZECM_REQ, ZECM_USER, ZECM_LOG)
- **DMS:** SAP Document Management System (DRAW, DRAD, DRAP)
- **Auth:** Server-side cookie (CL_BSP_SERVER_SIDE_COOKIE)

---

## 2. STATUS FLOW

### ECR/ECO Status Flow (di aplikasi BSP)
```
CRTD (Draft/ECR) ──→ INWK (In Work/ECO) ──→ INSP (Inspection) ──→ CLSD (Closed)
     ↑ drafter buat       ↑ admin approve       ↑ drafter submit      ↑ approver approve
                         ↓ admin reject         ↓ approver revisi
                         REJC                   INWK (kembali)
```

| Status | Label (Card) | Warna | Arti |
|--------|-------------|-------|------|
| CRTD | ECR | 🔵 #3B82F6 | ECR baru diajukan drafter, nunggu admin approve |
| INWK | ECO | 🟠 #F59E0B | Sudah di-approve admin, drafter kerjakan + upload DMS |
| INSP | On Inspection | 🟡 #EAB308 | Drafter selesai, tunggu approver review |
| CLSD | Closed | 🟢 #22C55E | Disetujui approver, selesai |
| REJC | Rejected (ditolak) | 🔴 #EF4444 | Ditolak oleh admin (dari CRTD) atau approver (dari INSP) |

### DMS Status Flow (di SAP DMS)
```
IA (In Work) ──→ AP (Inspection Required) ──→ FR (Released)
      ↑                                            ↓
      └──── revisi ←── ZG (Rejected) ←── reject
```

| DMS Status | Arti |
|-----------|------|
| AA | Created (baru dibuat) |
| IA | In Work (drafter sedang isi/checkin file) |
| AP | Inspection Required (submit ke approver) |
| FR | Released (approved, dokumen aktif) |
| ZG | Rejected (ditolak) |
| H4 | Obsolete (versi lama, sudah digantikan versi baru) |

---

## 3. ROLES & PAGES

### Roles
| Role | Halaman Utama | Fungsi |
|------|--------------|--------|
| **DRAFTER** | drafter_list.htm | Buat ECR, kerjakan ECO, submit ke inspection, upload DMS |
| **ADMIN** | admin_dashboard.htm | Dashboard monitoring, approve/reject ECR (CRTD→INWK) |
| **APPROVER** | approver_dashboard.htm | Dashboard, approve/reject ECR di INSP, approve DMS (AP→FR) |
| **OTHERS** | dashboard.htm | Superadmin (existing) |

### Pages Structure (BSP)
```
Tab Layout          → HTML + CSS + JavaScript (Tailwind, Chart.js, SweetAlert2)
Tab Page Attributes → DATA: variabel global (GV_*, LT_*, LS_*)
Tab Type Definitions → TYPES: internal table
Tab Event Handler:
  ├── OnInitialization  → Cookie check, routing, data query (SELECT)
  └── OnInputProcessing → Form submit, logout, actions
```

### Key BSP Files per Role
| Role | Files |
|------|-------|
| Admin | admin_dashboard.htm, admin_dashboard_oninit.txt, admin_dashboard_event_handler.txt, admin_dashboard_page_attributes.txt, admin_dashboard_type_definitions.txt |
| Drafter | drafter_list.htm, drafter_list_oninit.txt, drafter_list_event_handler.txt, drafter_list_page_attributes.txt, drafter_list_type_definitions.txt |
| Approver | approver_list.htm, approver_list_oninit.txt, approver_list_event_handler.txt, approver_list_page_attributes.txt, approver_list_type_definitions.txt |
| DMS | dms_list.htm, dms_detail.htm, dms_detail_download.htm |
| ECR Form | ecr_form.htm (modal popup, bukan navigate) |
| Headers | admin_header.htm, app_header.htm (detect role, conditional nav) |
| Login | login.htm, login_event_handler.txt |

---

## 4. DATABASE TABLES

### ZECM_REQ (ECR/ECO Requests)
| Field | Type | Keterangan |
|-------|------|------------|
| ECR_NO | NUMC 10 | Primary key (SNRO: ZECM_REQ) |
| TITLE | CHAR 100 | Judul perubahan |
| DOKAR | CHAR 3 | Document type (DRW/DBX/DMT) |
| STATUS | CHAR 5 | CRTD/INWK/INSP/CLSD/REJC |
| DESCR | CHAR ... | Deskripsi perubahan |
| PRIORITY | CHAR 10 | CRITICAL/HIGH/MEDIUM/LOW |
| COST_ESTIMATE | CURR 15 | Estimasi biaya (opsional) |
| ZDEPT | CHAR 30 | Departemen (PROD/QC/SALES/DRAFT) |
| ZREASON | CHAR 50 | Alasan (DEFECT/COST/DESIGN/BUYER/STANDARD) |
| REJECT_REASON | CHAR 255 | Alasan penolakan (free text) |
| REJECTED_BY | CHAR 12 | User yang reject |
| DIR_NUMBER | CHAR 40 | DMS document number |
| KATEGORI | CHAR 3 | DRW/DBX/DMT |
| MATNR_FG | CHAR 18 | Material number (Finish Goods) |
| CREATED_BY | CHAR 12 | Creator |
| CREATED_DATE | DATS | Creation date |
| CREATED_TIME | TIMS | Creation time |

### ZECM_USER (User Management)
| Field | Type | Keterangan |
|-------|------|------------|
| ZECM_USER_ID | NUMC | Primary key (auto increment) |
| ZECM_FULL_NAME | CHAR | Nama lengkap |
| ZECM_PWD_HASH | CHAR | Password (plain text, despite name) |
| ZECM_ROLE | CHAR | ADMIN/APPROVER/DRAFTER/OTHERS |
| ZECM_ACTIVE | CHAR | X = aktif |
| ZECM_LAST_LOGIN | TIMESTAMP | Login terakhir |

### ZECM_LOG (Audit Trail)
| Field | Type | Keterangan |
|-------|------|------------|
| LOG_ID | NUMC | Primary key (auto increment) |
| ECR_NO | NUMC 10 | ECR number |
| ACTION | CHAR | Action type |
| OLD_STATUS | CHAR 5 | Status sebelum |
| NEW_STATUS | CHAR 5 | Status sesudah |
| USER_ID | CHAR 12 | Pelaku |
| ACTION_DATE | DATS | Tanggal |
| ACTION_TIME | TIMS | Jam |
| REASON | CHAR 255 | Alasan |

---

## 5. APPROVAL FLOW (3 PROSES)

### Proses 1: ECR Approval (BSP App)
```
Drafter buat ECR → status CRTD
    ↓
Admin approve → CRTD → INWK (ECO aktif)
    ↓ Admin reject → REJC + reason
Drafter kerjakan ECO (upload DMS)
    ↓
Drafter submit → INWK → INSP
    ↓
Approver approve → INSP → CLSD
    ↓ Approver revisi → INSP → INWK (kembali ke drafter)
    ↓ Approver reject → REJC + reason
```

### Proses 2: DMS File Approval (BSP + BAPI)
```
Drafter checkin file ke DMS → status IA
    ↓
Drafter submit → IA → AP (via BAPI_DOCUMENT_CHANGE2, statusintern)
    ↓
Approver approve → AP → FR (released, via BAPI_DOCUMENT_CHANGE2, statusintern)
    ↓ Approver revisi → AP → ZG → IA (2-step, kembali ke drafter)
    ↓ Approver reject → AP → ZG (rejected)
```

### Proses 3: DMS Version Obsoleting
```
Setelah versi baru FR → versi lama FR → H4 (obsolete)
(via BAPI_DOCUMENT_CHANGE2, statusextern)
```

### Logging
Setiap perubahan status ECR di-log ke **ZECM_LOG** (audit trail).

---

## 6. DMS INTEGRATION

### DMS Document Types
| DOKAR | Divisi | File Types | Format |
|-------|--------|------------|--------|
| DRW | Wood | Drawing (.DRW), BOM (.BOM) | PDF |
| DMT | Metal | Drawing (.DRW), BOM (.BOM) | PDF |
| DBX | Box | Drawing (.DRW), BOM (.BOM), Assembly Instruction (.ASM, .ASM2, ...) | PDF |
| TDS | Technical | Technical Data Sheet (.TDS) | XLSX (as-is) |

### DMS BSP Pages
| Page | Fungsi |
|------|--------|
| dms_list.htm | List semua dokumen DMS (filter by status, pagination) |
| dms_detail.htm | Detail dokumen + status log + file originals |
| dms_detail_download.htm | Download file dari DMS |

### Key BAPIs untuk DMS
| BAPI | Fungsi |
|------|--------|
| BAPI_DOCUMENT_CHANGE2 | Ubah status DMS (IA→AP, AP→FR, AP→ZG, dll) |
| BAPI_DOCUMENT_GETDETAIL2 | Ambil detail dokumen DMS |
| CVAPI_DOC_GETDETAIL | Ambil file originals (lo_objid, ph_objid untuk replace) |
| BAPI_TRANSACTION_COMMIT | Commit transaksi (WAJIB setelah BAPI) |

### DMS Detection Pattern (Penting!)
- **JANGAN** filter DMS by `dokar` dari ZECM_REQ (bisa salah)
- **GUNAKAN** pattern: loop DRAW + check DRAD object link + ALPHA_OUTPUT compare
- Material number comparison WAJIB pakai CONVERSION_EXIT_ALPHA_OUTPUT

### DMS Approval Flow (BSP Reference)
- **zdms_list.htm** → List dokumen pending approval (status ≠ FR dan ≠ kosong)
- **zdms_detail.htm** → Detail + approve/reject/revisi buttons
- **Approve**: AP → FR (via statusintern)
- **Revisi**: AP → ZG → IA (2-step, via statusintern)
- **Reject**: AP → ZG (via statusintern)
- **Otorisasi**: hardcode sy-uname (KMI-U057, AUTO_EMAIL)

---

## 7. ZUPLOAD_CS_AUTO — AUTO DMS UPLOAD PROGRAM

### Overview
Program ABAP **ZUPLOAD_CS_AUTO** (v36) untuk **auto upload file ke SAP DMS Content Server** dan **auto-linking ke BOM material**. Berjalan sebagai background job (AL11 path).

### Bagaimana Cara Kerjanya
1. **Scan folder** di AL11 path (default: `/mnt/sap_media/engineering`)
2. **Parse nama file** → deteksi DOKAR (DRW/DBX/DMT/TDS), MATNR (opsional), description, content code
3. **Lookup dokumen** di DMS berdasarkan MATNR + DOKAR (via DRAD object link ke MARA)
4. **Jika dokumen ada + status IA** → REPLACE file original
5. **Jika dokumen ada + status FR** → Naik versi baru (FR→ZG, buat AA→IA, checkin file, restore ZG→IA→AP→FR)
6. **Jika dokumen tidak ada** → buat dokumen baru (AA→IA, checkin, IA→AP→FR)
7. **Link BOM**: cari semua komponen BOM (recursive, max level) → link sebagai object links
8. **Error handling**: file gagal dipindah ke subfolder `/error/` dengan suffix timestamp

### Format Nama File
```
FORMAT LAMA (backward compatible):
  [DOKAR]_[DESCRIPTION].[CONTENT_CODE].pdf
  Contoh: DRW_Cabinet Base Unit.DRW.pdf

FORMAT BARU (MATNR eksplisit, lebih akurat):
  [DOKAR]_[MATNR]_[DESCRIPTION].[CONTENT_CODE].pdf
  Contoh: DRW_19804726_PALAIS 4D LIGHT R24053.DRW.pdf

FORMAT TDS (selalu format baru):
  TDS_[MATNR]_[DESCRIPTION].TDS.xlsx
  Contoh: TDS_H8317XCG001_SHAPED LEG CONSOLE 309 PTG.TDS.xlsx
```

### Content Codes
| Code | Arti | Format |
|------|------|--------|
| .DRW | Drawing produk | PDF |
| .BOM | Bill of Material | PDF |
| .ASM | Assembly Instruction (DBX) | PDF |
| .ASM2, .ASM3, ... | Assembly ke-2, ke-3 | PDF |
| .TDS | Technical Data Sheet | XLSX (as-is) |

### Selection Screen Parameters
| Parameter | Default | Fungsi |
|-----------|---------|--------|
| p_dir | /mnt/sap_media/engineering | Folder AL11 |
| p_doktl | 000 | Document Part |
| p_stcat | ZDMS | Storage Category |
| p_werks | 2000 | Plant BOM 1 |
| p_wer2 | (kosong) | Plant BOM 2 (opsional) |
| p_stlan | 1 | BOM Usage |
| p_maxlv | 25 | Maks level BOM recursion |
| p_test | (unchecked) | Test mode / simulasi |

### Key Algorithm: File Parsing (parse_filename)
1. Validasi ekstensi (.pdf / .xlsx / .xls)
2. Deteksi DOKAR dari prefix (DRW_ / DBX_ / DMT_ / TDS_)
3. Deteksi MATNR opsional (format baru): token setelah prefix → validasi ke MARA (5 metode lookup)
4. Deteksi Content Code (.DRW / .BOM / .ASM / .TDS)
5. Backward compatibility: *_XLS → .BOM, lainnya → .DRW
6. Sisa = Description (as-is, case sensitive)

### Key Algorithm: BOM Linking
1. Cari BOM header (MAST → STKO)
2. Recursive collect semua komponen BOM (STPO → IDNRK) sampai max level
3. Link sebagai object links: STKO_DOC (BOM header) + MARA (setiap komponen)

### Key Algorithm: Replace vs Add
- Baca existing files via CVAPI_DOC_GETDETAIL → PT_FILES
- Match nama file (case insensitive)
- Jika match → set lo_objid + ph_objid → REPLACE (hanya file target, lainnya aman)
- Jika tidak match → INSERT sebagai original baru

### Key Algorithm: Naik Versi dari FR
```
1. Versi lama: FR → ZG (unlock)
2. Buat versi baru: AA → IA (checkin file)
3. Setelah checkin berhasil: versi lama ZG → IA → AP → FR (restore)
```

### Version History (penting)
| Versi | Perubahan Kritis |
|-------|-----------------|
| v27 | Fix replace: lo_objid+ph_objid dari CVAPI_DOC_GETDETAIL |
| v28 | Restore versi lama ke FR + error folder |
| v29 | Fix MAKT case sensitivity (jangan uppercase) |
| v30 | Strict: MATNR tidak ditemukan → file DITOLAK |
| v31 | Fix restore: ZG→IA→AP→FR (bukan ZG→FR langsung) |
| v32 | Fix find_best_document: IA priority=1 (bukan FR) |
| v33 | Format baru: MATNR opsional di nama file |
| v33a | Fix deteksi MATNR: validasi langsung ke MARA |
| v33b | 5 metode lookup MARA + fallback ke MAKT |
| v34 | Tambahan plant kedua (p_wer2) |
| v35 | Tambah TDS (Technical Data Sheet, .xlsx) |
| v36 | Rename SSC → TDS |

---

## 8. CURRENT STATE (V05_i — 03 Juli 2026)

### Subversi Aktif: v05_i (61 files)
**Fitur terakhir:**
- Date range filter di semua dashboard (admin, approver, drafter)
- CLSD removed dari summary cards + charts
- Shortcut buttons (1/2/6 Bulan)
- Chart layout fix
- Label rename: ECR Aktif→ECR, Dalam Proses→ECO, Inspection→On Inspection, Ditolak→Rejected
- Date format fix (YYYY-MM-DD → YYYYMMDD)

### Development Progress
| Versi | Tanggal | Status | Fitur Utama |
|-------|---------|--------|-------------|
| v05_a | 30 Jun | 📦 | Dashboard admin + drafter list + ECR form modal |
| v05_b | 30 Jun | 📦 | Fix reject/approve + DMS query |
| v05_c | 01 Jul | 📦 | PRG fix + reject button + status colors |
| v05_d | 01 Jul | 📦 | Drafter sync + reject with reason |
| v05_e | 02 Jul | 📦 | Drafter dashboard + DMS fix |
| v05_f | 02 Jul | 📦 | Approver dashboard + Chart.js |
| v05_g | 02 Jul | 📦 | DMS revisi flow fix (2-step) |
| v05_h | 02 Jul | 📦 | FERT label fix + spec doc |
| v05_i | 03 Jul | ✅ | Date range filter + cleanup |

### File Location di Server
```
/mnt/data/files/sap-docs/ecm/
├── bsp-ecm-app/
│   ├── V01/ ~ V04/ (backup)
│   ├── V05/
│   │   ├── v05_a/ ~ v05_i/ (full copies)
│   │   ├── CHANGELOG.md (detail per subversi)
│   │   └── v05_master_plan.md
│   └── PROGRAM DMS/
│       └── ZUPLOAD_CS_AUTO.txt (v36)
├── (Referensi) DMS Approval/
├── (Referensi) Pencarian Material/
├── ARCHITECTURE.md
├── CHANGELOG.md (summary semua versi)
├── VERSIONS.md
├── README2.md
└── subversion-notes.md
```

---

## 9. PITFALLS & LESSONS LEARNED

### BSP Pitfalls
1. `*` comment di Event Handler → WAJIB pakai `"` (double quote)
2. SELECT WAJIB pakai koma (New Open SQL) + `@` di host variable
3. DATA declarations TOP LEVEL ONLY (bukan di dalam IF/CASE)
4. Layout hanya HTML + `<%= %>` (tidak ada navigation-> atau logic ABAP)
5. SweetAlert di modal → WAJIB pakai `target: document.getElementById('modalId')`
6. Date format: input HTML `YYYY-MM-DD` → strip dashes → `YYYYMMDD` sebelum assign ke TYPE d
7. `REJECT_REASON` ≠ `ZREASON` — beda fungsi, jangan diganti
8. COLLECT tidak bisa untuk non-numeric → pakai manual READ TABLE loop
9. CONCATENATE integer → convert ke string dulu
10. DRAW query → jangan JOIN drat (causes SPRAS error), pakai draw langsung

### DMS Pitfalls
1. DMS detection: JANGAN filter by `dokar` dari ZECM_REQ — gunakan `dokar IN (DRW,DBX,DMT)` + DRAD object link
2. Material number comparison: WAJIB pakai CONVERSION_EXIT_ALPHA_OUTPUT
3. DMS revisi: AP → ZG → IA (2-step, bukan AP → IA langsung)
4. DMS restore dari ZG: ZG → IA → AP → FR (bukan ZG → FR langsung)
5. File replace: WAJIB pakai lo_objid + ph_objid dari CVAPI_DOC_GETDETAIL
6. Case sensitivity: MAKT description case-sensitive (jangan uppercase)
7. MATNR lookup: 5 metode (as-is, ALPHA_INPUT, -→/ as-is, -→/+ ALPHA_INPUT, fallback MAKT)

### General Pitfalls
1. FOR ALL ENTRIES → WAJIB cek table tidak kosong
2. FOR ALL ENTRIES → WAJIB pakai dict types (TYPE matnr, BUKAN TYPE c LENGTH 18)
3. Performance: FOR ALL ENTRIES bulk SELECT + READ TABLE (210s→30s untuk 483 records)
4. VBUP empty → gunakan LIKP-WBSTK
5. COND# fails in HTML
6. Date input: strip separators + rearrange DDMMYYYY → YYYYMMDD

### Troubleshooting Method
1. **Lihat versi sebelumnya** — ambil dari subversi yang terakhir JALAN
2. **Revert ke versi bersih** → buat perubahan kecil → test → lanjut
3. **Jangan pernah rewrite besar-besaran** — minimal edit
4. **SweetAlert2 built-in `input: 'textarea'`** lebih aman dari custom HTML

---

## 10. VARIABLE NAMING CONVENTION

**ALL CAPS** — konsisten sejak V03:
- `GV_*` → Global Variable (Page Attributes)
- `LV_*` → Local Variable
- `LS_*` → Local Structure
- `LT_*` → Local Table
- `LR_*` → Local Range

---

## 11. FM/BAPI YANG DIGUNAKAN

| FM/BAPI | Fungsi |
|---------|--------|
| BAPI_DOCUMENT_CHANGE2 | Ubah DMS status (IA→AP, AP→FR, dll) |
| BAPI_DOCUMENT_GETDETAIL2 | Ambil detail dokumen DMS |
| BAPI_TRANSACTION_COMMIT | Commit transaksi (WAJIB wait = 'X') |
| BAPI_TRANSACTION_ROLLBACK | Rollback transaksi (on error) |
| CVAPI_DOC_GETDETAIL | Ambil file originals (untuk replace mechanism) |
| NUMBER_GET_NEXT | Generate ZECM_LOG ID |
| CONVERSION_EXIT_ALPHA_INPUT | Tambah leading zero |
| CONVERSION_EXIT_ALPHA_OUTPUT | Hapus leading zero |
| CL_BSP_SERVER_SIDE_COOKIE | Auth cookie management |

---

---

## 12. LOGIN & AUTHENTICATION

### Login Flow
```
User buka login.htm → isi user_id + password
    ↓
OnInputProcessing: SELECT FROM zecm_user WHERE user_id = ? AND password = ? AND active = 'Y'
    ↓ success
Update last_login → redirect per role:
    DRAFTER  → drafter_list.htm?u=...&r=DRAFTER&n=Nama
    ADMIN    → admin_dashboard.htm?u=...&r=ADMIN&n=Nama
    APPROVER → approver_list.htm?u=...&r=APPROVER&n=Nama
    OTHERS   → dashboard.htm?u=...&r=OTHERS&n=Nama
```

### Auth Mechanism
- **URL params**: `?u={user_id}&r={role}&n={full_name}` (passed between pages)
- **Server-side cookie**: CL_BSP_SERVER_SIDE_COOKIE, name=ECM_AUTH
- **Cookie fields**: USER_ID, FULL_NAME, ROLE, SESSION_ID
- **Set on**: login (OnInputProcessing)
- **Read on**: every page OnInit (security check)
- **Password**: plain text comparison (despite field name `ZECM_PWD_HASH`)

### User Management
- **Page**: user_list.htm (superadmin only)
- **CRUD**: Create, Edit, Deactivate users
- **Fields**: user_id (auto), full_name, password, role, active (Y/N)
- **Roles**: ADMIN, APPROVER, DRAFTER, OTHERS

---

## 13. COMPLETE DMS APPROVE FLOW (Detail)

### DMS Approve (3-Step Chain)
```
AP → FR:
  Step 1: statusintern = 'AP' → BAPI_DOCUMENT_CHANGE2 → COMMIT
  Step 2: statusintern = 'FR' → BAPI_DOCUMENT_CHANGE2 → COMMIT
  Step 3: Obsolete versi lama:
    SELECT dokvr FROM draw WHERE dokst = 'FR' AND dokvr <> current
    LOOP: statusextern = 'H4' → BAPI_DOCUMENT_CHANGE2 → COMMIT
  Step 4: Email notification (ZMAIL_DMS_NOTIFY, kecuali DMT)
```

### DMS Reject
```
AP → ZG:
  statusintern = 'ZG' → BAPI_DOCUMENT_CHANGE2 → COMMIT
```

### DMS Revisi (2-Step)
```
AP → ZG → IA:
  Step 1: statusextern = 'ZG' → BAPI_DOCUMENT_CHANGE2 → COMMIT
  Step 2: statusextern = 'IA' → BAPI_DOCUMENT_CHANGE2 → COMMIT
```

### Email Notification
- **FM**: ZMAIL_DMS_NOTIFY
- **Trigger**: Setelah DMS berhasil FR (approve)
- **Exception**: Tidak kirim email untuk tipe DMT (Metal)
- **Recipient**: Approver email (from USR21 + ADR6)
- **Params**: doknr, dokar, dokvr, doktl, dktxt, approver_email

### Otorisasi DMS Approval
- Hardcode: `sy-uname = 'KMI-U057'` atau `'AUTO_EMAIL'`
- Non-authorized user → error "Anda tidak memiliki hak akses"

---

## 14. Z_ECM_CREATE_CHANGE_NUMBER (Spec FM)

### Tujuan
Create SAP Change Number (AENR) secara programmatic saat approve ECR, tanpa CC01 BDC.

### Interface
```
IMPORTING:
  IV_ECR_NO  (NUMC10)   ← ECR number
  IV_TITLE   (CHAR40)    ← Judul perubahan
  IV_REASON  (CHAR40)    ← Alasan (opsional)
  IV_MATNR   (CHAR18)    ← Material FG (opsional, untuk object link)
  IV_DOKAR   (CHAR3)     ← Tipe dokumen DRW/DBX/DMT (opsional)
  IV_DOKNR   (CHAR25)    ← Nomor DMS (opsional)
  IV_DOKVR   (CHAR2)     ← Versi DMS (opsional)
  IV_DOKTL   (CHAR3)     ← Part DMS (opsional)

EXPORTING:
  EV_AENNR   (CHAR12)    ← Change Number yang di-generate
  EV_SUCCESS (ABAP_BOOL) ← Berhasil/gagal
  EV_MESSAGE (STRING)    ← Pesan
```

### Tables yang Di-insert
| Tabel | Key | Fields |
|-------|-----|--------|
| AENR | AENNR | CCART='ZECR', TEXT1, DATUV, GRUND, AENST='01', ERNAM, ERDAT, AENAM |
| AENR_STATUS | AENNR+STAT | STAT='01', USNAM, DATUM, ZEIT |
| AEOI | AENNR+OBJTP+OBJKY | OBJTP='MARA', OBJKY=matnr (jika ada) |
| AEOI | AENNR+OBJTP+OBJKY | OBJTP='DRAW', OBJKY=doknr (jika ada) |

### Integration di Approver
```
approve_ecr → DMS release → CALL 'Z_ECM_CREATE_CHANGE_NUMBER' → UPDATE ZECM_REQ SET aennr = ...
```

### Prerequisites di SAP
| # | Item | TCode | Status |
|---|------|-------|--------|
| 1 | Number Range AENNR | SNRO | ❓ Cek object AENNR, nr 01 |
| 2 | Change Type ZECR | TCC11/SPRO | ❓ Cek CCART value |
| 3 | AENR table | SE11 | ❓ Cek field lengkap |
| 4 | AENR_STATUS | SE11 | ❓ Cek STAT values |
| 5 | AEOI | SE11 | ❓ Cek OBJTP values |

---

## 15. UI/UX PATTERNS

### Design System
- **Font**: DM Sans (body) + DM Mono (code/numbers)
- **Colors**: CSS custom properties (--bg, --surface, --accent, --danger, --success, --muted)
- **Framework**: Tailwind CSS (utility classes)
- **Charts**: Chart.js (stacked bar, doughnut, horizontal bar)
- **Modals**: SweetAlert2 (alerts, confirmations, input forms)
- **Icons**: Font Awesome 6

### Card Labels (Pak Bos Convention)
| Status | Label | Subtitle |
|--------|-------|----------|
| CRTD | **ECR** | Menunggu approval |
| INWK | **ECO** | ECO aktif |
| INSP | **On Inspection** | Tunggu review |
| REJC | **Rejected** | ditolak (lowercase) |

**JANGAN gunakan**: "ECR Aktif", "Dalam Proses", "Inspection", "Ditolak"

Label harus KONSISTEN di: cards, doughnut chart, stacked bar chart, horizontal bar chart.

### Chart Types
| Chart | Library | Data Source | Notes |
|-------|---------|------------|-------|
| Volume Perubahan | Chart.js stacked bar | ZECM_REQ GROUP BY month+status | 6 bulan, per status |
| Status Change Request | Chart.js horizontal bar | ZECM_REQ COUNT by status | Legend click disabled |
| Status Distribution | Chart.js doughnut | ZECM_REQ COUNT by status | Per role (admin/approver/drafter) |

### Date Range Filter
- **Default**: awal bulan → hari ini
- **Shortcut buttons**: 1 Bulan, 2 Bulan, 6 Bulan (auto-set + submit)
- **Input type**: HTML `<input type="date">` (format YYYY-MM-DD)
- **Conversion**: strip dashes → YYYYMMDD → assign to TYPE d
- **Applied to**: semua query cards, charts, tables di dashboard

### SweetAlert Patterns
```javascript
// Alert sukses
Swal.fire({ icon: 'success', title: 'Berhasil', text: msg, timer: 2000 })

// Konfirmasi
Swal.fire({ title: 'Yakin?', text: '...', icon: 'warning',
  showCancelButton: true, confirmButtonText: 'Ya' })

// Input textarea (reject reason)
Swal.fire({ title: 'Alasan Reject', input: 'textarea',
  inputPlaceholder: 'Tulis alasan...', showCancelButton: true })

// SweetAlert DI DALAM MODAL → WAJIB tambah target
Swal.fire({ target: document.getElementById('ecrModal'), ... })
```

### Material Search Pattern
- **Source**: MARA (material master) + MAKT (material description)
- **Search**: keyword → SELECT WHERE matnr LIKE '%keyword%' OR maktx LIKE '%keyword%'
- **MTART Badge**:
  - FERT (Finish Goods) → 🟢 green
  - HALB (Semifinish Goods) → 🔵 blue
  - HALM (Semifinish Metal) → 🟠 orange
- **Modal**: tetap terbuka setelah search (tidak navigate)

### PRG Pattern (Post-Redirect-Get)
Mencegah duplicate submission:
```
OnInputProcessing (POST):
  1. Process action (INSERT/UPDATE/DELETE)
  2. BUKAN navigation->goto_page() (akan POST ulang)
  3. TAPI redirect GET: CONCATENATE page.htm '?msg=berhasil' INTO url
     navigation->goto_page( url )
```

### Audit Trail Modal
- **Data**: SELECT FROM zecm_log WHERE ecr_no = current_ecr
- **Display**: timeline (vertical) dengan icon per action
- **Info**: action, old_status → new_status, user, date, time, reason
- **DMS Link**: clickable link ke DMS detail (jika ada dir_number)

---

## 16. COMPLETE FILE LIST — V05_i (61 FILES)

### Dashboard & Overview (8 files)
| File | Fungsi |
|------|--------|
| dashboard.htm | Superadmin dashboard (existing) |
| dashboard_oninit.txt | OnInit superadmin |
| dashboard_event_handler.txt | Event handler superadmin |
| dashboard_page_attributes.txt | Page attributes superadmin |
| admin_dashboard.htm | Admin dashboard (cards + charts + tables) |
| admin_dashboard_oninit.txt | Query data, date filter, count status |
| admin_dashboard_event_handler.txt | Logout, navigation |
| admin_dashboard_page_attributes.txt | GV_* variables |

### Admin ECR List (5 files)
| File | Fungsi |
|------|--------|
| admin_ecr_list.htm | Admin ECR list (table + filter) |
| admin_ecr_list_oninit.txt | Query ECR list |
| admin_ecr_list_event_handler.txt | Actions (approve/reject) |
| admin_ecr_list_page_attributes.txt | Variables |
| admin_ecr_list_type_definitions.txt | Types |

### Drafter (5 files)
| File | Fungsi |
|------|--------|
| drafter_list.htm | Drafter dashboard (cards + list) |
| drafter_list_oninit.txt | Query data, DMS detection, date filter |
| drafter_list_event_handler.txt | Submit ECR, reject, cancel (PRG pattern) |
| drafter_list_page_attributes.txt | Variables |
| drafter_list_type_definitions.txt | Types (termasuk drafter_name) |

### Approver (5 files)
| File | Fungsi |
|------|--------|
| approver_list.htm | Approver dashboard (cards + doughnut + list) |
| approver_list_oninit.txt | Query data, DMS detection, date filter |
| approver_list_event_handler.txt | Approve/reject/revisi ECR |
| approver_list_page_attributes.txt | Variables |
| approver_list_type_definitions.txt | Types |

### ECR Form (5 files)
| File | Fungsi |
|------|--------|
| ecr_form.htm | Form create ECR (modal popup) |
| ecr_form_oninit.txt | Init form |
| ecr_form_event_handler.txt | Submit create ECR |
| ecr_form_page_attributes.txt | Variables |
| ecr_form_type_definitions.txt | Types |

### DMS (8 files)
| File | Fungsi |
|------|--------|
| dms_list.htm | DMS document list (pagination, filter) |
| dms_list_oninit.txt | Query DMS documents |
| dms_list_event_handler.txt | List actions |
| dms_list_page_attributes.txt | Variables |
| dms_list_type_definitions.txt | Types |
| dms_detail.htm | DMS detail (header + files + status log) |
| dms_detail_oninit.txt | Load detail + status log |
| dms_detail_page_attributes.txt | Variables |

### DMS Download (1 file)
| File | Fungsi |
|------|--------|
| dms_detail_download_event_handler_on_request.txt | Download file dari content server |

### Headers (4 files)
| File | Fungsi |
|------|--------|
| admin_header.htm | Header untuk admin (Dashboard + Monitoring + User Mgmt) |
| approver_header.htm | Header untuk approver (Dashboard + Inspection + DMS) |
| drafter_header.htm | Header untuk drafter (ECR List + DMS) |
| app_header.htm | Header universal (detect role, conditional nav) |
| superadmin_header.htm | Header superadmin (existing) |

### Login (3 files)
| File | Fungsi |
|------|--------|
| login.htm | Login page (user_id + password) |
| login_oninit.txt | OnInit login |
| login_event_handler.txt | Auth check + routing per role |
| login_page_attributes.txt | Variables |

### User Management (5 files)
| File | Fungsi |
|------|--------|
| user_list.htm | User CRUD (superadmin only) |
| user_list_oninit.txt | Load users |
| user_list_event_handler.txt | Create/edit/deactivate |
| user_list_page_attributes.txt | Variables |
| user_list_type_definitions.txt | Types |

### Spec Document (1 file)
| File | Fungsi |
|------|--------|
| Z_ECM_CREATE_CHANGE_NUMBER_spec.md | Spec FM untuk create AENR |

---

## 17. STAKEHOLDER & COMMUNICATION

### Pak Bos (Surjantoro) — Owner KMI
- **Level**: Business Process + Functional SAP
- **BOLEH**: Sebut TCode standar SAP (CC01/CC02/CC03, CS01/CS02, dll)
- **JANGAN**: Masuk ranah ABAP (SELECT, internal table, Page Attributes, dll)
- **Penjelasan**: DETAIL tentang alur sistem, bukan singkat
- **Custom program**: Jelaskan APA fungsinya, bukan BAGAIMANA kode internal

### Pak Ricky (Supervisor IT)
- **Level**: Ringkas, profesional, fokus progress & masalah

### Hanif (Basis)
- **Level**: Sabar, mudah dipahami, hanya topik SAP

### Pak Eris (Supervisor Drafter)
- **Level**: Fungsional, flow kerja drafter

---

## 18. ZECM_REQ ADDITIONAL FIELDS (untuk Change Number)

Setelah FM Z_ECM_CREATE_CHANGE_NUMBER diimplementasi:
| Field | Type | Keterangan |
|-------|------|------------|
| AENNR | CHAR 12 | SAP Change Number (diisi otomatis saat approve) |

---

## 19. KEY SAP TABLES (Standard) YANG DIGUNAKAN

| Tabel | Fungsi di ECM |
|-------|---------------|
| MARA | Material master (lookup MATNR, MTART) |
| MAKT | Material description (lookup MAKTX) |
| DRAW | DMS document header (doknr, dokar, dokvr, dokst) |
| DRAD | DMS object links (doknr → MARA/MARA) |
| DRAP | DMS status log (history perubahan status) |
| DRAT | DMS document description (dktxt) |
| DMS_DOC_FILES | DMS file list (filename, dappl) |
| MAST | BOM header (matnr → stlnr) |
| STKO | BOM header detail |
| STPO | BOM items (stlnr → idnrk) |
| AENR | Change Number header |
| AENR_STATUS | Change Number status log |
| AEOI | Change Number object links |
| USR21 | User address key |
| ADR6 | Email address (SMTP) |

---

## 20. SUMMARY: BAGAIMANA SEMUA TERHUBUNG

```
┌─────────────────────────────────────────────────────────────────┐
│                    ECM/ECR BSP Application                       │
│                    (ZBSP_ECM_APP - V05_i)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                   │
│  │ DRAFTER  │    │  ADMIN   │    │ APPROVER │                   │
│  │ Create   │    │ Dashboard│    │ Dashboard│                   │
│  │ ECR/ECO  │    │ Approve  │    │ Review   │                   │
│  │ Upload   │    │ ECR      │    │ Approve  │                   │
│  │ DMS      │    │ Reject   │    │ DMS      │                   │
│  └────┬─────┘    └────┬─────┘    └────┬─────┘                   │
│       │               │               │                          │
│       ▼               ▼               ▼                          │
│  ┌──────────────────────────────────────────┐                   │
│  │              ZECM_REQ (Database)          │                   │
│  │  CRTD → INWK → INSP → CLSD / REJC       │                   │
│  └──────────────────┬───────────────────────┘                   │
│                     │                                            │
│       ┌─────────────┼─────────────┐                             │
│       ▼             ▼             ▼                              │
│  ┌─────────┐  ┌──────────┐  ┌───────────┐                      │
│  │ ZECM_LOG│  │ SAP DMS  │  │ AENR      │                      │
│  │ Audit   │  │ DRAW/DRAD│  │ Change No │                      │
│  │ Trail   │  │ IA→AP→FR │  │ (spec)    │                      │
│  └─────────┘  └──────────┘  └───────────┘                      │
│                     │                                            │
│                     ▼                                            │
│  ┌──────────────────────────────────────────┐                   │
│  │     ZUPLOAD_CS_AUTO (Background Job)      │                   │
│  │  Auto upload files → DMS + BOM linking    │                   │
│  │  /mnt/sap_media/engineering/              │                   │
│  │  DRW_*.pdf, DBX_*.pdf, DMT_*.pdf,        │                   │
│  │  TDS_*.xlsx                               │                   │
│  └──────────────────────────────────────────┘                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow
```
1. Drafter buat ECR → INSERT ZECM_REQ (CRTD) + INSERT ZECM_LOG
2. Admin approve → UPDATE ZECM_REQ (INWK) + INSERT ZECM_LOG
3. Drafter kerjakan → upload file ke /mnt/sap_media/engineering/
4. ZUPLOAD_CS_AUTO (background) → parse file → create/update DMS → link BOM
5. Drafter submit → UPDATE ZECM_REQ (INSP) + DMS IA→AP + INSERT ZECM_LOG
6. Approver approve → UPDATE ZECM_REQ (CLSD) + DMS AP→FR + obsoleting + email + INSERT ZECM_LOG
   + CALL Z_ECM_CREATE_CHANGE_NUMBER → INSERT AENR/AENR_STATUS/AEOI + UPDATE ZECM_REQ.aennr
7. Reject/revisi di setiap tahap → UPDATE ZECM_REQ + DMS status change + INSERT ZECM_LOG
```

---

*Document ini dibuat oleh Hermes (AI Assistant Arya) untuk sharing insight dengan Claude (AI Assistant Pak Bos). Semua informasi berdasarkan kode dan dokumentasi aktual di server KMI srv168.*
*Last updated: 04 Juli 2026, WIB*
