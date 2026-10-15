# CHANGELOG — v14_g_fix_skip_bom (09 September 2026)

## Perbaikan Fitur Skip BOM di Dashboard Drafter

Memperbaiki bug pada fitur *Skip BOM* (Tombol "Lewati / Tidak Ada Perubahan BOM") di modal detail ECR Drafter (`drafter_list.htm` & `drafter_list_event_handler.txt`):

### 1. Masalah yang Ditemukan (Root Cause):
- **Frontend Bug (`drafter_list.htm`)**:
  - Tombol `skipBom()` tidak mengoper parameter `ecr_no`.
  - Fungsi `skipBom` sebelumnya mencoba mengubah `input[name="OnInputProcessing"]` pertama di dokumen secara acak dan men-submit form `bomUploadForm` yang tidak memiliki atribut `action` resmi.
- **Backend Bug (`drafter_list_event_handler.txt`)**:
  - Pada event `skip_bom`, sistem hanya mengubah status ECR menjadi `BMAP`, tetapi **lupa meng-update field `bom_check = 'A'`** (Approved/Ready).
  - Akibatnya, UI modal tetap menganggap BOM belum berstatus approved (karena kondisi tampil form upload adalah `bom_check IS INITIAL OR bom_check = 'R'`), kolom status BOM Gate di tabel tetap tanda strip (`-`), dan tombol "Submit" ke inspeksi tidak pernah muncul.

### 2. Perbaikan yang Diterapkan (Fix):
- **`drafter_list.htm`**:
  - Tombol Skip BOM di modal detail ECR memanggil `skipBom('<%= LS_ECR_DETAIL-ecr_no %>')`.
  - Fungsi `skipBom(ecrNo)` distandarkan menggunakan form action terpusat (`actionForm` dengan `actionType = 'skip_bom'` dan `actionEcrNo = ecrNo`) sama seperti fungsi `cancelUploadBom` dan `submitEcr`.
- **`drafter_list_event_handler.txt`**:
  - Pada blok `ELSEIF lv_action = 'skip_bom'`:
    - Mengupdate `status = 'BMAP'`.
    - **Mengupdate `bom_check = 'A'`** (Ready / Skipped).
    - Menambahkan `bom_notes = 'BOM Skipped - Tidak ada perubahan BOM'`.
    - Mengupdate `changed_date` dan `changed_time`.
    - Mencatat log audit trail `BOM_SKIP` di tabel `ZECM_LOG`.
