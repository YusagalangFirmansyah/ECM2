# ECM Development Guidelines & Project Rules

## 1. Git Automation
- Setiap kali ada modifikasi/penambahan file (kode BSP, dokumentasi, script pendukung), lakukan **auto commit dan auto push ke remote GitHub (origin main) tanpa perlu konfirmasi manual**.
- Format commit message: conventional commit (e.g., eat: ..., ix: ..., docs: ..., efactor: ...).

## 2. Response Structure: Changed Files Checklist
- Pada akhir setiap respons, **selalu berikan daftar lengkap (list) file apa saja yang terkena perubahan** beserta lokasinya (misal file di sp-app/, docs/, dll).

## 3. SAP SE80 Deployment & Copy-Paste Guard
- Karena alur deployment SAP BSP adalah menyalin kode dari folder lokal project ke SAP GUI SE80 secara manual, selalu lakukan pemeriksaan cermat terhadap:
  - Kelengkapan tab SE80 yang perlu di-update untuk halaman bersangkutan (Layout (.htm), Page Attributes, Type Definitions, Event Handler -> OnInitialization, Event Handler -> OnInputProcessing).
  - Jika ada potensi error akibat user lupa meng-copy salah satu file pendukung (misalnya hanya meng-copy .htm tapi lupa meng-copy _oninit.txt atau _type_definitions.txt), atau ada risiko salah paste antar-tab di SE80, **wajib berikan peringatan dan checklist copy-paste SE80 secara eksplisit**.

## 4. Scope Guard: Produksi List Excluded
- File `produksi_list.htm` dan komponen terkait role produksi **BUKAN merupakan bagian dari ekosistem ECM Drawing** dan tidak termasuk dalam lingkup yang dikerjakan.
- **JANGAN pernah memodifikasi, mengikutsertakan, atau menerapkan perubahan pada `produksi_list`**. Fokus fitur cetak dan aliran proses hanya untuk role Requester (`requester_*`), Admin (`admin_*`), dan role terkait ECM Drawing lainnya.

## 5. SAP SE80 JavaScript Formatting & Anti-Truncation Standard
- **Batas Maksimal Panjang Baris (Max 120 Karakter)**: Text editor SAP SE80 memiliki limit buffer per baris (200-255 karakter) dan rentan memotong (*truncate*) atau mengacak *line wrap* kode JavaScript. Oleh karena itu:
  - **DILARANG** menggabungkan banyak statement JavaScript dalam satu baris (misal: `stmt1; stmt2; stmt3;`).
  - Setiap statement wajib berada pada baris tersendiri.
  - Untuk string HTML/URL panjang, wajib dipecah menjadi *multiline concatenation* menggunakan tanda `+`.
- **Pemisahan Penuh ABAP & JavaScript**:
  - Semua variabel SAP backend yang dibutuhkan di frontend wajib dideklarasikan sebagai variabel global window di satu blok `<script>` khusus di bagian paling atas halaman (misal: `window.GV_USER_ID = '<%= GV_USER_ID %>';`).
  - Fungsi-fungsi JavaScript di bawahnya **TIDAK BOLEH** menggunakan tag `<% IF ... %>` atau `<%= ... %>` secara langsung di dalam logika fungsi, melainkan membaca dari `window.GV_*`.
- **Standar Kompatibilitas ES5**:
  - Hindari penulisan *arrow function* `() =>` pada callback sederhana SweetAlert atau DOM listener jika berpotensi membingungkan engine internal SAP BSP; gunakan `function(...) { ... }` standar.
- **Integritas Penutupan Tag `<script>`**:
  - Setiap blok script terpisah (seperti Chart.js dan UI Handler) wajib ditutup dengan `</script>` secara eksplisit sebelum membuka `<script>` baru guna mencegah error *nested script token*.
- **Verifikasi Integritas Penutupan Blok/Callback (`{}` & `()`)**:
  - Semua fungsi callback dan event listener (seperti `window.addEventListener`, `.then(...)`, `.forEach(...)`) wajib memiliki penutup kurung dan titik koma (`});`) yang lengkap sebelum tag `</script>`.
  - Ketidakhadiran `});` akan menyebabkan browser membaca tag `</script>` sebagai token JavaScript, menghasilkan `SyntaxError: Unexpected token '<'` dan membatalkan pendaftaran SELURUH fungsi pada halaman (cascading failure).
- **Integritas Penempatan Modal HTML**:
  - Semua elemen overlay modal (seperti audit trail atau detail popup) wajib berada di dalam tag `<body>` sebelum penutup `</body></html>`, bukan di luar dokumen HTML.

## 6. Cross-Project Validation (Pencegahan Salah Instruksi)
- **Verifikasi Konteks:** Sebelum menulis kode, menjalankan script, atau memodifikasi file, periksa terlebih dahulu apakah instruksi yang diberikan oleh pengguna relevan dengan ekosistem aplikasi **ECM (Engineering Change Management) Drawing** dan BSP *bsp-app*.
- **Peringatan Proaktif:** Jika instruksi tampak tidak berhubungan, menyebutkan nama tabel/file dari project lain, atau secara logika berada di luar lingkup ECM, **BERHENTI**. Jangan langsung mengeksekusi instruksi tersebut.
- **Konfirmasi:** Berikan peringatan kepada pengguna (contoh: *"Instruksi ini sepertinya milik project lain..."*) dan minta konfirmasi eksplisit sebelum melanjutkan pekerjaan.

## 7. UI Refactoring & Feature Preservation Guard
- **Preservasi Fitur Penuh:** Ketika melakukan refactoring antarmuka (UI/UX), penyesuaian tata letak (responsiveness/mobile), maupun restrukturisasi CSS/HTML:
  - **DILARANG KERAS** mengubah, mengurangi, memindahkan tanpa sengaja, atau merusak logika fitur yang sudah berjalan (business logic, event handler, form submission, ID elemen DOM, atribut `name`, pemanggilan fungsi `onclick`/`onsubmit`, serta integrasi backend ABAP).
  - Setiap perubahan tampilan wajib murni menyasar layer styling/presentasi tanpa menimbulkan efek samping (*side effects*) atau bug baru pada fitur yang sudah ada.
  - Selalu lakukan audit kelengkapan fitur sebelum dan sesudah refactoring untuk memastikan fungsionalitas tetap 100% utuh.

## 8. Anti-Regression, Surgical Editing & Git Diff Audit Guard
- **Surgical / Atomic Edit Wajib:**
  - Pada file backend/handler request maupun file monolitik yang memiliki banyak baris dan endpoint, **DILARANG KERAS** menggunakan metode replace berbasis index kasar, broad regex, atau coarse slicing yang memotong area besar sekaligus.
  - Setiap modifikasi wajib bersifat *surgical* (hanya menargetkan blok kode yang relevan) tanpa menyentuh, menggeser, atau menghapus blok fitur/action lainnya.
- **Audit Wajib `git diff --stat` (Pencegahan Truncation & Deletion Tak Disengaja):**
  - Sebelum kode di-commit atau diberikan ke pengguna untuk di-deploy ke SAP SE80, wajib dilakukan audit diff (misal `git diff --stat`).
  - **RED FLAG:** Jika tujuan perubahan hanya berupa perbaikan kecil/syntax/styling namun `git diff --stat` menunjukkan puluhan atau ratusan baris terhapus (*massive deletions*), proses harus **SEGERA DIHENTIKAN** dan diaudit ulang hingga dipastikan tidak ada logika yang terpotong.
- **Verifikasi Integritas Endpoint / Action:**
  - Pastikan seluruh daftar action/event/fitur yang sebelumnya sudah aktif tetap utuh dan terdaftar setelah proses edit selesai.
- **SOP Rantai Validasi Baku:**
  - Setiap perubahan kode wajib mengikuti urutan:
    `Target Isolasi -> Surgical Edit -> Syntax/Logic Check -> Audit git diff --stat -> Verifikasi Integritas Fitur -> Deploy / SE80 Checklist`.

