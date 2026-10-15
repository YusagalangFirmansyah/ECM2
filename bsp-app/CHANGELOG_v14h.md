# CHANGELOG — v14_h_add_dept_reason
Tanggal: 12 September 2026
Tipe: Enhancement Form Input (Master Dropdown Sync)

## 📌 Ringkasan Perubahan
Menambahkan opsi pilihan Departemen dan Alasan Perubahan baru pada form Request Perubahan Baru di role Requester (`requester_list.htm`), serta menyinkronkan opsi tersebut ke seluruh form terkait (Admin Review, Admin Dashboard, Drafter List, dan ECR Form).

### 1. Departemen Baru Ditambahkan:
- **`Purchasing`**

### 2. Alasan Perubahan Baru Ditambahkan:
- **`Perubahan Bahan`**

## 📂 File-File yang Dimodifikasi:
1. `requester_list.htm`
   - Menambahkan `<option value="Purchasing">Purchasing</option>` pada dropdown Departemen.
   - Menambahkan `<option value="Perubahan Bahan">Perubahan Bahan</option>` pada dropdown Alasan Perubahan.
2. `admin_req_review.htm`
   - Menyinkronkan dropdown `zdept` dan `zreason` agar nilai `Purchasing` dan `Perubahan Bahan` terdeteksi saat mode edit/review.
3. `admin_dashboard.htm`
   - Menyinkronkan modal pembuatan ECR langsung oleh Admin.
4. `drafter_list.htm`
   - Menyinkronkan modal pembuatan ECR langsung oleh Drafter.
5. `ecr_form.htm`
   - Menyinkronkan form ECR standalone.

## ⚙️ Backend ABAP:
- Tidak memerlukan perubahan struktur tabel atau event handler karena field `zdept` dan `zreason` pada tabel `ZECM_IREQ` dan `ZECM_ECR` bertipe string char dinamis dan langsung menyimpan nilai string dari form POST.
