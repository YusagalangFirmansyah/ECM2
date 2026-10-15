# CHANGELOG — ECM BSP Application

Dokumen ini mencatat seluruh riwayat perubahan kode, fitur, dan bugfix pada aplikasi Engineering Change Management (ECM) BSP SAP KMI.

---

## V14 — Implementation Tracking (Target Rilis PO & Tanggal) (31 Agu - 12 Sep 2026) 📦

Fitur pencatatan rencana implementasi lapangan (PO, Tanggal, dan Alasan Lapangan).

### v14_i_panel_print_split (12 Sep 2026) 🌟 CURRENT
- **Pemisahan Fitur Cetak per Panel di Dashboard Admin (`admin_dashboard`)**:
  - Menghapus tombol cetak global lama di baris filter tanggal atas.
  - **Panel Request Masuk**: Tombol *"Cetak Request Masuk"* (`type=ireq`) mencetak daftar IREQ (`ZECM_IREQ`) status `REQ`, `APPR`, `REJC`, `ECO` lengkap dengan kolom Departemen & Requester.
  - **Panel Antrian Approval**: Tombol *"Cetak Antrian Approval"* (`type=approval`) mencetak ECR status `CRTD` yang menunggu persetujuan Admin (`ZECM_REQ`) beserta PIC Drafter & Requester.
  - **Panel Daftar ECR**: Tombol *"Cetak Daftar ECR"* (`type=ecr`) mencetak seluruh riwayat ECR dalam rentang tanggal filter.
  - **Dinamisasi Halaman Cetak (`admin_print_ecr`)**: Judul laporan, kolom header tabel, query data, dan badge count berganti dinamis berdasarkan tipe panel yang dicetak.

### v14_h_add_dept_reason (12 Sep 2026)
- **Penambahan Pilihan Master Departemen & Alasan Perubahan**:
  - **Departemen Baru**: Menambahkan opsi `Purchasing` pada dropdown departemen form Requester (`requester_list.htm`).
  - **Alasan Perubahan Baru**: Menambahkan opsi `Perubahan Bahan` pada dropdown alasan perubahan form Requester (`requester_list.htm`).
  - **Sinkronisasi Multi-Halaman**: Menyinkronkan pilihan dropdown baru tersebut ke seluruh halaman portal terkait: `admin_req_review.htm` (mode review & edit), `admin_dashboard.htm` (modal Buat ECR Admin), `drafter_list.htm` (modal Buat ECR Drafter), dan `ecr_form.htm` (form ECR mandiri).

### v14_g_fix_skip_bom (09 Sep 2026)
- **Fix Bug Skip BOM Drafter (`drafter_list`)**:
  - Memperbaiki pemanggilan fungsi `skipBom('<%= LS_ECR_DETAIL-ecr_no %>')` pada tombol modal detail ECR.
  - Memperbaiki pengiriman form `skipBom` agar menggunakan `actionForm` terpusat (`actionType = 'skip_bom'` dan `actionEcrNo`).
  - Memperbaiki event handler backend `drafter_list_event_handler.txt`: menambahkan update field `bom_check = 'A'` (Ready) dan `bom_notes`, sehingga status ECR langsung siap diajukan ke tahap inspeksi (tombol Submit aktif dan form upload BOM tertutup).

### v14_f_admin_all_ecr_sources_impl (07 Sep 2026)
- **Implementation Tracking Komprehensif di Seluruh Sumber ECR -> ECO**:
  - **Approval ECR Drafter (`admin_dashboard`)**: Tombol centang approve ECR `CRTD` memicu pop-up SweetAlert2 wajib isi Target PO, Tanggal Estimasi, dan Alasan Lapangan sebelum status naik ke `INWK` (ECO).
  - **Create ECR Langsung oleh Admin (`ecr_form`)**: Jika Admin membuat permohonan langsung, form menyediakan Section 4 untuk input Rencana Implementasi, status ECR langsung `INWK` (ECO aktif), dan diarahkan ke `admin_dashboard`.
  - **Review IREQ Requester (`admin_req_review`)**: Tetap aktif, Admin wajib mengisi Target Rilis saat klik "Buat ECO" (Assign Drafter).

### v14_e_admin_impl_tracking (07 Sep 2026)
- **Pergeseran Alur Bisnis Implementation Tracking**:
  - **Approver (Head R&D)**: Kembali ke approval murni. Modal pop-up input PO/Date/Reason di `approver_list.htm` dan `admin_req_review.htm` dihapus. Persetujuan IREQ (`REQ` -> `APPR`) murni konfirmasi persetujuan tanpa beban input lapangan.
  - **Admin ECR (`admin_req_review`)**: Menjadi PIC pengisian Implementation Tracking saat mengeksekusi pembuatan ECO (penugasan Drafter).
  - Penambahan form input mandatory (`impl_po`, `impl_date`, `impl_reason`) menyatu di bawah dropdown Assign Drafter pada `admin_req_review.htm`.
  - Backend event handler `assign_drafter`/`approve` diperbarui untuk memvalidasi input Admin dan menyimpan data ke `ZECM_REQ` dan `ZECM_IREQ`.

### v14_d_approver_reject_view (04 Sep 2026)
- **Approver Dashboard (`approver_list`)**:
  - Menampilkan *Reject Reason* pada baris/kartu IREQ yang berstatus ditolak (`REJC`).
  - Menambahkan tombol dan pop-up *Audit Trail* langsung pada card IREQ di dashboard Approver.

### v14_c_requester_view (04 Sep 2026)
- **Requester Dashboard (`requester_list`)**:
  - Menghubungkan pembacaan field `IMPL_PO`, `IMPL_DATE`, dan `IMPL_REASON` agar muncul secara read-only pada detail request yang diajukan oleh Requester.

### v14_b_drafter_impl (02-03 Sep 2026)
- **Drafter Dashboard (`drafter_list`)**:
  - Menambahkan informasi Target Rilis (PO, Tanggal, dan Alasan) dari Kepala R&D secara read-only di modal detail ECR Drafter.
  - Menambahkan indikator icon badge "Rilis" pada daftar ECR Drafter.
- **Approver Dashboard (`approver_list`)**:
  - Memodifikasi fungsi Batal Approve (`cancel_approve_ireq`): mereset otomatis field `IMPL_PO`, `IMPL_DATE`, dan `IMPL_REASON` di tabel `ZECM_IREQ` saat status dikembalikan ke `REQ`.

### v14_a_impl_tracking (31 Agu - 01 Sep 2026)
- **Struktur Database (SE11)**:
  - Penambahan field `IMPL_PO` (CHAR 50), `IMPL_DATE` (DATS 8), dan `IMPL_REASON` (CHAR 255) pada tabel `ZECM_IREQ` dan `ZECM_REQ`.
- **Approver Dashboard (`approver_list`)**:
  - Pop-up modal input wajib isi (mandatory) untuk Target PO, Tanggal Efektif Rilis, dan Alasan saat Head R&D menekan Approve IREQ.
- **Admin Request Review (`admin_req_review`)**:
  - Pewarisan data otomatis: Memindahkan nilai `IMPL_PO`, `IMPL_DATE`, dan `IMPL_REASON` dari `ZECM_IREQ` ke `ZECM_REQ` saat Admin membuat ECO/Assign Drafter.
  - Tampilan read-only Implementation Tracking di panel Admin.
- **Viewer & Admin ECR List**:
  - Menampilkan info Implementation Tracking pada expandable detail row di `viewer_list` dan `admin_ecr_list`.

---

## V13 — Prevent Double Request & Status Fix (27-28 Agu 2026) 📦

### v13_a_prevent_double_request (27-28 Agu 2026)
- **Pencegahan Tiket Ganda (Double Request)**:
  - Validasi AJAX dan backend pada Form Requester (`requester_list`) dan Form Manual Drafter (`ecr_form`). Jika material masih terikat pada ECO aktif (`STATUS <> 'CLSD'`), pengajuan request baru diblokir dengan pesan peringatan.
  - Validasi final pada `admin_req_review` saat Admin membuat ECO agar tidak melahirkan nomor ECO ganda untuk material yang sama.
- **BSP Runtime Fix**:
  - Mengganti pemanggilan objek `response->set_cdata` menjadi `_m_response->set_cdata` sesuai standar HTTP handler global class BSP.
- **Status Transisi IREQ**:
  - Saat Admin assign Drafter (Buat ECO), status `ZECM_IREQ` berubah menjadi `ECO` (bukan menggantung di `APPR`), sehingga IREQ selesai dari antrian review dan beralih ke siklus ECR.
  - Perbaikan logging audit trail di `ZECM_LOG`: pencatatan transisi status dirapikan (`APPR` -> `ECO`).

---

## V12 — Request Reject Handling & UI Refinements (20-27 Agu 2026) 📦

### v12_p_admin_approve_bugfix (27 Agu 2026)
- **Fix Admin Review**: Memperbaiki logika pencegahan double-action di `admin_req_review_event_handler.txt` yang sebelumnya salah mencegat request dengan status `APPR`. Admin kini dapat memproses pembuatan ECO tanpa terhalang.

### v12_k s/d v12_o — Admin & Approver Action Updates (24-25 Agu 2026)
- Penambahan fungsi Batal Approve IREQ oleh Approver R&D (`v12_k`).
- Penyesuaian visibilitas tombol aksi Admin dan perbaikan role mapping (`v12_m`, `v12_n`, `v12_o`).

### v12_c s/d v12_j — Dashboard Usability & Filters (21-24 Agu 2026)
- Filter kategori IREQ dan perbaikan rendering deskripsi material panjang (`v12_d`, `v12_j`).
- Fitur UI: Quick Action buttons, Expand All / Collapse All, Active Row highlight, dan perbaikan posisi scroll via `sessionStorage` (`v12_e` s/d `v12_i`).

### v12_a & v12_b — Request Reject & Requester Edit (20-21 Agu 2026)
- Requester dapat melihat alasan penolakan dan mengedit ulang data permohonan yang ditolak (`v12_a`, `v12_b`).

---

## V11 — Multi-Level IREQ Approval (13-20 Agu 2026) 📦

### v11_i s/d v11_m — Dashboard Button & Filter Polish (18-20 Agu 2026)
- Tombol aksi di Panel Request Masuk Admin dikembalikan menjadi "Review" (hijau). Cegatan blokir "Buat ECO" (Perlu Persetujuan R&D) dikendalikan penuh di `admin_req_review.htm`.
- Penyesuaian filter tab approval dan grafik ringkasan pada dashboard Approver.

### v11_a_ireq_approver (13 Agu 2026)
- **Multi-Level Flow**: Requester (`REQ`) -> Head R&D / Approver (`APPR`) -> Admin ECR (`PROC`/`ECO`).
- **Approver Dashboard**: Penambahan tab khusus IREQ untuk persetujuan Head R&D (Pak Eris).
- **Admin Dashboard**: Filter antrian disesuaikan agar hanya menampilkan request yang telah disetujui Head R&D.
- **Attachment Lifecycle**: Tabel temporary `ZECM_BOM_ATT` dipertahankan sampai Admin memproses tiket menjadi ECR (tidak dihapus saat approval awal).

---

## V10 — Routing Approval & Scope Standardization (10-12 Agu 2026) 📦

### v10_a s/d v10_g (10-12 Agu 2026)
- **Keputusan Arsitektur `CHANGE_SCOPE`**:
  - Penggunaan tabel terpisah `ZECM_IROUTING` dibatalkan. Semua data routing digabung ke tabel utama `ZECM_REQ`.
  - Wajib menyertakan filter `CHANGE_SCOPE = 'DRWG'` (Drawing/BOM) atau `CHANGE_SCOPE = 'ROUT'` (Routing) pada setiap query dashboard.
- Pemecahan string literal HTML (CONCATENATE) agar tidak melebihi 255 karakter/baris untuk mencegah error SE80.
- Penambahan role `COSTING` dan `PAYROLL` pada manajemen user dan logika routing login.

---

## V09 — Produksi Role (08-10 Agu 2026) 📦
- Role khusus Produksi untuk mengajukan permohonan perubahan routing langsung melalui antarmuka web.

---

## V08 — Multi Attachment Requester & BOM Gate (03-08 Agu 2026) 📦
- Fitur multi-upload attachment pada form Requester, penyimpanan informasi di `ZECM_BOM_ATT`, dan estimasi biaya (`v08_o`, `v08_p`).
- Integrasi BOM Gate dan catatan perubahan BOM oleh Master Data.

---

## V07 — Master Data Role & BOM Gate (23 Jul - 03 Agu 2026) 📦
- Pembangunan Master Data Dashboard untuk eksekusi penutupan ECR dan approval perubahan BOM.

---

## V06 — Admin PDF & Viewer Role (09-22 Jul 2026) 📦
- Cetak dokumen resmi ECR PDF korporat KMI.
- Penambahan role `VIEWER` (read-only) untuk pemantauan status lintas departemen.

---

## V05 — Dashboard Development & Chart.js (30 Jun - 08 Jul 2026) 📦
- Redesain antarmuka dashboard, integrasi grafik statistik, dan filter rentang tanggal.

---

## V01 s/d V04 — Fondasi & Multi-Role Architecture (Jun 2026) 📦
- Pembangunan MVP ECR form, eliminasi dependensi CC31 S/4HANA yang diblokir, dan transformasi ke sistem multi-role berbasis web BSP.
