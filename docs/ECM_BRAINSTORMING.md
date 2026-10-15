# ECM Project Brainstorming — KMI

**Status:** Aktif
**Fokus Saat Ini:** Persiapan Fitur Perubahan Routing

---

## TOPIK 1: Alur & Desain Perubahan Routing (Agustus 2026)

Menyusul kesuksesan implementasi fitur BOM Gate, tahap selanjutnya adalah mengakomodasi perubahan **Routing** (urutan proses produksi) dalam sistem ECM.

### Kesepakatan (Berdasarkan Diskusi dengan Arya):
1. **Menu Terpisah:** Untuk Master Data, akan dibuatkan *menu terpisah* di dashboard: satu menu khusus "Approve BOM", dan satu menu baru "Dashboard Perubahan Routing".
2. **Tabel Baru (ZECM_IROUTING):** Request perubahan Routing akan menggunakan tabel baru bernama `ZECM_IROUTING` di SAP (terpisah dari ZECM_IREQ) agar lebih rapi dan modular.
3. **Role Baru (PRODUKSI):** Alur Routing ini di-trigger (di-request) oleh pihak **Produksi**, BUKAN oleh Requester standar. Karena itu, akan ditambahkan Role baru di aplikasi yaitu `PRODUKSI`.

### Rencana Eksekusi (Action Plan):

#### 1. Desain Database Baru (SE11)
Arya akan membuat struktur tabel `ZECM_IROUTING`. 

#### 2. Penambahan Role PRODUKSI
- Tambahkan logic routing login untuk role `PRODUKSI` (di `login_event_handler.txt` & `dashboard_oninit.txt`).
- Buat halaman dashboard khusus untuk role `PRODUKSI` (`produksi_list.htm`, dll) sebagai tempat mereka mengajukan request perubahan Routing.
- Update `user_list.htm` agar Admin bisa mendaftarkan user dengan role `PRODUKSI`.

#### 3. Penyesuaian UI & Menu Master Data
- Master Data Dashboard: Tambahkan sistem navigasi/tab untuk beralih antara "Approve BOM" dan "Dashboard Perubahan Routing".
- Review dan verifikasi routing (dengan form approval/rejection).

#### Hasil Desain Tabel `ZECM_IROUTING` (SE11)
Arya telah membuat tabel `ZECM_IROUTING`. Strukturnya dibuat hampir **identik/cloning** dari `ZECM_IREQ`, dengan field utama sebagai berikut:
- `MANDT` (Key)
- `IROUTING_ID` (Key) - CHAR 10
- `REQUESTER`
- `REQ_DATE`
- `TITLE`
- `MATNR_FG`
- `KATEGORI`
- `PRIORITY`
- `ZDEPT`
- `ZREASON`
- `DESCRIPTION` (STRING)
- `STATUS`
- `ADMIN_NOTE`
- `ASSIGNED_DRAFTER`
- `ECR_NO`
- `CREATED_AT`
- `UPDATED_AT`
- `COST_ESTIMATE` (CHAR 15)

*Catatan Analisis:* Karena strukturnya sama persis dengan IREQ, ini sangat memudahkan dari sisi BSP. Kita bisa me-reuse pattern kodingan (layout dan handler) dari halaman Requester List saat ini untuk di-porting ke halaman Produksi List.

### Analisis Workflow (ZECM_REQ)
Arya bertanya apakah status Routing ini bisa "numpang" menggunakan field status milik Drawing/BOM yang sudah ada di `ZECM_REQ`. 

Jawaban: **Lebih baik dipisah (ditambahkan field baru).**
- *Alasan 1 (Beda Lifecycle):* BOM dan Drawing punya *gate* dan aktor sendiri (Drafter & Master Data BOM). Routing punya aktor sendiri (Mbak Septin). Jika kita hanya punya 1 field `STATUS` di `ZECM_REQ` (misal: 'INWK', 'BMPR', 'BMAP'), kita akan bingung melacak *siapa yang sedang kerja*. Apakah sedang nunggu Drawing? Nunggu BOM? Atau nunggu Routing?
- *Alasan 2 (Status Bentrok):* Kalau ECR sudah selesai Drawing & BOM-nya (`BOM_CHECK` = 'A'), dia siap masuk `INSP`. Tapi kalau ECR itu ternyata butuh Routing dan Routing-nya belum selesai, dia tidak boleh masuk `INSP`. Kita butuh 2 "gembok" yang berbeda.
- *Rekomendasi Arsitektur:* 
  1. ECR "Jalur Drawing & BOM": Gate `BOM_CHECK` harus 'A' untuk lanjut.
  2. ECR "Jalur Routing": Gate `ROUT_CHECK` harus 'A' untuk lanjut.
  3. Dengan punya `ROUT_CHECK` (CHAR 1) dan `ROUT_NOTES` (CHAR 255) sendiri di `ZECM_REQ`, status perkerjaan Mbak Septin terisolasi rapi dan tidak akan menimpa/merusak log pekerjaan Mbak Ayu/Kesi.

### Revisi Workflow Routing (Berdasarkan Diskusi Terbaru)
Berbeda dengan workflow Drawing & BOM yang panjang (Drafter -> MD -> Inspection/QC -> Admin), alur Routing didesain jauh lebih ringkas:

**HANYA ADA 2 AKTOR:**
1. **PRODUKSI (Requester Routing):**
   - Mengajukan request perubahan routing via tabel `ZECM_IROUTING`.
2. **MASTER DATA (Penerima & Eksekutor Routing - Mbak Septin):**
   - Menerima request dari Produksi.
   - Mengerjakan perubahan routing langsung di SAP (CA02).
   - Menandai request sebagai Selesai / DONE.

**Tidak ada tahap Inspection (INSP) oleh QC/Admin.** Setelah dikerjakan oleh Master Data, dokumen langsung dianggap selesai (`CLSD` / DONE).

#### Mapping Status (CHANGE_SCOPE = 'ROUT'):
1. Saat Produksi Submit: `STATUS = 'REQ'` (Tersimpan di `ZECM_IROUTING`)
2. Master Data (Septin) memproses: Request di-Approve menjadi ECR resmi di `ZECM_REQ` dengan status **`INWK`** (In Work).
3. Master Data (Septin) mengeksekusi routing di sistem dan klik "Selesai": Status ECR langsung berubah menjadi **`CLSD`** (Closed / Done).

### Analisis Risiko "Tercampur" Antara Drawing dan Routing
Arya mengkonfirmasi ulang apakah penggunaan field STATUS yang sama ('INWK', 'CLSD') berisiko membuat data Routing tercampur dengan data Drawing/BOM di dashboard.

Jawaban: **TIDAK AKAN TERCAMPUR, asalkan kita disiplin menggunakan `CHANGE_SCOPE`.**

**Bagaimana kita mencegahnya di Kodingan BSP:**
Di setiap halaman (Drafter, Master Data BOM, QC, Viewer), kita WAJIB menambahkan filter `AND change_scope = 'DRWG'` pada query SQL-nya.
Contoh di `drafter_list_oninit.txt`:
```abap
SELECT * FROM zecm_req INTO TABLE lt_ecr 
  WHERE status = 'INWK' 
  AND change_scope = 'DRWG'. " <-- INI KUNCI PENGAMannya
```
Dengan begitu, meskipun ada ECR Routing milik Mbak Septin yang statusnya juga sedang `'INWK'`, ECR tersebut **tidak akan pernah muncul** di layar Drafter, karena *scope*-nya berbeda (`'ROUT'`).

**Satu-satunya halaman yang menggabungkan keduanya:**
Halaman Dashboard Admin (Grafik Donat / Bar Chart beban kerja pabrik). Di chart ini, ECR Drawing dan ECR Routing yang statusnya sama-sama `'INWK'` akan dihitung jadi satu total beban kerja `INWK` pabrik, yang mana ini memang tujuan dari pelaporan level manajemen (Melihat total ECR In Work secara keseluruhan). Jika manajemen ingin melihat pemisahannya, kita bisa membuat filter Chart berdasarkan `CHANGE_SCOPE` nanti.
