# Tutorial ECM — Role Drafter

**Sistem:** ECM BSP (ZBSP_ECM_APP)
**Target User:** Drafter / Engineering Staff
**Terakhir Update:** 16 Juli 2026

---

## Daftar Isi

1. [Apa itu Role Drafter?](#1-apa-itu-role-drafter)
2. [Halaman Utama Drafter](#2-halaman-utama-drafter)
3. [Membuat ECR Baru](#3-membuat-ecr-baru)
4. [Memeriksa DMS yang Masuk](#4-memeriksa-dms-yang-masuk)
5. [Submit ECR ke Inspection](#5-submit-ecr-ke-inspection)
6. [Menolak ECR (Reject)](#6-menolak-ecr-reject)
7. [Membatalkan ECR (Cancel)](#7-membatalkan-ecr-cancel)
8. [Melihat Detail ECR & Audit Trail](#8-melihat-detail-ecr--audit-trail)
9. [Status ECR & Alur Proses](#9-status-ecr--alur-proses)
10. [FAQ & Troubleshooting](#10-faq--troubleshooting)

---

## 1. Apa itu Role Drafter?

Drafter adalah user yang bertanggung jawab untuk:

- **Membuat ECR** (Engineering Change Request) — permintaan perubahan engineering
- **Menyiapkan dokumen DMS** — upload drawing/revisi ke sistem DMS
- **Submit ECR ke Inspection** — setelah dokumen DMS siap, drafter submit untuk review approver

### Alur Singkat

```
Drafter buat ECR → Admin approve → ECR masuk "In Work" → Drafter upload DMS → Drafter submit → Inspection
```

---

## 2. Halaman Utama Drafter

Setelah login sebagai Drafter, Anda akan melihat halaman utama dengan komponen berikut:

### 2.1 Status Cards

Di bagian atas terdapat 4 kartu status yang menunjukkan jumlah ECR berdasarkan status:

| Kartu | Status | Keterangan |
|-------|--------|------------|
| **ECR Draft** | CRTD | ECR yang baru dibuat, menunggu approval admin |
| **Dalam Proses** | INWK | ECR yang sudah di-approve admin, siap dikerjakan |
| **Inspection** | INSP | ECR yang sudah di-submit, menunggu review approver |
| **Ditolak** | REJC | ECR yang ditolak (oleh admin atau drafter sendiri) |

### 2.2 Filter & View

- **Filter Tanggal**: Batasi data berdasarkan rentang tanggal
- **View Mode**: Toggle antara "ECR Saya" (hanya ECR yang Anda buat) atau "Semua ECR"
- **Status Filter**: Filter berdasarkan status tertentu (Draft, In Work, Inspection, dll)

### 2.3 Tombol Aksi

- **+ ECR Baru**: Membuka form untuk membuat ECR baru
- **DMS List**: Melihat daftar dokumen DMS yang terkait

---

## 3. Membuat ECR Baru

### Langkah-langkah:

1. Klik tombol **"+ ECR Baru"** di pojok kanan atas
2. Form modal akan terbuka dengan field-field berikut:

### 3.1 Field yang Wajib Diisi

| Field | Keterangan | Contoh |
|-------|------------|--------|
| **Material** | Pilih material yang akan diubah | Klik "Cari" → pilih dari hasil |
| **Judul Perubahan** | Judul singkat perubahan | "Revisi dimensi kaki kursi" |
| **Kategori** | Tipe dokumen drawing | DRW (Drawing Wood), DBX (Drawing Box), DMT (Drawing Metal) |
| **Prioritas** | Tingkat urgensi | Critical, High, Medium, Low |
| **Deskripsi** | Detail perubahan yang diminta | "Ubah dimensi A dari 100mm ke 120mm" |
| **Departemen** | Departemen yang meminta | "Production", "Quality" |
| **Alasan** | Alasan perubahan | "Customer request" |

### 3.2 Cara Memilih Material

1. Ketik nama material atau ID di kolom pencarian
2. Klik tombol **"Cari"**
3. Daftar material akan muncul (FERT, HALB, HALM)
4. Klik **"+ Pilih"** pada material yang diinginkan
5. Material bisa dipilih lebih dari satu (multi-select)

### 3.3 Setelah Submit

- ECR akan dibuat dengan status **CRTD (Draft)**
- Setiap material yang dipilih akan menjadi ECR terpisah
- ECR menunggu **approval dari Admin** sebelum bisa dikerjakan

---

## 4. Memeriksa DMS yang Masuk

Setelah Admin approve ECR, status berubah menjadi **INWK (In Work)**. Pada tahap ini, Anda perlu memeriksa apakah dokumen DMS sudah masuk.

### 4.1 Cara Cek DMS

1. Di halaman utama, cari ECR dengan status **"Dalam Proses"** (INWK)
2. Perhatikan kolom **"DMS"** pada tabel ECR
3. Sistem akan otomatis mendeteksi DMS berdasarkan:
   - **Material** yang terkait dengan ECR
   - **Kategori** dokumen (DRW/DBX/DMT)
   - **Status DMS** harus **"IA" (In Work)**

### 4.2 Indikator DMS

| Indikator | Arti |
|-----------|------|
| ✅ **DMS Terdeteksi** | Dokumen DMS sudah ada dengan status "In Work" |
| ❌ **Belum Ada DMS** | Dokumen belum di-upload atau status belum "In Work" |

### 4.3 Klik DMS List

- Klik tombol **"DMS List"** di header untuk melihat daftar semua DMS
- Filter berdasarkan status: In Work (IA), Approved (AP), dll
- Klik nomor DMS untuk melihat detail dokumen

### 4.4 Catatan Penting

- **DMS harus ada** sebelum Anda bisa submit ECR ke Inspection
- **Status DMS harus "IA" (In Work)** — jika status berbeda, ECR tidak bisa di-submit
- Jika DMS belum ada, hubungi tim terkait untuk upload dokumen

---

## 5. Submit ECR ke Inspection

Setelah DMS terdeteksi dengan status "In Work", Anda bisa submit ECR ke Inspection.

### Langkah-langkah:

1. Cari ECR dengan status **"Dalam Proses"** (INWK)
2. Klik tombol **"Submit"** pada ECR yang akan di-submit
3. Konfirmasi dialog akan muncul
4. Klik **"Ya, Submit"** untuk melanjutkan

### Apa yang Terjadi:

1. **DMS berubah status**: IA (In Work) → AP (Approved)
2. **ECR berubah status**: INWK (In Work) → INSP (Inspection)
3. **Nomor DMS** tercatat di ECR (untuk tracking)
4. **Audit log** tercatat otomatis

### Setelah Submit:

- ECR masuk ke status **"Inspection"** (INSP)
- **Approver** akan menerima notifikasi untuk review
- Anda bisa melihat progress di detail ECR

---

## 6. Menolak ECR (Reject)

Jika Anda menemukan masalah dengan ECR yang sudah di-approve admin, Anda bisa menolaknya.

### Langkah-langkah:

1. Cari ECR dengan status **"Dalam Proses"** (INWK)
2. Klik tombol **"Reject"** pada ECR
3. **Isi alasan penolakan** (wajib)
4. Klik **"Submit"** untuk menolak

### Apa yang Terjadi:

- ECR berubah status: **INWK → REJC (Rejected)**
- Alasan penolakan tercatat di sistem
- **Requester** akan menerima notifikasi

---

## 7. Membatalkan ECR (Cancel)

Anda bisa membatalkan ECR yang sedang dalam status "In Work" untuk dikembalikan ke Draft.

### Langkah-langkah:

1. Cari ECR dengan status **"Dalam Proses"** (INWK)
2. Klik tombol **"Cancel"** pada ECR
3. Konfirmasi dialog akan muncul
4. Klik **"Ya, Batalkan"** untuk melanjutkan

### Apa yang Terjadi:

- ECR berubah status: **INWK → CRTD (Draft)**
- ECR kembali ke antrian approval admin
- **Audit log** tercatat otomatis

---

## 8. Melihat Detail ECR & Audit Trail

### 8.1 Melihat Detail ECR

1. Klik pada **nomor ECR** di tabel
2. Modal detail akan terbuka menampilkan:
   - Informasi lengkap ECR (material, judul, kategori, dll)
   - Status saat ini
   - Informasi DMS (jika ada)
   - **Audit Trail** — riwayat semua perubahan status

### 8.2 Membaca Audit Trail

Audit Trail menampilkan kronologi perubahan ECR:

| Aksi | Keterangan |
|------|------------|
| **Created** | ECR pertama kali dibuat |
| **Approved** | Admin menyetujui ECR |
| **Submitted** | Drafter submit ke Inspection |
| **Rejected** | ECR ditolak (oleh admin atau drafter) |
| **Cancelled** | ECR dibatalkan oleh drafter |

Format timestamp: `DD.MM.YYYY HH:MM`

---

## 9. Status ECR & Alur Proses

### 9.1 Diagram Alur

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  Draft  │────▶│In Work  │────▶│Inspection│────▶│ Closed  │
│  (CRTD) │     │ (INWK)  │     │  (INSP)  │     │ (CLSD)  │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
     ▲               │
     │               ▼
     │          ┌─────────┐
     └──────────│Rejected │
                │ (REJC)  │
                └─────────┘
```

### 9.2 Penjelasan Status

| Status | Kode | Siapa yang Ubah | Keterangan |
|--------|------|-----------------|------------|
| **Draft** | CRTD | Drafter / System | ECR baru dibuat, menunggu approval |
| **In Work** | INWK | Admin | Admin approve, drafter mulai kerjakan |
| **Inspection** | INSP | Drafter | Drafter submit, menunggu review approver |
| **Closed** | CLSD | Approver | Approver setujui, ECR selesai |
| **Rejected** | REJC | Admin / Drafter | ECR ditolak |

### 9.3 Aksi yang Bisa Dilakukan Drafter

| Status ECR | Aksi yang Tersedia |
|------------|-------------------|
| CRTD (Draft) | — (menunggu admin approve) |
| INWK (In Work) | Submit, Reject, Cancel |
| INSP (Inspection) | — (menunggu approver review) |
| REJC (Rejected) | — (perlu buat ECR baru) |

---

## 10. FAQ & Troubleshooting

### Q: ECR saya masih status "Draft" padahal sudah lama?

**A:** ECR perlu di-approve oleh Admin terlebih dahulu. Hubungi Admin untuk memproses approval.

### Q: Saya tidak bisa submit ECR, muncul error "DMS belum terdeteksi"?

**A:** Pastikan:
1. Dokumen DMS sudah di-upload ke sistem
2. Status DMS adalah **"In Work" (IA)**
3. Material di DMS sesuai dengan material di ECR
4. Kategori dokumen (DRW/DBX/DMT) sesuai

### Q: Saya salah submit ECR, bagaimana cara membatalkan?

**A:** Jika ECR masih status "Inspection" (INSP), hubungi Approver untuk reject. Jika ECR sudah "Closed" (CLSD), buat ECR baru.

### Q: Bagaimana cara melihat ECR yang sudah saya buat?

**A:** Gunakan toggle **"ECR Saya"** di bagian filter untuk melihat hanya ECR yang Anda buat.

### Q: Saya ingin menolak ECR, tapi tombol "Reject" tidak muncul?

**A:** Tombol Reject hanya muncul untuk ECR dengan status **"In Work" (INWK)**. Jika status berbeda, aksi tidak tersedia.

### Q: Bagaimana cara melihat siapa yang approve ECR saya?

**A:** Klik nomor ECR → lihat **Audit Trail** di bagian bawah detail. Akan terlihat siapa yang approve dan kapan.

---

## Lampiran

### Kategori Dokumen DMS

| Kode | Nama | Keterangan |
|------|------|------------|
| DRW | Drawing Wood | Drawing untuk produk kayu |
| DBX | Drawing Box | Drawing untuk packaging/box |
| DMT | Drawing Metal | Drawing untuk produk metal |

### Prioritas ECR

| Prioritas | Warna | Kapan Digunakan |
|-----------|-------|-----------------|
| Critical | 🔴 Merah | Perubahan mendesak, safety issue |
| High | 🟠 Oranye | Perubahan penting, deadline dekat |
| Medium | 🔵 Biru | Perubahan normal, rutin |
| Low | ⚪ Abu-abu | Perubahan minor, bisa ditunda |

### Field ECR

| Field | Wajib | Keterangan |
|-------|-------|------------|
| Material | ✅ | Material yang akan diubah |
| Judul | ✅ | Judul perubahan |
| Kategori | ✅ | Tipe dokumen (DRW/DBX/DMT) |
| Prioritas | ✅ | Tingkat urgensi |
| Deskripsi | ✅ | Detail perubahan |
| Departemen | ✅ | Departemen yang meminta |
| Alasan | ✅ | Alasan perubahan |
| Cost Estimate | ❌ | Estimasi biaya (opsional) |

---

*Dokumen ini dibuat berdasarkan source code ZBSP_ECM_APP V06_f.*
*Untuk pertanyaan lebih lanjut, hubungi tim IT atau admin sistem.*
