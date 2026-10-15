# SAP BSP Engineering Handover — Engineering Change Management (ECM)
## Khusus Partner AI Antigravity (Baseline: V14_i)

Dokumen ini adalah **panduan arsitektur lengkap, pemetaan alur bisnis, katalog database, dan field lessons** untuk proyek **Engineering Change Management (ECM)** di lingkungan SAP S/4HANA PT. Kayu Mebel Indonesia (KMI).

---

## 1. Identitas Lingkungan & Spesifikasi Sistem

| Komponen | Spesifikasi / Nilai | Keterangan |
|---|---|---|
| **SAP System** | SAP S/4HANA 1809 On-Premise | SAP_BASIS 753 SP03 / S4CORE 103 SP03 |
| **Client** | `300` (Production) / `200` (Testing) | Selalu perhatikan client saat login/test |
| **Backend URL** | `http://kmiprd.kmi.com:8001/sap(bD1lbiZjPTMwMA==)/bc/bsp/sap/zecm_bsp/` | Akses langsung intranet |
| **Reverse Proxy** | `https://releasepo.kayumebel.net/` (srv167) | Server 167 murni reverse proxy Nginx |
| **Server File** | `srv168` (192.168.254.168) | **Rumah utama file project**. Akses via WinSCP/Samba |
| **Aturan Mutlak** | **DILARANG KERAS upload/SCP file project SAP ke server 167!** | Server 167 bukan tempat file SAP BSP |
| **Editor SE80** | SAP GUI SE80 | Copy-paste kode dari folder lokal ke SE80 lalu Activate |

---

## 2. Latar Belakang & Visi Bisnis ECM KMI

Sebelum modul ECM dibangun, revisi drawing kayu, perakitan, dan hardware sering dilakukan secara liar di lantai produksi (komunikasi verbal, catatan kertas di kardus komponen). Akibatnya:
1. Drawing di produksi berbeda dengan master data di SAP.
2. Bill of Material (BOM) tidak ter-update sehingga costing purchasing salah beli bahan.
3. Kualitas barang retur karena perakitan memakai revisi kadaluarsa.

**Visi "Gatekeeper Approach":**
Semua perubahan gambar teknik dan spesifikasi produk **WAJIB** melalui pintu ECM. Tidak ada drawing yang boleh dicetak dan turun ke mesin produksi tanpa status ECO yang sah dan persetujuan lengkap.

---

## 3. Matriks Peran (Roles) & Tanggung Jawab

Aplikasi ECM membagi alur kerja ke dalam beberapa peran berbasis hak akses (`ZECM_USER`):

```
[Requester]                [Approver (Head R&D)]            [Admin ECR]                       [Drafter]
   │                              │                              │                               │
   │─── Buat Request (IREQ) ─────>│                              │                               │
   │    Status: REQ               │─── Review & Approve ────────>│                               │
   │                                   Status: APPR              │─── Assign Drafter (ECO) ─────>│
   │                                                             │    + Input Target PO & Date   │── Upload Revisi Drawing (DMS)
   │                                                             │    Status: INWK               │── Upload BOM / Skip BOM
   │                                                             │                               │── Ajukan Inspeksi (INSP)
   │                                                             │                               │
                                                                 │<── Approval Akhir ECO ────────│
                                                                 │    Status: CLSD
```

### Rincian Halaman per Role:
1. **Requester (`requester_list.htm`)**:
   - Mengajukan permohonan perubahan baru (**Pre-ECR / IREQ**).
   - Input: Material FG, Kategori (`DRW` Wood, `DBX` Box, `DMT` Metal), Prioritas (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`), Estimasi Dampak Biaya (Rp), **Departemen** (`Produksi`, `QC`, `Purchasing`, `Sales`, `Drafter`, `Owner`), **Alasan** (`Koreksi Cacat`, `Reduksi Biaya`, `Perbaikan Desain`, `Perubahan Bahan`, `Req. Buyer`, `Kepatuhan Standar Industri`), Deskripsi, dan File Attachment (s.d 5 file lampiran).
2. **Approver / Head R&D (`approver_list.htm`)**:
   - Menyetujui atau menolak permohonan IREQ (`REQ` $\rightarrow$ `APPR` atau `REJC`).
   - Sesuai keputusan arsitektur V14_e: **Approval murni tanpa beban input PO/Date**.
3. **Admin ECR (`admin_dashboard.htm`, `admin_req_review.htm`)**:
   - **Gatekeeper & Koordinator Utama**:
     - Membuka tiket `APPR`, menugaskan Drafter PIC, dan **wajib menginput Implementation Tracking** (`impl_po`, `impl_date`, `impl_reason`). Tiket IREQ otomatis ditutup (`ECO`) dan lahir tiket `INWK` (ECO Aktif).
     - Menyetujui pengerjaan ECR dari Drafter (`CRTD` $\rightarrow$ `INWK`).
     - Mengawasi analitik dashboard (grafik tren, counter status).
     - **Mencetak Laporan PDF per Panel**: Panel Request Masuk, Panel Antrian Approval, dan Panel Daftar ECR.
4. **Drafter (`drafter_list.htm`)**:
   - PIC pengerjaan revisi teknis.
   - Mengunggah nomor dokumen DMS SAP (link drawing).
   - **BOM Gate**: Mengunggah PDF revisi BOM atau menekan tombol **"Skip BOM (Tidak Ada Perubahan)"** jika perubahan hanya pada tampilan/grafis.
   - Mengirim permohonan ke tahap inspeksi produksi (`INSP`).

---

## 4. Siklus Hidup Dokumen (State Machine)

### A. Alur Pre-ECR (Tabel `ZECM_IREQ`):
- **`REQ` (Requested)**: Baru dibuat oleh Requester, menunggu tinjauan Approver Head R&D.
- **`APPR` (Approved)**: Disetujui Head R&D, masuk ke antrian Admin Review untuk penugasan Drafter.
- **`REJC` (Rejected)**: Ditolak oleh Head R&D dengan alasan penolakan.
- **`ECO` (Assigned)**: Admin telah menugaskan Drafter dan mengisi Target PO. IREQ selesai dan bertransformasi menjadi ECO aktif.

### B. Alur ECR / ECO (Tabel `ZECM_REQ`):
- **`CRTD` (Created / Draft ECR)**: Dibuat langsung oleh Drafter atau Admin tanpa jalur IREQ, menunggu approval Admin.
- **`INWK` (In Work / ECO Aktif)**: Sedang dikerjakan revisi drawing-nya oleh Drafter.
- **`BMAP` (BOM Approved / Ready)**: Revisi BOM telah disetujui atau di-skip oleh Drafter (`bom_check = 'A'`).
- **`INSP` (Inspection)**: Pengerjaan selesai dan sampel perbaikan sedang diuji di lantai produksi/QC.
- **`CLSD` (Closed)**: ECO selesai tuntas dan diterapkan permanen.
- **`REJC` (Rejected)**: Ditolak oleh Admin saat tahap draft.

---

## 5. Struktur Database (Kamus Data SAP `ZECM_*`)

### 1. `ZECM_REQ` (Tabel Master ECR / ECO)
* **`MANDT`**: Client SAP (`300`/`200`).
* **`ECR_NO`**: Nomor ECR/ECO (NUMC 10, format 10 digit leading zeros).
* **`TITLE`**: Judul perubahan material.
* **`MATNR_FG`**: Nomor material Finish Goods SAP (NUMC 18).
* **`KATEGORI`**: Kategori perubahan (`DRW`, `DBX`, `DMT`).
* **`PRIORITY`**: Prioritas (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).
* **`STATUS`**: Status aktif (`CRTD`, `INWK`, `BMAP`, `INSP`, `CLSD`, `REJC`).
* **`DRAFTER`**: User ID Drafter PIC (`ZECM_USER-ZECM_USER_ID`).
* **`REQUESTER`**: User ID pemohon awal.
* **`DMS_DOC_NUMBER`**: Nomor dokumen DMS SAP (`DRAW-DOKNR`).
* **`BOM_CHECK`**: Status BOM Gate (`'A'` = Ready/Skipped, `'P'` = Pending Upload).
* **`BOM_NOTES`**: Catatan revisi BOM (mis: *"BOM Skipped - Tidak ada perubahan BOM"*).
* **`IMPL_PO`**: Target Rilis PO Lapangan (wajib diisi Admin).
* **`IMPL_DATE`**: Target Tanggal Implementasi Lapangan (YYYYMMDD).
* **`IMPL_REASON`**: Alasan penetapan target implementasi lapangan.
* **`CREATED_DATE`** & **`CREATED_TIME`**: Timestamp pembuatan.

### 2. `ZECM_IREQ` (Tabel Pre-ECR Request)
* **`MANDT`**: Client.
* **`IREQ_ID`**: ID request internal (CHAR 10).
* **`TITLE`**: Judul request.
* **`MATNR_FG`**: Material Finish Goods.
* **`ZDEPT`**: Departemen pemohon (`Produksi`, `QC`, `Purchasing`, `Sales`, `Drafter`, `Owner`).
* **`ZREASON`**: Alasan perubahan (`Koreksi Cacat`, `Reduksi Biaya`, `Perbaikan Desain`, `Perubahan Bahan`, `Req. Buyer`, `Kepatuhan Standar Industri`).
* **`COST_ESTIMATE`**: Estimasi nilai rupiah dampak perubahan.
* **`STATUS`**: Status (`REQ`, `APPR`, `REJC`, `ECO`).
* **`APPROVER`** & **`APPROVAL_DATE`**: Jejak audit Head R&D.
* **`REJECT_REASON`**: Alasan jika ditolak.

### 3. `ZECM_ATTACH` (Tabel Multi-Attachment)
* Menyimpan dokumen pendukung foto cacat, PDF referensi buyer, atau revisi BOM.
* Disimpan dalam bentuk RAW BLOB / XSTRING.

### 4. `ZECM_LOG` (Tabel Audit Trail)
* Mencatat setiap transisi status (`old_status` $\rightarrow$ `new_status`), timestamp, dan user eksekutor.

---

## 6. Field Lessons & Pedoman Koding BSP KMI (Wajib Patuhi)

### A. Quirks SweetAlert2 vs Modal Tailwind (`z-index`)
* **Problem**: Modal detail ECR (`#detailModal`) menggunakan kelas Tailwind `z-[9999]`. SweetAlert2 standarnya menggunakan `z-index: 1060`, sehingga popup konfirmasi muncul **di belakang modal** (layar menggelap tapi tombol konfirmasi tertutup).
* **Solusi Mutlak**:
  1. Pasang CSS override di `<style>`:
     ```css
     .swal2-container { z-index: 100000 !important; }
     ```
  2. Gunakan target `document.body` pada SweetAlert:
     ```javascript
     Swal.fire({
       target: document.body,
       customClass: { popup: 'rounded-xl shadow-lg', container: '!z-[100000]' },
       ...
     });
     ```

### B. Injeksi Pesan Server (`GV_MESSAGE`) ke JavaScript
* **Problem**: Menginjeksi langsung variabel ABAP ke string JS seperti `text: '<%= GV_MESSAGE %>'` rawan memicu `SyntaxError: Invalid or unexpected token` jika pesan mengandung spasi URL, newline, atau tanda kutip. Error ini akan mematikan parser browser dan melumpuhkan fungsi-fungsi JS di bawahnya (mis. `cetakPanel is not defined`).
* **Solusi Mutlak**:
  Gunakan atribut data HTML untuk membungkus pesan:
  ```html
  <% IF GV_ICON IS NOT INITIAL AND GV_MESSAGE IS NOT INITIAL. %>
  <div id="swalServerMsg" data-icon="<%= GV_ICON %>" data-msg="<%= GV_MESSAGE %>" style="display:none;"></div>
  <script>
    (function() {
      var el = document.getElementById('swalServerMsg');
      if (el && typeof Swal !== 'undefined') {
        Swal.fire({ icon: el.getAttribute('data-icon'), text: el.getAttribute('data-msg') });
      }
    })();
  </script>
  <% ENDIF. %>
  ```

### C. Pemanggilan Form Terpusat (`actionForm`)
* Pada halaman dengan banyak baris tabel dan modal dinamis (seperti `drafter_list.htm`), hindari membuat tag `<form>` bertumpuk di dalam `<tr>` atau modal.
* **Gunakan Pola Hidden `actionForm` Terpusat**:
  ```html
  <form id="actionForm" method="post" style="display:none;">
    <input type="hidden" name="action" id="actionType">
    <input type="hidden" name="ecr" id="actionEcrNo">
  </form>
  ```
  Lalu panggil via JS:
  ```javascript
  document.getElementById('actionType').value = 'skip_bom';
  document.getElementById('actionEcrNo').value = ecrNo;
  document.getElementById('actionForm').submit();
  ```

### D. Konversi Field NUMC & Leading Zeros
* Material dan ECR No bertipe NUMC dengan padding nol di SAP (misal: `000000000030013746`).
* **Sebelum SELECT/JOIN**: Selalu jalankan `CONVERSION_EXIT_ALPHA_INPUT`.
* **Sebelum Menampilkan ke User**: Selalu bersihkan dengan `CONVERSION_EXIT_ALPHA_OUTPUT` atau `SHIFT lv_mat LEFT DELETING LEADING '0'`.

### E. Fitur Cetak Laporan PDF per Panel (`admin_print_ecr.htm`)
* Menggunakan parameter URL: `admin_print_ecr.htm?type=ireq|approval|ecr`.
* Layout menggunakan CSS `@media print` dengan ukuran A4 landscape dan `@page { margin: 15mm; size: A4 landscape; }`.
* Tombol cetak berada di masing-masing header panel di `admin_dashboard.htm`:
  - `cetakPanel('ireq')`: Panel Request Masuk.
  - `cetakPanel('approval')`: Panel Antrian Approval.
  - `cetakPanel('ecr')`: Panel Daftar ECR.

---

## 7. Lokasi File & Direktori Kerja

* **Direktori Kerja Antigravity**:  
  📁 **`\files\sap-docs\ecm\ECM (Antigravity)\`**
* **Seluruh Kodingan BSP Versi Terakhir Siap Pakai**:  
  📁 **`\files\sap-docs\ecm\ECM (Antigravity)\bsp-app\`** (Salinan identik dari `v14_i_panel_print_split`)
* **Arsip Pengetahuan & Dokumentasi Historis Lengkap**:  
  📁 **`\files\sap-docs\ecm\ECM (Antigravity)\docs\`**  
  - 📄 `docs/ECM_PROJECT_INSIGHT.md` (Wajib: filosofi bisnis & aturan pabrik)
  - 📄 `docs/ECM_ROADMAP.md` (Peta fitur makro & roadmap modul)
  - 📄 `docs/tutorial-upload-dms.md` & `docs/tutorial-drafter.md` (Panduan teknis DMS & Drafter)
  - 📄 `docs/CHANGELOG.md` & `docs/VERSIONS.md` (Changelog V01 s/d V14_i)
  - 📄 `docs/insight-dms-cross-contamination.md` (Studi kasus pencegahan bug DMS)
  - 📄 `docs/communication-guidelines.md` (Gaya kerja & komunikasi Yogi)
* **Master Changelog di Root**:  
  📄 **`\files\sap-docs\ecm\CHANGELOG.md`**  
  📄 **`\files\sap-docs\ecm\VERSIONS.md`**  
  📄 **`\files\sap-docs\ecm\INDEX.md`**
