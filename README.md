# ECM (Antigravity Workspace)

Direktori ini dipersiapkan khusus sebagai workspace pengerjaan modul **Engineering Change Management (ECM)** oleh AI Agent **Antigravity**.

---

## 📌 Dokumen Wajib Baca Sebelum Mulai:
1. 📄 **[`ANTIGRAVITY_HANDOVER_ECM.md`](ANTIGRAVITY_HANDOVER_ECM.md)**:
   * Panduan arsitektur lengkap, matrik role & permission, state machine status tiket, kamus tabel database `ZECM_*`, dan katalog jebakan koding BSP & solusinya.
2. 📄 **[`../CHANGELOG.md`](../CHANGELOG.md)**:
   * Riwayat perubahan detail dari V01 sampai versi aktif terkini (V14_i).
3. 📄 **[`../VERSIONS.md`](../VERSIONS.md)**:
   * Garis waktu keputusan arsitektur major yang tidak boleh dilanggar.

---

## 📚 Knowledge Base & Dokumentasi Penting (Folder `docs/`):
Seluruh arsip pengetahuan dan analisis teknis proyek ECM telah dihimpun di dalam subfolder **[`docs/`](docs/)**:
1. 📄 **[`docs/ECM_PROJECT_INSIGHT.md`](docs/ECM_PROJECT_INSIGHT.md)** *(34 KB)*:
   * **Wajib Baca**: Filosofi mendalam proyek ECM, alasan bisnis ("Gatekeeper Approach"), keluhan user di lapangan, aturan revisi BOM, dan batasan UI minimalis.
2. 📄 **[`docs/ECM_ROADMAP.md`](docs/ECM_ROADMAP.md)** *(17 KB)*:
   * Status pengembangan makro modul ECM, daftar fitur selesai, dan integrasi modul selanjutnya (Costing, Master Data).
3. 📄 **[`docs/tutorial-upload-dms.md`](docs/tutorial-upload-dms.md)** & **[`docs/tutorial-drafter.md`](docs/tutorial-drafter.md)**:
   * Alur teknis Drafter dan integrasi SAP DMS (`DOKAR`, `DOKNR`, `DRAW`) untuk gambar teknik.
4. 📄 **[`docs/insight-dms-cross-contamination.md`](docs/insight-dms-cross-contamination.md)**:
   * Catatan investigasi pencegahan bug kontaminasi link dokumen antar-ECR.
5. 📄 **[`docs/CHANGELOG.md`](docs/CHANGELOG.md)** & **[`docs/VERSIONS.md`](docs/VERSIONS.md)**:
   * Riwayat mikro setiap rilis dari V01 s/d V14_i dan garis waktu keputusan arsitektur.
6. 📄 **[`docs/V14_IMPL_TRACKING_DESIGN.md`](docs/V14_IMPL_TRACKING_DESIGN.md)**:
   * Desain asli Implementation Tracking (`impl_po`, `impl_date`, `impl_reason`).
7. 📄 **[`docs/communication-guidelines.md`](docs/communication-guidelines.md)**:
   * Gaya kerja dan preferensi komunikasi dengan Yogi (bahasa Indonesia, to-the-point, anti asumsi, verifikasi nyata).

---

## 📂 Struktur Folder Workspace:
* **`bsp-app/`**:
  * Berisi salinan **100% lengkap dan mutakhir** dari subversi terakhir (**`v14_i_panel_print_split`**).
  * Semua file HTML (`.htm`), Event Handler (`.txt`), Page Attributes, dan Type Definitions siap diinspeksi, dimodifikasi, dan di-copy ke SAP SE80.
* **`docs/`**:
  * Seluruh dokumen referensi, panduan DMS, roadmap, dan catatan arsitektur di atas.
* **`PDF_CONVERTER/`**:
  * Tool/skrip pendukung konversi dokumen PDF.
* **`SCRIPT_PYTHON_DMS/`**:
  * Skrip otomasi pengolahan dokumen drawing DMS.

---

## ⚠️ Aturan Penting Lapangan:
1. **Server 168 adalah Rumah Tunggal Project**: Seluruh file project berada di host srv168.
2. **Dilarang Upload/SCP ke Server 167**: Server 167 murni reverse proxy Nginx dan DB non-SAP.
3. **SweetAlert Z-Index**: Selalu pasang `.swal2-container { z-index: 100000 !important; }` jika dialog muncul bersamaan dengan modal `#detailModal`.
4. **Hindari Injeksi String Mentah ke JS**: Bungkus pesan server ABAP menggunakan atribut data HTML (`data-msg`) untuk menghindari `SyntaxError`.
