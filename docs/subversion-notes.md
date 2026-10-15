# ECM BSP — Sub-Version System

## Alur Kerja

1. Mulai kerja di subversi terbaru (working copy)
2. Sebelum perubahan besar → **snapshot ke sub-versi baru** (full copy)
3. Lanjut fix di subversi baru
4. Kalau rusak → rollback ke checkpoint terakhir

## Struktur Folder (Status per 04 September 2026)

```
ecm/
├── README2.md
├── CHANGELOG.md
├── VERSIONS.md
├── INDEX.md
├── ECM_ROADMAP.md
├── subversion-notes.md
├── archive/
├── bsp-ecm-app/
│   ├── V01/                ← Production Baseline (SAP)
│   ├── V02/                ← Development MVP backup (v02_a - v02_b)
│   ├── V03/                ← ECR List Enhancement (v03_a - v03_c)
│   ├── V04/                ← Multi-Role + DMS (v04_a - v04_i)
│   ├── V05/                ← Dashboard Redesign + Date Filter (v05_a - v05_m)
│   ├── V06/                ← Viewer Role + Cetak PDF (v06_a - v06_j)
│   ├── V07/                ← Pre-ECR Request System (v07_a - v07_r)
│   ├── V08/                ← Multi Attachment + BOM Gate (v08_a - v08_p)
│   ├── V09/                ← Produksi Role (v09_a - v09_b)
│   ├── V10/                ← Routing Approval & CHANGE_SCOPE (v10_a - v10_g)
│   ├── V11/                ← Multi-Level IREQ Approval (v11_a - v11_m)
│   ├── V12/                ← Request Reject Handling & UI Enhancements (v12_a - v12_p)
│   ├── V13/                ← Prevent Double Request & Status Fix (v13_a_prevent_double_request)
│   └── V14/                ← Implementation Tracking (PO & Date Rilis) (AKTIF)
│       ├── v14_a_impl_tracking/
│       ├── v14_b_drafter_impl/
│       ├── v14_c_requester_view/
│       ├── v14_d_approver_reject_view/
│       ├── v14_e_admin_impl_tracking/
│       ├── v14_f_admin_all_ecr_sources_impl/
│       ├── v14_g_fix_skip_bom/
│       ├── v14_h_add_dept_reason/
│       └── v14_i_panel_print_split/       ← CURRENT WORKING COPY
├── design/
├── sap-config/
└── ztables/
```

## Aturan Penting

1. **Setiap subversi = FULL COPY** — bukan hanya file yang berubah.
2. **Naik subversi** hanya atas perintah user.
3. **Jangan hapus** subversi yang masih dipakai.
4. **Archive** hanya untuk file one-time.
5. **Naming**: `vXX_y_descriptive_title` (underscore + lowercase + descriptive).
6. **Dokumentasi Sinkron**: Setiap selesai rilis subversi baru, update `CHANGELOG.md` dan `VERSIONS.md` di root `/ecm/`.

---

*Last updated: 04 September 2026*
