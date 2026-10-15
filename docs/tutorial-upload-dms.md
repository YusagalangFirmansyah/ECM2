# Tutorial Upload DMS — Untuk Drafter

**Sistem:** DMS Tools (ZDMS) + File Browser + SAP DMS
**Target User:** Drafter / Engineering Staff
**Terakhir Update:** 16 Juli 2026

---

## Daftar Isi

1. [Overview Proses Upload DMS](#1-overview-proses-upload-dms)
2. [Persiapan: Siapkan File dengan Nama yang Benar](#2-persiapan-siapkan-file-dengan-nama-yang-benar)
3. [Langkah 1: Rename File menggunakan DMS Tools](#3-langkah-1-rename-file-menggunakan-dms-tools)
4. [Langkah 2: Upload File ke File Browser](#4-langkah-2-upload-file-ke-file-browser)
5. [Langkah 3: Tunggu Proses Otomatis](#5-langkah-3-tunggu-proses-otomatis)
6. [Langkah 4: Verifikasi DMS di ECM](#6-langkah-4-verifikasi-dms-di-ecm)
7. [Langkah 5: Cek Dokumen di SAP DMS](#7-langkah-5-cek-dokumen-di-sap-dms)
8. [Naming Convention DMS](#8-naming-convention-dms)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Overview Proses Upload DMS

Proses upload DMS terdiri dari 5 langkah utama:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  1. Rename File │───▶│ 2. Upload ke    │───▶│ 3. Tunggu       │───▶│ 4. Verifikasi   │───▶│ 5. Cek di SAP   │
│  (DMS Tools)    │    │ File Browser    │    │ Proses Otomatis │    │ di ECM          │    │ DMS             │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Aplikasi yang Digunakan

| Aplikasi | URL | Fungsi |
|----------|-----|--------|
| **DMS Tools (ZDMS)** | http://192.168.254.168:5005 | Rename file sesuai naming convention DMS |
| **File Browser** | http://192.168.254.161:8084 | Upload file ke folder yang sesuai |
| **ECM System** | SAP BSP ZBSP_ECM_APP | Verifikasi status DMS |

---

## 2. Persiapan: Siapkan File dengan Nama yang Benar

### Sebelum Memulai

Pastikan Anda sudah memiliki:

- [ ] File drawing yang akan di-upload (format: PDF, DWG, dll)
- [ ] Nomor material yang terkait dengan ECR
- [ ] Mengetahui kategori dokumen (DRW/DBX/DMT)
- [ ] Mengetahui jenis dokumen (BOM, dll)

### Informasi yang Dibutuhkan

| Informasi | Sumber | Contoh |
|-----------|--------|--------|
| **Material Number** | Dari ECR atau SAP | 30012282 |
| **Material Description** | Dari SAP atau ECR | BANDSIDE RAILS 8' FOG |
| **DMS Type** | Sesuai kategori ECR | DRW (Drawing Wood) |
| **Document Type** | Jenis dokumen | BOM (Bill of Materials) |
| **Plant** | Lokasi produksi | 2000, 3000 |

---

## 3. Langkah 1: Rename File menggunakan DMS Tools

### 3.1 Buka DMS Tools

1. Buka browser, akses: **http://192.168.254.168:5005**
2. Anda akan melihat interface **ZDMS Engineering**

### 3.2 Pilih Tipe Dokumen

Di panel kiri **"TIPE DOKUMEN"**:

1. **DMS TYPE**: Pilih tipe dokumen
   - DRW — Wood (Drawing Wood)
   - DBX — Box (Drawing Box)
   - DMT — Metal (Drawing Metal)

2. **DOCUMENT TYPE**: Pilih jenis dokumen
   - BOM — Bill of Materials
   - Sesuaikan dengan kebutuhan

### 3.3 Upload File Sumber

1. Di panel kiri **"FILE NUMBER 1"**:
   - Klik area **"Klik atau drag file sumber"**
   - Atau **drag & drop** file dari komputer Anda
2. File akan muncul di daftar di bawahnya

### 3.4 Cari Material

Di panel tengah **"PILIH MATERIAL"**:

1. Ketik **nama material** atau **nomor material** di kolom pencarian
   - Contoh: `BANDSIDE RAILS 8' FOG` atau `30012282`
2. Klik tombol **"Cari"** 🔍
3. **Filter opsional** (jika hasil terlalu banyak):
   - **Plant**: Pilih plant tertentu (2000, 3000) atau "Semua Plant"
   - **Type**: Pilih "Finish Goods", "Semi Finish", atau "HALM"
4. Hasil pencarian akan muncul di bawah

### 3.5 Pilih Material

1. Klik pada material yang sesuai di hasil pencarian
2. Material akan masuk ke **"KERANJANG"** di bagian bawah
3. Pastikan material yang dipilih benar (cek nomor dan deskripsi)

### 3.6 Preview dan Download

Di panel kanan **"GENERATE"**:

1. Klik tombol **"Preview"** 👁️ untuk melihat nama file hasil rename
2. Cek **"PREVIEW OUTPUT"** di bawahnya:
   ```
   DRW_30012282_51871966001 BANDSIDE RAILS 8' FOG.DRW.PDF
   ```
3. Jika sudah benar, klik tombol **"Download"** ⬇️
4. File akan ter-download dengan nama yang sudah sesuai format DMS

### 3.7 Format Nama File

Format yang dihasilkan:
```
[DMS_TYPE]_[MATNR]_[DESC]_[DOC_TYPE].[EXT]
```

Contoh:
```
DRW_30012282_51871966001 BANDSIDE RAILS 8' FOG.DRW.PDF
│   │          │                                    │   │
│   │          │                                    │   └─ Extension asli
│   │          │                                    └───── Document Type
│   │          └────────────────────────────────────── Deskripsi Material
│   └────────────────────────────────────────────────── Nomor Material
└────────────────────────────────────────────────────── DMS Type
```

---

## 4. Langkah 2: Upload File ke File Browser

### 4.1 Buka File Browser

1. Buka browser baru (atau tab baru), akses: **http://192.168.254.161:8084**
2. Login jika diminta

### 4.2 Navigasi ke Folder yang Sesuai

1. Di **breadcrumb navigation** di atas, navigasi ke folder material yang sesuai
2. Struktur folder:
   ```
   Home > [Kategori] > [Material Name] > CAD
   ```
3. Contoh:
   ```
   Home > 02. POOLTABLE > BANKSIDE 8' > CAD
   ```

### 4.3 Upload File

1. Klik icon **Upload** (panah ke atas) di pojok kanan atas
2. Atau **drag & drop** file dari komputer ke area file browser
3. Pilih file yang sudah di-rename dari DMS Tools
4. Tunggu hingga upload selesai

### 4.4 Verifikasi Upload

Pastikan file sudah muncul di daftar dengan:
- ✅ Nama file sesuai format DMS
- ✅ Ukuran file benar
- ✅ Timestamp menunjukkan waktu upload terbaru

---

## 5. Langkah 3: Tunggu Proses Otomatis

### 5.1 Apa yang Terjadi Secara Otomatis

Setelah file di-upload ke File Browser, sistem akan:

1. **Watcher** mendeteksi file baru
2. **Converter** memproses file (jika perlu konversi format)
3. **Mover** memindahkan file ke folder staging SAP
4. **SAP Upload** mengupload file ke DMS via BAPI

### 5.2 Waktu Proses

| Tahap | Estimasi Waktu |
|-------|---------------|
| Deteksi file | ~1-2 menit |
| Konversi format | ~2-5 menit |
| Upload ke SAP | ~1-3 menit |
| **Total** | **~5-10 menit** |

### 5.3 Monitoring Proses

- Cek **LOG** di DMS Tools untuk melihat status proses
- Cek File Browser untuk memastikan file sudah dipindahkan

---

## 6. Langkah 4: Verifikasi DMS di ECM

### 6.1 Buka Halaman Drafter di ECM

1. Login ke **ECM System** (ZBSP_ECM_APP)
2. Masuk ke halaman **Drafter**

### 6.2 Cek Status DMS

1. Cari ECR yang terkait dengan material yang di-upload
2. Perhatikan kolom **"DMS"** pada tabel ECR

### 6.3 Indikator Status DMS

| Status | Indikator | Arti |
|--------|-----------|------|
| **Menunggu DMS** | ⏳ Abu-abu | DMS belum terdeteksi, masih dalam proses |
| **DMS Terdeteksi** | ✅ Hijau + Kode DMS | DMS sudah berhasil di-upload |

### 6.4 Klik Kode DMS

1. Jika status sudah **hijau** dengan kode DMS (contoh: `DRW/51871966001`)
2. **Klik kode DMS** tersebut
3. Anda akan diarahkan ke halaman detail DMS di SAP

---

## 7. Langkah 5: Cek Dokumen di SAP DMS

### 7.1 Via Kode DMS di ECM

1. Klik kode DMS di halaman Drafter
2. Sistem akan membuka detail dokumen DMS

### 7.2 Via SAP Transaction

1. Buka SAP GUI
2. Jalankan transaction **CV03N** (Display Document)
3. Masukkan:
   - **Document Type**: DRW/DBX/DMT
   - **Document Number**: Nomor DMS dari ECM
4. Klik **Enter**

### 7.3 Verifikasi di DMS

Pastikan:
- [ ] Dokumen ter-upload dengan benar
- [ ] Status DMS sesuai (IA = In Work, AP = Approved)
- [ ] File attachment ada dan bisa dibuka
- [ ] Material link terhubung dengan benar

---

## 8. Naming Convention DMS

### 8.1 Format Standar

```
[DMS_TYPE]_[MATNR]_[DESCRIPTION]_[DOC_TYPE].[EXT]
```

### 8.2 Komponen Nama

| Komponen | Panjang | Contoh | Keterangan |
|----------|---------|--------|------------|
| DMS Type | 3 char | DRW | Tipe dokumen DMS |
| MATNR | 8 digit | 30012282 | Nomor material SAP |
| Description | Variable | BANDSIDE RAILS 8' FOG | Deskripsi material |
| DOC Type | 3 char | BOM | Jenis dokumen |
| Extension | 3-4 char | PDF, DWG | Format file |

### 8.3 Contoh Nama File

```
DRW_30012282_51871966001 BANDSIDE RAILS 8' FOG.DRW.PDF
DBX_30013453_51871966002 BANDSIDE RAILS 8' ONYX.DBX.DWG
DMT_30024567_51871966003 METAL FRAME 6FT.DMT.PDF
```

### 8.4 Aturan Penamaan

| Aturan | Keterangan |
|--------|------------|
| **Spasi** | Gunakan spasi (bukan underscore) untuk deskripsi |
| **Karakter** | Hindari karakter khusus: `\ / : * ? " < > |` |
| **Case** | Gunakan UPPERCASE untuk tipe dan nomor |
| **Deskripsi** | Boleh mixed case, sesuai material master |

---

## 9. Troubleshooting

### Q: File tidak muncul di DMS Tools saat di-upload?

**A:** 
- Pastikan format file didukung (PDF, DWG, DXF, dll)
- Cek ukuran file (maksimal biasanya 100MB)
- Coba drag & drop dari folder lokal, bukan dari network drive

### Q: Preview menunjukkan nama file yang salah?

**A:**
- Pastikan **DMS Type** dan **Document Type** sudah dipilih dengan benar
- Pastikan **material** yang dipilih di keranjang sudah sesuai
- Klik **Preview** ulang untuk refresh

### Q: File sudah di-upload ke File Browser, tapi DMS tidak muncul di ECM?

**A:**
- Tunggu **10-15 menit** untuk proses otomatis
- Cek **LOG** di DMS Tools untuk melihat error
- Pastikan file di-upload ke **folder yang benar** (sesuai material)
- Pastikan **nama file** sesuai format DMS

### Q: Status DMS tetap "Menunggu DMS" setelah 15 menit?

**A:**
- Cek apakah file sudah dipindahkan dari folder upload (tanda proses selesai)
- Cek folder staging di SAP: `/mnt/data/files/sap-docs/dms-staging/`
- Hubungi admin sistem jika file tidak terproses

### Q: DMS muncul tapi status salah (bukan "In Work")?

**A:**
- Status DMS harus **"IA" (In Work)** agar bisa di-submit dari ECM
- Jika status berbeda, hubungi admin untuk update status DMS

### Q: Saya salah upload file, bagaimana cara menghapus?

**A:**
- Hapus file dari **File Browser** sebelum diproses sistem
- Jika sudah ter-upload ke DMS, hubungi admin untuk delete di SAP

### Q: Folder material tidak ditemukan di File Browser?

**A:**
- Hubungi admin untuk membuat folder baru sesuai material
- Struktur folder: `[Kategori] > [Material Name] > CAD`

---

## Lampiran

### A. URL Aplikasi

| Aplikasi | URL | Keterangan |
|----------|-----|------------|
| DMS Tools | http://192.168.254.168:5005 | Rename file |
| File Browser | http://192.168.254.161:8084 | Upload file |
| ECM System | SAP BSP ZBSP_ECM_APP | Verifikasi DMS |

### B. DMS Type Code

| Code | Nama | Kegunaan |
|------|------|----------|
| DRW | Drawing Wood | Drawing produk kayu |
| DBX | Drawing Box | Drawing packaging/box |
| DMT | Drawing Metal | Drawing produk metal |

### C. Document Type Code

| Code | Nama | Kegunaan |
|------|------|----------|
| BOM | Bill of Materials | Daftar material |
| SPK | Surat Perintah Kerja | Instruksi produksi |
| PKD | Produk Kustom Design | Design kustom |

### D. Status DMS

| Status | Code | Keterangan |
|--------|------|------------|
| In Work | IA | Dokumen dalam pengerjaan |
| Released | FR | Dokumen sudah di-release |
| Approved | AP | Dokumen sudah disetujui |

### E. Alur Proses Lengkap

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              ALUR UPLOAD DMS                                        │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐ │
│  │  Siapkan │────▶│  Rename  │────▶│  Upload  │────▶│  Tunggu  │────▶│Verifikasi│ │
│  │  File    │     │  di ZDMS │     │  di FB   │     │  Proses  │     │  di ECM  │ │
│  └──────────┘     └──────────┘     └──────────┘     └──────────┘     └──────────┘ │
│       │                │                │                │                │         │
│       ▼                ▼                ▼                ▼                ▼         │
│  File asli       File renamed      File uploaded     Auto-process     DMS ready    │
│  (PDF/DWG)       (format DMS)      ke folder         oleh system      di SAP       │
│                                    material                                        │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

*Dokumen ini dibuat berdasarkan sistem DMS Tools (ZDMS) dan proses upload DMS di PT. Kayu Mebel Indonesia.*
*Untuk pertanyaan lebih lanjut, hubungi tim IT atau admin sistem.*
