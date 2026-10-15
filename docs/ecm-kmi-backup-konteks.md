# ECM KMI — BACKUP KONTEKS LENGKAP
## Engineering Change Management — PT. Kayu Mebel Indonesia

**File ini berisi seluruh konteks design ECM KMI.**
**Tujuan: backup kalau session Hermes hilang — baca ini langsung tanpa harus ke RAG.**
**Terakhir diupdate: 2026-06-12**

---

## 1. LATAR BELAKANG

KMI menggunakan SAP S/4HANA 1809 On-Premise. Transaksi **CC31** (SAP Standard ECM) di-BLOCK karena SAP Note 2476734. Transaksi CECN dan CE11 juga TIDAK tersedia di 1809.

Oleh karena itu, KMI harus membuat aplikasi BSP custom **ZBSP_ECM_APP** sebagai pengganti CC31.

Catatan teknis:
- Field Change Type di S/4HANA 1809: **CCART** (NUMC 3, bukan AENART seperti ECC 6.0)
- Tabel Change Type: **TCC11** (master data) + **TCC12** (texts), bukan TCC50
- 48 tabel ECM core ada di sistem, saat ini **0 record** (perlu dikonfigurasi)
- CC01/CC02/CC03 tetap tersedia, CC31 blocked

---

## 2. DESIGN ECM KMI

### Change Type
- **1 Change Type saja: ZECR** untuk semua DOKAR
- Design lama (OBSOLETE): 3 Change Type terpisah ZECR_DRW/ZECR_DBX/ZECR_DMT — TIDAK DIPAKAI
- Design lama lainnya (OBSOLETE): ZECM Full, ZECML Material Lite, ZECRE Emergency — TIDAK DIPAKAI

### Scope DOKAR (yang masuk ECM)
| DOKAR | Divisi       | Warna Label BSP | Keterangan                            |
|-------|-------------|-----------------|----------------------------------------|
| DRW   | Wood (Kayu) | Biru (#1d4ed8)  | Drawing produk kayu                    |
| DBX   | Box (Panel) | Ungu (#7c3aed)  | Drawing panel, box, instruksi perakitan|
| DMT   | Metal (Besi)| Hijau (#15803d)  | Drawing produk logam                  |

**TIDAK masuk ECM:** TDS (Technical Data Sheet) — flow tetap biasa: IA → FR langsung, tanpa approval ECM.

### Scope Object (yang terikat ke Change Number)
| Objek                  | Tabel | Keterangan                              |
|------------------------|-------|------------------------------------------|
| Material Master (FG)   | MARA  | Perubahan spesifikasi Material FG        |
| Document Info Record   | DRAW  | Revisi drawing, upload versi baru        |

**Belum masuk scope:** BOM (STKO/STPO) dan Routing (PLFH/PLPO) — diimplementasikan nanti jika dibutuhkan.

### Rule Penting
- **1 ECO = 1 DIR**
- **1 Change Type ZECR** untuk semua DOKAR
- Material FG **WAJIB** diisi di form ECR — bukan opsional. Ini kunci utama tracing riwayat perubahan per material FG.
- DOKAR di-resolve di level form ECR dan DIR sebagai label, bukan di level Change Type

---

## 3. ALUR ECM (4 FASE)

### FASE 1 — ECR REQUEST
1. Requester buka BSP ZBSP_ECM_APP (web browser)
2. Sistem cek: user terdaftar di ZECM_USER?
   - Tidak → Ditolak, hubungi admin → STOP
   - Ya → lanjut
3. Requester isi form ECR:
   - Pilih DOKAR (DRW/DBX/DMT)
   - Kode Material Finish Goods (WAJIB)
   - Deskripsi perubahan
4. Sistem buat Change Number otomatis, Change Type: ZECR
   - Status: CRTD (Created)
   - Data tersimpan di ZECM_REQ
5. Notifikasi dikirim ke Dashboard Drafter

### FASE 2 — DRAFTER PROSES (ECR → ECO)
6. ECR muncul di Dashboard Drafter (ZBSP_ECM_APP) — satu halaman general, filter per DOKAR
7. Drafter: terima atau tolak?
   - Tolak → status REJECTED, notifikasi ke Requester → STOP (requester buat ECR baru)
   - Terima → lanjut
8. ECR menjadi ECO
   - Status: CRTD → REVW (In Progress)
   - Drafter tercatat di ZECM_REQ

### FASE 3 — UPLOAD & ASSIGN DIR
9. Drafter upload/revise drawing via ZBSP_DMS_APP atau ZUPLOAD_CS_AUTO
10. Sistem cek: DIR sudah ada?
    - Belum → buat DIR baru, status IA, versi 00
    - Sudah → buat versi baru, versi naik, status IA
11. Drafter pilih ECO, pilih DIR terkait, klik PROSES
12. Sistem link DIR ke ECO:
    - DRAW-AENNR = Change Number
    - Status DIR: IA → AP
    - Status ECO: REVW → APPR

### FASE 4 — INSPECTION & RELEASE
13. DIR muncul di halaman Approval DMS (ZBSP_DMS_APP), filter: DOKAR ECM + Status AP
14. Pak Eris review drawing
15. Approve atau Reject?
    - Reject → Status DIR: AP → IA, Status ECO: APPR → REVW → LOOP KOREKSI ke Fase 3
    - Approve → lanjut
16. Status DIR: AP → FR (Released), Status ECO: APPR → CLSD (Closed)
17. Change Number selesai, perubahan tercatat & teraudit

### Catatan Loop Koreksi
- Reject oleh Drafter (Fase 2) → STOP, bukan loop
- Reject oleh Pak Eris (Fase 4) → loop kembali ke Fase 3 (revise ulang)

---

## 4. STATUS LIFECYCLE

### Change Number (ECO)
| Status | Keterangan                     |
|--------|-------------------------------|
| CRTD   | Created — ECR baru dibuat      |
| REVW   | Under Review — Drafter kerja   |
| APPR   | Approved for Inspection        |
| CLSD   | Closed — Disetujui, selesai    |

### Document Info Record (DIR)
| Status | Keterangan                          |
|--------|--------------------------------------|
| IA     | In Work — drawing dikerjakan/direvise|
| AP     | Awaiting Approval — menunggu review |
| FR     | Finally Released — disetujui        |

**Non-ECM DIR (termasuk TDS):** IA → FR langsung (skip AP)

---

## 5. AKTOR & ROLE

| Role                | Nama/Posisi          | Fungsi                                                   |
|---------------------|----------------------|----------------------------------------------------------|
| Requester           | Siapa saja (ZECM_USER)| Ajukan ECR via ZBSP_ECM_APP                              |
| Drafter             | Tim Engineering      | Terima ECR, kerjakan ECO, upload/revise drawing          |
| Approver            | Pak Eris (Supervisor)| Review & approve/reject drawing di ZBSP_DMS_APP           |
| Admin               | IT                   | Maintain ZECM_USER via SM30                               |
| Sistem SAP          | Backend otomatis     | Create Change Number, update status, notifikasi           |

Pemisahan peran:
- Requester TIDAK bisa approve
- Drafter TIDAK bisa membuat material (MM01) — hanya tim Master Data
- Approver hanya Pak Eris untuk semua DOKAR (DRW/DBX/DMT)
- Dashboard Drafter: satu halaman general, filter per DOKAR, siapa saja yang mau ambil ECR tinggal klik terima

---

## 6. CUSTOM TABLES

### ZECM_USER — Daftar Requester
- Maintain via SM30 oleh Admin
- Field: SAP User ID, nama, departemen, status aktif
- Validasi: saat requester buka form ECR, sistem cek apakah user terdaftar di sini

### ZECM_REQ — Log/Record ECR/ECO
- Field: nomor ECR, Change Number (AENNR), Requester, Drafter, Material FG (wajib), DOKAR (DRW/DBX/DMT), deskripsi perubahan, status, timestamp create dan update

Kedua tabel BELUM dibuat di SAP — masih tahap design.

---

## 7. APLIKASI BSP

### ZBSP_ECM_APP (BARU — pengganti CC31)
Status: **BELUM mulai coding**

Scope:
- Halaman Request ECR: form input DOKAR, Material FG (wajib), deskripsi
- Dashboard Drafter: satu halaman general, filter per DOKAR, aksi terima/tolak
- Halaman Proses ECO: link DIR ke ECO

### ZBSP_DMS_APP (MODIFIKASI — tambah filter ECM)
Status: sudah ada dan berjalan, perlu modifikasi

Modifikasi:
- Tambah filter: DOKAR ECM (DRW/DBX/DMT) + Status AP
- Halaman review untuk Pak Eris (approve/reject drawing)
- Reject → loop koreksi (DIR AP → IA, ECO APPR → REVW)
- Distinguish: DIR ECM lewat AP, DIR non-ECM langsung IA → FR

Referensi teknis ZBSP_DMS_APP:
- Controller: ZCL_DMS_CONTROLLER
- Pages: zdms_list.htm, zdms_detail.htm
- BAPI: BAPI_DOCUMENT_CHANGE2
- Approval saat ini: user AUTO_EMAIL / KMI-U057 (mv_can_approve = true)
- Perlu ditambahkan otorisasi untuk role Approver ECM (Pak Eris)

---

## 8. INTEGRASI TEKNIS

- **ZBSP_ECM_APP** ↔ SAP ECM Backend — BAPI/FM untuk create Change Number, update status
- **ZBSP_DMS_APP** ↔ SAP DMS — BAPI_DOCUMENT_CHANGE2 untuk transisi status DIR (IA → AP → FR)
- **ZUPLOAD_CS_AUTO** v38 — program ABAP background job untuk auto-upload drawing ke DMS Content Server, parsing metadata dari filename, linking dokumen ke BOM material (legacy, akan dievaluasi saat ECTR rollout)
- **ZECM_USER / ZECM_REQ** — custom tables di SAP dictionary (SE11)

---

## 9. TRANSAKSI ECM

| TCODE     | Fungsi                | Status di KMI |
|-----------|-----------------------|--------------|
| CC01      | Create Change Number  | ✅ Tersedia (dipanggil sistem otomatis) |
| CC02      | Change Change Number  | ✅ Tersedia   |
| CC03      | Display Change Number | ✅ Tersedia   |
| CC04      | Change Documents      | ✅ Tersedia   |
| CC13      | Object Overview       | ✅ Tersedia   |
| CC14      | Where-Used List       | ✅ Tersedia   |
| S_CC_PRC  | Change Number Reports | ✅ Tersedia   |
| CC31      | Engineering Workbench| ❌ BLOCKED (SAP Note 2476734) |
| CECN/CE11 | (N/A)                 | ❌ Tidak tersedia di 1809 |

---

## 10. KONFIGURASI SPRO (ROADMAP)

Langkah konfigurasi ECM di SAP S/4HANA 1809:

1. Activate Change Master
2. Define Change Types — ZECR (satu-satunya)
3. Define Object Types — Material (41), Document (31) saja
4. Define Change Number Range
5. Define Release Key / Approval Workflow
6. Define Status Profile — CRTD → REVW → APPR → CLSD
7. Assign Change Types to Object Types
8. Maintain Settings per Plant (1000, 2000, 3000)

Catatan: KMI tidak memiliki Customizing Project di SPRO, jadi konfigurasi beberapa hal perlu via SM30 langsung.

---

## 11. CATATAN TENTANG ECTR

KMI berencana implementasi SAP ECTR (Engineering Control Center) di masa depan.
- ECTR berfungsi sebagai front-end CAD → ECM → DMS
- ECTR mengandalkan ECM sebagai approval engine — tidak bypass
- Prioritas: ECM harus fully implemented dan stabil dulu sebelum ECTR rollout
- ZUPLOAD_CS_AUTO bisa di-phase-out untuk dokumen engineering saat ECTR aktif
- ZECM/ZECML/ZECRE (design lama ECM) sudah dibahas dengan konsultan SAP — sekarang sudah diganti dengan design ZECR

---

## 12. INFORMASI SISTEM KMI

- SAP: S/4HANA 1809 On-Premise, SS03
- BASIS: 753 SP03 (NOT SP74)
- DB: HANA 2.0 SPS04 Rev045
- Machine: IBM Power LE (linuxppc64le)
- OS: SLES 15 SP1
- Server: kmiqas_OAS_01
- Client: 200 = ECM, 300 = QM
- QAS → PRD: manual rebuild (no transport)
