# Communication Guidelines — Stakeholder KMI

**Update:** 17 Juni 2026

---

## Surjantoro (Pak Bos) — Owner PT. KMI Business Group

**Profil:** Logical kuat, mau terjun langsung memahami alur sistem yang akan dibuat. Bukan developer, tapi paham bisnis process SAP.

**Dokumen governance yang disiapkan Pak Bos:**
- PWID-CONFIG-ECM-001
- MDAPPR-001
- PRICEAPPR-001
- MMDEMAR-001

### Aturan Penjelasan ke Pak Bos

1. **Penjelasan DETAIL, bukan singkat** — Pak Bos mau paham alur sistem secara mendalam, bukan sekadar gambaran besar.
2. **BOLEH sebut TCode standar SAP** — CC01/CC02/CC03, CS01/CS02, CS02, CE31/CE31, dll. Itu bahasa bisnis yang dia pahami.
3. **JANGAN masuk ranah ABAP** — Tidak perlu sebut `SELECT * FROM`, `IF sy-subrc = 0`, internal table, Page Attributes, Event Handler, dll. Dia bukan developer.
4. **Custom program jelaskan APA fungsinya** — Misalnya: "ZBSP_ECM_APP adalah aplikasi web di dalam SAP untuk membuat dan mengelola ECR (Engineering Change Request). Aplikasi ini menggantikan transaksi CC31 yang di-block oleh SAP." Jelaskan **APA** yang dilakukan custom program, bukan **BAGAIMANA** kode internalnya bekerja.

**Level bahasa:** Business Process + Functional SAP.
**Level bahasa yang SALAH:** Technical Implementation (ABAP, BSP code, database query).

### Contoh Penjelasan yang BENAR

> "ECR dibuat oleh Requester melalui aplikasi web ZBSP_ECM_APP. Setelah ECR terbuat dengan status Created (CRTD), Admin Drafter akan menerima notifikasi dan memilih Drafter yang sesuai. ECR berpindah ke status In Assignment (INASS). Selanjutnya Drafter yang dipilih menerima ECR, mengerjakan perubahan di SAP menggunakan transaksi CC02, lalu mengubah status ke In Review (REVW). Setelah Drafter selesai dan meng-upload hasil kerja, status berubah ke Inspection (INSP). Di tahap ini, Supervisor Drafter (Pak Eris) melakukan review dan approval melalui aplikasi BSP Approval. Jika disetujui, status menjadi Closed (CLSD) dan SAP Change Number yang sudah ter-create dapat digunakan untuk production order."

### Contoh Penjelasan yang SALAH

> "ECR di-insert ke ZECM_REQ dengan field STATUS='CRTD'. OnInputProcessing trigger ketika user klik submit, lalu SELECT SINGLE dari ZECM_USER untuk validasi. Event handler pake CASE event_id WHEN 'submit_ecr'."

---

## Stakeholder Lain

| Stakeholder | Peran | Level Penjelasan |
|------------|------|-------------------|
| Pak Ricky (Supervisor IT) | Supervisor Arya | Ringkas, profesional, fokus progress & masalah |
| Hanif (Basis) | Belajar SAP | Sabar, mudah dipahami, hanya topik SAP |
| Pak Eris | Supervisor Drafter | Fungsional, flow kerja drafter |

---

*Dibuat: 17 Juni 2026*
*File: /mnt/data/files/sap-docs/ecm/08-docs/communication-guidelines.md*
