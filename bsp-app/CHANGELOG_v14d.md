## v14_d_approver_reject_view (04/09/2026)
- **Tujuan**: Mempermudah Approver melihat *Reject Reason* (alasan penolakan) pada IREQ yang sudah ditolak, dan menambahkan fitur *Audit Trail* pada card IREQ di dashboard Approver.
- **Perubahan**:
  - Menyalin base dari `v14_c_requester_view` ke `v14_d_approver_reject_view`.
  - [SELESAI] Mengedit `approver_list_oninit.txt` untuk menampilkan `reject_reason` bila status IREQ adalah `REJC` (Ditolak).
  - [SELESAI] Menambahkan button *Audit Trail* pada card detail IREQ di file yang sama beserta file `approver_list.htm` dan `page_attributes`.