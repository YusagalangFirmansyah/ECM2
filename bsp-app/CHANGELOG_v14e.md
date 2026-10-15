# CHANGELOG — v14_e_admin_impl_tracking (07 September 2026)

## Perubahan Alur Bisnis Implementation Tracking
Berdasarkan hasil diskusi dengan user, alur pengisian Implementation Tracking dialihkan dari **Approver (Head R&D)** ke **Admin ECR**:
1. **Approver (Head R&D)**:
   - Kembali ke alur approval murni.
   - Saat Approver klik "Approve IREQ", tidak lagi muncul modal popup pengisian Target PO / Tanggal / Alasan. Cukup dialog konfirmasi persetujuan standar (Status `REQ` -> `APPR`).
2. **Admin ECR (`admin_req_review`)**:
   - Menjadi penanggung jawab pengisian *Implementation Tracking* (Target Berjalan / PO, Tanggal Estimasi Jalan, dan Alasan / Kondisi Lapangan).
   - Form input Implementation Tracking diletakkan langsung di halaman `admin_req_review.htm` menyatu di bawah panel penugasan Drafter (*Assign Drafter*).
   - Validasi ketat di frontend dan backend: Admin **wajib** memilih Drafter dan mengisi ketiga field tersebut sebelum sistem membuatkan nomor ECO baru.
   - Nilai Implementation Tracking yang diisi Admin otomatis disimpan ke tabel `ZECM_REQ` (ECO baru) dan di-update ke tabel `ZECM_IREQ` agar data tetap sinkron di seluruh dashboard (Requester, Drafter, Viewer).
