# CHANGELOG — v14_f_admin_all_ecr_sources_impl (07 September 2026)

## Implementation Tracking dari Seluruh Sumber Pembuatan / Approval ECO oleh Admin

Menyempurnakan pencatatan *Implementation Tracking* (`IMPL_PO`, `IMPL_DATE`, `IMPL_REASON`) agar berlaku komprehensif pada seluruh pintu masuk pembuatan/persetujuan ECO oleh Admin:

### 1. Jalur ECR Manual Drafter -> Approval Admin (`admin_dashboard`)
- **UI (`admin_dashboard.htm` & `admin_dashboard_oninit.txt`)**:
  - Tombol centang approve (`action=approve`) di tabel Antrian Review ECR diubah menjadi trigger modal SweetAlert2 (`.btn-approve-ecr`).
  - Modal meminta input mandatory: **Target Berjalan (PO)**, **Tanggal Estimasi Jalan**, dan **Keterangan / Alasan Lapangan**.
- **Backend (`admin_dashboard_oninit.txt`)**:
  - Mengambil nilai input implementasi tersebut, memvalidasi agar tidak kosong, dan menyimpannya langsung ke record `ZECM_REQ` bersamaan dengan transisi status dari `CRTD` -> `INWK` (ECO baru).

### 2. Jalur Form Pembuatan ECR/ECO Langsung oleh Admin (`ecr_form`)
- **UI (`ecr_form.htm`)**:
  - Menambahkan Section 4: *Rencana Implementasi (Wajib Diisi Admin)* jika form dibuka oleh role `ADMIN`.
  - Berisi input Target PO, Tanggal Estimasi Jalan, dan Alasan Lapangan.
  - Tombol submit disesuaikan menjadi "Buat ECO Langsung".
  - Validasi JavaScript di `submitForm()`: memastikan ketiga field implementasi tidak boleh kosong untuk Admin.
- **Backend (`ecr_form_event_handler.txt`)**:
  - Mengambil parameter `impl_po`, `impl_date`, dan `impl_reason`.
  - Jika dibuat oleh Admin, status otomatis langsung `INWK` (ECO Aktif) dengan field implementasi terisi penuh, dan diarahkan kembali ke `admin_dashboard.htm`.

### 3. Jalur IREQ Requester -> Admin Review (`admin_req_review`)
- Tetap aktif sesuai penyempurnaan di `v14_e`: Admin mengisikan Target PO, Tanggal, dan Alasan saat membuat ECO (Assign Drafter).
