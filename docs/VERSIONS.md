# ECM Project — Timeline & Evolusi Arsitektur

Dokumen ini merangkum evolusi besar (Major Versions) dari proyek ECM, termasuk keputusan arsitektur penting yang tidak boleh dilanggar oleh AI di sesi berikutnya.

## Versi Saat Ini (Target Aktif)
**V14 — Implementation Tracking (Target Rilis PO & Tanggal) (Aktif per 12 Sep 2026)**
- **Sub-versi aktif:** `v14_i_panel_print_split`
- **Pembaruan Terkini:**
  - `v14_i`: Pemisahan fitur cetak per panel di Dashboard Admin (Cetak Request Masuk, Cetak Antrian Approval, dan Cetak Daftar ECR) serta dinamisasi halaman `admin_print_ecr`.
  - `v14_h`: Penambahan pilihan master Departemen (`Purchasing`) dan Alasan Perubahan (`Perubahan Bahan`) pada form Requester serta sinkronisasi multi-halaman (`admin_req_review`, `admin_dashboard`, `drafter_list`, `ecr_form`).
  - `v14_g`: Perbaikan fitur Skip BOM di dashboard Drafter: pemanggilan form via `actionForm`, z-index SweetAlert2 fix, dan penambahan update `bom_check = 'A'` di database sehingga status ECR langsung siap diajukan ke inspeksi.
  - `v14_e` & `v14_f`: Pengisian Target Rilis (`IMPL_PO`, `IMPL_DATE`, `IMPL_REASON`) diberlakukan seragam pada seluruh pintu masuk ECO oleh Admin.

---

## Sejarah Evolusi (Dari Terakhir ke Terdahulu)

### V13 — Prevent Double Request & Audit Trail Cleanup (27-28 Agustus 2026)
- **Pencegahan Tiket Duplikat:** Blokir di frontend (AJAX) dan backend pada form Requester (`requester_list`) dan Drafter (`ecr_form`). Jika material sudah memiliki ECO aktif (`status <> 'CLSD'`), pembuatan tiket dicegat.
- **Admin Review Final Gate:** Validasi di `admin_req_review` saat klik "Buat ECO".
- **Status Transisi Bersih:** Status `ZECM_IREQ` berubah menjadi `ECO` (bukan `APPR`) saat ditugaskan ke Drafter, agar tiket pre-request tertutup rapi dari antrian.
- **Audit Trail:** Transisi status `ZECM_LOG` dirapikan dari `APPR` -> `ECO`.

### V12 — Request Reject Handling & Dashboard UI Refinements (20-27 Agustus 2026)
- **Reject & Resubmit:** Requester dapat melihat alasan penolakan dan mengedit request (`v12_a`, `v12_b`).
- **Dashboard Usability Enhancements:**
  - Fitur Quick Action, Expand All, Active Row Highlight, dan Auto-scroll fix via sessionStorage (`v12_e` s/d `v12_i`).
  - Filter kategori IREQ dan perbaikan rendering deskripsi material (`v12_d`, `v12_j`).
  - Batal Approve IREQ oleh Approver R&D (`v12_k`).
- **Admin Approval Bugfix (`v12_p`):** Perbaikan logika pencegahan double-action di `admin_req_review` agar tidak mencegat tiket berstatus `APPR` sah saat dibuatkan ECO.

### V11 — Multi-Level IREQ Approval (13-20 Agustus 2026)
- Flow Approval IREQ berubah dari 2 tahap menjadi 3 tahap: Requester -> Head R&D / Approver -> Admin ECR.
- Status `APPR` pada `ZECM_IREQ` menandakan IREQ telah disetujui Head R&D, menunggu diproses Admin.
- Tabel Attachment `ZECM_BOM_ATT` tidak dihapus saat disetujui Head R&D, melainkan dipertahankan sampai Admin memprosesnya menjadi ECR.
- Perbaikan tombol aksi Admin Dashboard & penyesuaian filter antrian Approval.

### V10 — Routing Approval (10-12 Agustus 2026)
**KEPUTUSAN ARSITEKTUR KRUSIAL:**
- Ide penggunaan tabel `ZECM_IROUTING` **DIBATALKAN** dan seluruh tabel IROUTING **DEPRECATED**.
- Semua data routing diputuskan masuk ke tabel utama `ZECM_REQ`.
- Untuk membedakan ECR BOM/Engineering dengan ECR Routing, diperkenalkan filter wajib menggunakan field **`CHANGE_SCOPE`**.
  - `CHANGE_SCOPE = DRWG` untuk ECR BOM/Drawing.
  - `CHANGE_SCOPE = ROUT` untuk Request Routing.
- Setiap kali AI menulis `SELECT` query untuk dashboard manapun (Produksi, Costing, Admin, Master Data), **WAJIB MENYERTAKAN** filter `CHANGE_SCOPE` di klausa `WHERE` atau melakukan `DELETE lt_tabel WHERE change_scope = ROUT` apabila menggunakan loop ABAP.

### V09 — Produksi Role (08-10 Agustus 2026)
- Penambahan role baru khusus untuk user Produksi.
- Login Routing & Dashboard otomatis untuk role PRODUKSI agar langsung diarahkan ke halaman permohonan routing (yang kemudian disempurnakan di V10).

### V08 — Multi Attachment Requester + BOM (03-08 Agustus 2026)
- Pengenalan penyimpanan attachment IREQ. File diupload oleh Requester ke folder `/mnt/sap_media/ecm_files/` dan informasinya direkam di `ZECM_BOM_ATT`.
- File attachment dibersihkan jika IREQ ditolak (`REJC`) atau dialihkan lifecycle-nya saat diproses menjadi ECR utuh.

### V07 — Master Data Role & BOM Gate (23 Juli - 03 Agustus 2026)
- Master Data Dashboard: Memfasilitasi role Master Data untuk mengeksekusi (Close) request yang sudah disetujui, mencakup perubahan BOM.
- Refactor layout dan pembersihan logic IREQ ke ECR. 

### V06 — Admin PDF & Pagination (09-22 Juli 2026)
- Cetak ECR PDF dengan desain korporat KMI, penambahan Viewer Role read-only.

### V05 — Dashboard Development & Date Filter (Akhir Juni - Awal Juli 2026)
- Perombakan besar pada struktur Dashboard ECR untuk Drafter, Admin, dan Approver. Penambahan grafik chart.js.

### V04 & V03 — Multi-Role & ECR List (Pertengahan Juni 2026)
- Transisi dari aplikasi linear menjadi multi-role (Admin, Drafter, dsb).
- Menghapus kewajiban pengisian DOKAR di tabel `ZECM_REQ` (dianggap sebagai urusan DMS secara terpisah).

### V01 s.d V02 — MVP & Error Cleanup
- Pembangunan MVP form ECR dan penggantian CC31 S/4HANA 1809 yang diblok.
