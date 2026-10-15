# CHANGELOG — v14_i_panel_print_split
Tanggal: 12 September 2026
Tipe: Enhancement & Feature Split (Panel-Specific Reporting / Print PDF)

## 📌 Ringkasan Perubahan
Memperbaiki fitur Cetak di Dashboard Admin (`admin_dashboard.htm`) yang sebelumnya menyatu di toolbar filter atas dan hanya mencetak tabel ECR. Fitur cetak kini dipecah dan dipindahkan langsung ke masing-masing panel utama agar Admin dapat mencetak laporan spesifik sesuai konteks data:

### 1. Pemecahan Tombol Cetak per Panel:
- **Panel Request Masuk (`IREQ`)**:
  - Menambahkan tombol hijau *"Cetak Request Masuk"* di header panel.
  - URL parameter: `type=ireq`.
  - Mencetak daftar request masuk (`ZECM_IREQ` status `REQ`, `APPR`, `REJC`, `ECO`) beserta kolom: NO, IREQ ID, Judul Request, Material & Deskripsi, Kategori, Prioritas, Departemen, Status, Requester, dan Tanggal.
- **Panel Antrian Approval (`CRTD`)**:
  - Menambahkan tombol oranye *"Cetak Antrian Approval"* di header panel.
  - URL parameter: `type=approval`.
  - Mencetak daftar ECR berstatus `CRTD` yang menunggu persetujuan Admin (`ZECM_REQ`) beserta PIC Drafter dan Requester.
- **Panel Daftar ECR (Seluruh Data)**:
  - Menambahkan tombol biru *"Cetak Daftar ECR"* di sebelah kontrol pencarian & pagination.
  - URL parameter: `type=ecr`.
  - Mencetak seluruh ECR dalam rentang tanggal filter yang dipilih.

### 2. Penghapusan Tombol Cetak Global:
- Menghapus tombol lama `btnCetakEcr` pada baris filter tanggal atas agar UI lebih bersih dan tidak membingungkan pengguna.

### 3. Dinamisasi Halaman Cetak (`admin_print_ecr`):
- `admin_print_ecr_page_attributes.txt`:
  - Menambahkan atribut: `GV_PRINT_TYPE`, `GV_REPORT_TITLE`, dan `GV_TH_HEADER`.
- `admin_print_ecr_oninit.txt`:
  - Menambahkan percabangan logika query dan rendering HTML berdasarkan `GV_PRINT_TYPE` (`ireq`, `approval`, atau `ecr`).
- `admin_print_ecr.htm`:
  - Menampilkan judul laporan dan kolom header tabel secara dinamis sesuai tipe laporan yang dicetak.
- `admin_print_ecr_type_definitions.txt`:
  - Menambahkan field `drafter` dan `drafter_name` pada tipe data cetak.

## 📂 File yang Dimodifikasi:
1. `admin_dashboard.htm`
2. `admin_print_ecr.htm`
3. `admin_print_ecr_oninit.txt`
4. `admin_print_ecr_page_attributes.txt`
5. `admin_print_ecr_type_definitions.txt`
