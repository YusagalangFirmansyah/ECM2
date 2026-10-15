# CHANGELOG - V14 Sub-versi b (Drafter Implementation Tracking)

### Perbaikan & Penambahan:
- **Drafter Dashboard (`drafter_list`)**:
  - Menambahkan *Implementation Tracking (Rencana Rilis)* pada Drafter List agar Drafter juga bisa melihat target Rilis yang sudah ditentukan di awal oleh Kepala R&D.
  - Modifikasi `drafter_list_oninit.txt` untuk mengambil field `impl_po`, `impl_date`, dan `impl_reason` menggunakan `LEFT OUTER JOIN` dari tabel `zecm_ireq` yang dihubungkan lewat `ecr_no`.
  - Menampilkan icon badge "Rilis" pada row tabel jika field *Implementation Tracking* sudah terisi.
  - Menampilkan detail informasi *Implementation Tracking* yang bersifat *Read-Only* di dalam halaman modal/detail ECR Drafter.
- **Approver Dashboard (`approver_list`)**:
  - Memodifikasi *Event Handler* pada fungsi Batal Approve (`cancel_approve_ireq`) agar selain mengembalikan status `APPR` ke `REQ`, juga akan otomatis menghapus/mereset (*clear*) field `impl_po`, `impl_date` (`00000000`), dan `impl_reason` di tabel `zecm_ireq` supaya data yang sudah dibatalkan tidak bocor ke UI Read-Only milik role lain.
