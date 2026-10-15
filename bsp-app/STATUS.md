# Status Modul ECM — v14_i_panel_print_split
Status: READY FOR COPY TO SE80 (Print Split Implementation)
Versi Aktif: V14 (Subversi: v14_i_panel_print_split)
Tanggal: 12 September 2026

## Ringkasan Fitur:
1. Tombol cetak dipisahkan ke masing-masing panel:
   - **Panel Request Masuk**: Cetak Laporan IREQ (`type=ireq`).
   - **Panel Antrian Approval**: Cetak Antrian Approval ECR `CRTD` (`type=approval`).
   - **Panel Daftar ECR**: Cetak Seluruh Daftar ECR (`type=ecr`).
2. Tombol cetak global di filter tanggal atas dihapus.
3. Halaman `admin_print_ecr` kini dinamis: judul laporan, kolom tabel, dan data di-query sesuai panel yang diklik.
4. Mewarisi seluruh fitur dari `v14_h_add_dept_reason` (opsi Purchasing & Perubahan Bahan) dan `v14_g_fix_skip_bom` (Skip BOM fix).

## File untuk Di-copy ke SE80:
1. `admin_dashboard.htm` (Layout Dashboard Admin)
2. `admin_print_ecr.htm` (Layout Halaman Cetak)
3. `admin_print_ecr_oninit.txt` (Event Handler OnInit Cetak)
4. `admin_print_ecr_page_attributes.txt` (Page Attributes Cetak)
5. `admin_print_ecr_type_definitions.txt` (Type Definitions Cetak)
