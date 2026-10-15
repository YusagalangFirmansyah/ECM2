# ECM V14 Design Notes: Implementation Tracking (PO and Date)

## 1. Latar Belakang dan Tujuan
Berdasarkan diskusi dengan Kepala R&D (Pak Eris), terdapat kebutuhan untuk mencatat rencana implementasi dari sebuah Engineering Change. 
Tujuan utamanya adalah sebagai **bukti catatan historis** (bukan sekadar instruksi ke Produksi/Purchasing) mengenai kapan suatu perubahan memungkinkan untuk dieksekusi berdasarkan kondisi di lapangan.

## 2. Struktur Database (SE11)
Akan ditambahkan 3 field baru pada tabel **ZECM_IREQ** (Pre-Request) dan **ZECM_REQ** (ECR). Kedua tabel harus memiliki field yang sama karena data diinput di fase IREQ dan harus diwariskan/dibawa saat menjadi ECR.

| Field Name | Type | Length | Keterangan |
| :--- | :--- | :--- | :--- |
| IMPL_PO | CHAR | 50 | Keterangan PO (misal: Next PO, Berlaku PO 45000123). |
| IMPL_DATE | DATS | 8 | Tanggal janji/estimasi dari R&D perubahan bisa berjalan. |
| IMPL_REASON | CHAR | 255 | Alasan kenapa dipilih tanggal/PO tersebut (kondisi lapangan). |

## 3. Aturan Bisnis dan Workflow
1. **Cakupan (Scope):** Hanya diterapkan pada ECR Engineering / Drawing (CHANGE_SCOPE = 'DRWG'). ECR Routing tidak terdampak fitur ini.
2. **Titik Input (Data Entry):** 
   - Dilakukan oleh **Kepala R&D (Approver)**.
   - Dilakukan **pada saat menyetujui IREQ** (Status REQ -> APPR).
3. **Validasi (Mandatory):** Ke-3 field tersebut bersifat **Wajib Isi (Mandatory)** di sisi frontend saat Kepala R&D melakukan Approve IREQ.
4. **Alur Pewarisan Data (Inheritance):**
   - Saat Admin ECR menekan "Buat ECO" (Assign Drafter), sistem **WAJIB** memindahkan nilai IMPL_PO, IMPL_DATE, dan IMPL_REASON dari ZECM_IREQ ke record baru di ZECM_REQ.

## 4. UI/UX Changes (Frontend)
1. **Halaman Approver (approver_list.htm):**
   - Modifikasi tombol Approve pada IREQ.
   - Menambahkan Modal/Pop-up Approval yang berisi form input untuk IMPL_PO, IMPL_DATE (Datepicker), dan IMPL_REASON (Textarea).
2. **Halaman Visibilitas (Admin, Requester, Drafter, Viewer):**
   - Menambahkan tampilan ke-3 field ini di bagian expandable row (Detail Request / Detail ECR).
3. **Cetak PDF (admin_print_ecr dan requester_print):**
   - Memasukkan ke-3 field informasi ini ke dalam layout cetakan dokumen PDF resmi.
