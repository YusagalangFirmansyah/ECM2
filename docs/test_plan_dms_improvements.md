# Test Plan: Validasi Perbaikan Fitur SAP DMS & ECM Drawing

Dokumen ini berisi panduan skenario pengujian komprehensif (*End-to-End Test Plan*) untuk memvalidasi perbaikan sistem yang telah diimplementasikan pada modul **DMS Detail** dan **Drafter List**.

---

## 1. Tujuan Pengujian (Objective)
1. Memastikan dokumen DMS dengan banyak versi (*multi-version*) membuka versi aktif yang memiliki file gambar kerja, bukan draf kosong (*Smart Version Routing*).
2. Memastikan fitur *Version Switcher Dropdown* dapat berpindah antar-versi dokumen secara lancar.
3. Memastikan penghapusan file lampiran berjalan mulus menggunakan *Native CVAPI* tanpa false-negative error KPro.
4. Memvalidasi mekanisme *Safety Guard* (tombol Delete otomatis hilang pada status rilis `FR` dan inspeksi `AP`).
5. Memastikan tidak ada efek samping (*zero regression*) pada alur kerja ECR (Upload, Submit, dan Approval).

---

## 2. Pra-Syarat Pengujian (Prerequisites)
Sebelum menjalankan pengujian, pastikan:
- [ ] Kode BSP di SAP GUI SE80 sudah sesuai dengan file lokal terbaru:
  - `bsp-app/drafter_list_oninit.txt`
  - `bsp-app/dms_detail.htm`
  - `bsp-app/dms_detail_oninit.txt`
  - `bsp-app/dms_detail_event_handler.txt`
- [ ] Akun pengujian memiliki role **Drafter** (misal: `DRAFTER_WOOD`) dan **Approver**.
- [ ] Lakukan **Hard Refresh (`Ctrl + F5`)** pada browser untuk membersihkan cache frontend.

---

## 3. Matriks Skenario Pengujian (Test Cases)

| ID | Kategori Fitur | Skenario Uji | Hasil yang Diharapkan | Status |
| :---: | :--- | :--- | :--- | :---: |
| **TC-01** | **Smart Version Routing** | Klik badge DMS hijau dari baris ECR di Drafter List | Sistem membuka versi aktif (`IA`/`AP`/`FR`), file gambar langsung terlihat lengkap (tidak kosong). | [ ] |
| **TC-02** | **Version Switcher** | Beralih versi via dropdown di kartu header `dms_detail.htm` | Halaman reload dan menampilkan data, status, serta file yang sesuai dengan versi terpilih. | [ ] |
| **TC-03** | **File Deletion (CVAPI)** | Hapus salah satu file lampiran pada versi status `IA` | SweetAlert konfirmasi muncul, file terhapus bersih dari SAP KPro tanpa error lock, tabel langsung refresh. | [ ] |
| **TC-04** | **Re-upload (In-Place)** | Upload ulang file dengan nama yang sama via modal Drafter | File ter-replace rapi di SAP DMS tanpa membuat baris file menumpuk dobel. | [ ] |
| **TC-05** | **Safety Guard Status** | Periksa dokumen yang berstatus `FR` (Released) atau `AP` | Tombol merah `[Delete]` **otomatis disembunyikan**, hanya tombol hijau `[Download]` yang aktif. | [ ] |
| **TC-06** | **Submit Flow Integrasi** | Klik tombol `[Submit]` pada ECR yang dokumennya berstatus `IA` | Status ECR berubah ke `INSP`, status DMS berubah ke `AP`, dan dokumen muncul di Approver. | [ ] |

---

## 4. Panduan Langkah Pengujian Rinci (Step-by-Step)

### Skenario 1: Uji Smart Version Routing (TC-01)
1. Buka halaman **Drafter List** (`drafter_list.htm`).
2. Cari baris ECR yang memiliki dokumen dengan riwayat multi-versi (contoh: Dokumen `200106` Winnetka).
3. Klik badge hijau nomor DMS **`200106`**.
4. **Verifikasi:**
   - Periksa header versi yang terbuka: Harus menampilkan versi aktif yang berisi file (misal Versi `15`), **bukan versi draf kosong** (misal Versi `16` berstatus `AA`).
   - Scroll ke bagian bawah: Ketiga file lampiran (`.dwg`, `.pdf`, `_bom.pdf`) harus tampil lengkap dengan tombol *Download*.

---

### Skenario 2: Uji Version Switcher Dropdown (TC-02)
1. Pada halaman **DMS Detail** (`dms_detail.htm`), perhatikan kartu ringkasan dokumen.
2. Di baris **Versi**, periksa apakah terdapat elemen dropdown `<select>`:
   - Harus terdapat daftar seluruh versi dokumen beserta statusnya (misal: `Ver 16 (AA)`, `Ver 15 (IA)`, `Ver 00 (FR)`).
3. Pilih salah satu versi lain (misal beralih ke `Ver 00 (FR)`).
4. **Verifikasi:**
   - Halaman otomatis me-refresh dan memuat informasi serta daftar file milik versi tersebut.
   - Status badge berubah sesuai versi terpilih.

---

### Skenario 3: Uji Penghapusan File via Native CVAPI (TC-03)
> [!IMPORTANT]
> Pastikan dokumen berada pada versi dengan status **`IA`** (In Work).
1. Siapkan sebuah file uji coba (misal upload dummy file atau gunakan file yang hendak diganti).
2. Di halaman **DMS Detail**, klik tombol merah **`[Delete]`** pada baris file tersebut.
3. Dialog konfirmasi SweetAlert akan muncul: *"Apakah Anda yakin ingin menghapus file ini dari SAP DMS?"*.
4. Klik **"Ya, Hapus!"**.
5. **Verifikasi:**
   - Muncul alert sukses hijau: *"File berhasil dihapus dari SAP DMS"*.
   - Tidak ada lagi error false-negative *"Error while checking in..."*.
   - Baris file tersebut langsung hilang dari daftar lampiran secara instan.
   - Buka SAP GUI tcode `CV03N` untuk memastikan file fisik di tab *Originals* juga telah terhapus di database SAP.

---

### Skenario 4: Uji Re-upload File (In-Place Replacement) (TC-04)
1. Di halaman **Drafter List**, klik tombol **`[Re-upload]`** pada baris ECR.
2. Pilih file gambar revisi dengan nama yang sama persis (misal: `200106.dwg`).
3. Klik tombol **Upload**.
4. **Verifikasi:**
   - Proses upload selesai dengan notifikasi sukses.
   - Buka kembali halaman detail DMS. File lama berhasil digantikan dengan file baru, dan jumlah file tidak bertambah ganda.

---

### Skenario 5: Uji Safety Guard Status Dokumen (TC-05)
1. Buka dokumen yang berstatus **`FR`** (Released) atau **`AP`** (Inspection Required).
2. Amati kolom aksi pada setiap baris file lampiran.
3. **Verifikasi:**
   - Tombol merah **`[Delete]`** **TIDAK MUNCUL** (disembunyikan demi keamanan data produksi).
   - Tombol hijau **`[Download]`** tetap muncul dan dapat digunakan untuk mengunduh gambar.

---

### Skenario 6: Uji Siklus Submit ECR (TC-06)
1. Di halaman **Drafter List**, pastikan:
   - Badge DMS hijau sudah aktif.
   - Status BOM adalah **Ready**.
2. Klik tombol biru **`[Submit]`**.
3. **Verifikasi:**
   - Status ECR berubah menjadi **`INSP`** (*In Inspection*).
   - Masuk ke akun **Approver**: Baris ECR muncul di dashboard Approver dengan tombol **`[Approve]`**, **`[Revisi]`**, dan **`[Tolak]`**.
   - Buka dokumen DMS terkait: Status dokumen telah berubah menjadi **`AP`** (*Inspection Required*).

---

## 5. Lembar Hasil Pengujian (Sign-off Template)

| Tanggal Uji | Penguji (Tester) | Role | Hasil Keseluruhan | Catatan Tambahan |
| :---: | :---: | :---: | :---: | :--- |
| `22/10/2026` | Annasrul Aina Fadli | Drafter Wood | `PASSED` / `PENDING` | |

---

## 6. Tindakan jika Ditemukan Kendala (Troubleshooting)
* **File masih belum muncul setelah klik DMS:** Pastikan SE80 `drafter_list_oninit.txt` dan `dms_detail_oninit.txt` sudah di-activate (Ctrl+F3), lalu lakukan hard reload browser (`Ctrl + F5`).
* **Tombol Delete tidak merespons:** Pastikan file `dms_detail.htm` bagian script JavaScript `confirmDelete(btn)` sudah ter-copy lengkap ke SE80.
* **Error Lock di CV03N:** Pastikan sesi CV02N/CV03N di SAP GUI ditutup terlebih dahulu sebelum menghapus atau mengunggah via web.
