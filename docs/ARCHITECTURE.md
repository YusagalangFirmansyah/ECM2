# ECM BSP — ARCHITECTURE

## Arsitektur BSP
- **Tipe:** Pages with Flow Logic (.htm)
- **Status:** Unchanged (NOT Stateful)
- **XSRF Protection:** unchecked
- **Tidak pakai:** Controller (.do), Page Fragment
- **Konvensi:** Sama dengan Z_MAINT_APP (KMI standard)
- **Sistem:** SAP S/4HANA 1809, SAP_BASIS 753 SP03

## Z-Tables

### ZECM_USER (SM30 maintainable)
- Field prefix: **ZECM_** (ZECM_USER_ID, ZECM_FULL_NAME, ZECM_PWD_HASH, ZECM_ROLE, ZECM_ACTIVE, ZECM_LAST_LOGIN)
- Auth: plain text password (field PWD_HASH tapi isinya plain)
- SNRO: ZECM_USER_ID (auto increment)

### ZECM_REQ (BSP-only, no SM30)
- Field prefix: **TANPA prefix** (ECR_NO, DOKAR, STATUS, DESCR, dll)
- SNRO: ZECM_REQ (NUMC 10)
- **V05 new fields:** TITLE, PRIORITY, COST_ESTIMATE, ZDEPT, ZREASON
- **Existing fields:** REJECT_REASON, REJECTED_BY, DIR_NUMBER

### ZECM_LOG (BSP-only, no SM30)
- Audit trail untuk semua perubahan status
- SNRO: ZECM_LOG (auto increment)
- Fields: LOG_ID, ECR_NO, ACTION, OLD_STATUS, NEW_STATUS, USER_ID, ACTION_DATE, ACTION_TIME, REASON

## Role (V05)

| Role | Fungsi | Halaman |
|------|--------|---------|
| DRAFTER | Buat ECR, kerjakan ECO, submit inspection | drafter_list, ecr_form, dms_list |
| ADMIN | Dashboard, approve/reject ECR (CRTD→INWK) | admin_dashboard, admin_ecr_list |
| APPROVER | Dashboard, approve/reject INSP | approver_dashboard, approver_list |
| OTHERS | Superadmin (existing) | dashboard, user_list |

## Status Flow (V05)

```
CRTD (Draft)     → Drafter buat ECR
  ↓ admin approve
INWK (In Work)   → ECO, drafter kerjakan + upload DMS
  ↓ drafter submit
INSP (Inspection) → Approver review
  ↓ approver approve
CLSD (Closed)     → Selesai

REJC (Rejected)   → Admin reject (dari CRTD) atau Approver reject (dari INSP)
```

### DMS Status Flow
```
IA (In Work) → AP (Inspection Req) → FR (Released)
                  ↓ approver revisi     ↓ approve (obsolete versi lama → H4)
                  IA (kembali)
                  ↓ approver reject
                  ZG (Rejected)
```

### Status Warna (Dashboard)

| Status | Label | Warna |
|--------|-------|-------|
| CRTD | Draft/ECR | 🔵 #3B82F6 |
| INWK | In Work/ECO | 🟠 #F59E0B |
| INSP | Inspection | 🟡 #EAB308 |
| CLSD | Closed | 🟢 #22C55E |
| REJC | Rejected | 🔴 #EF4444 |

## BSP Page Structure

```
Tab Layout          -> HTML murni + <%= variable %>
Tab Page Attributes -> DATA: variabel global (ALL CAPS: GV_*, LT_*, LS_*)
Tab Type Definitions -> TYPES: internal table (kalau perlu LOOP)
Tab Event Handler:
  +-- OnInitialization  -> Cookie, security check, data query, routing
  +-- OnInputProcessing -> Form submit, logout, actions
```

## Variable Naming Convention

**ALL CAPS** — Consistent since V03:
- **GV_*** → Global Variable (Page Attributes)
- **LV_*** → Local Variable
- **LS_*** → Local Structure
- **LT_*** → Local Table
- **LR_*** → Local Range

## Authentication

- **Metode:** Server-side cookie (CL_BSP_SERVER_SIDE_COOKIE)
- **Cookie name:** ECM_AUTH
- **Data fields:** USER_ID, FULL_NAME, ROLE
- **Session:** runtime->session_id

## Navigation

- **Di Event Handler:** `navigation->goto_page( page.htm )` — HTTP 302 redirect
- **Alternative:** `navigation->next_page( page.htm )` — server-side forward (no 302)
- **Di Layout:** TIDAK BISA (field unknown error)

## FM/BAPI

| FM | Fungsi |
|----|--------|
| BAPI_DOCUMENT_CHANGE2 | Update DMS status (IA→AP, AP→FR) |
| BAPI_TRANSACTION_COMMIT | Commit transaksi |
| NUMBER_GET_NEXT | Generate ZECM_LOG ID |
| CONVERSION_EXIT_ALPHA_OUTPUT | Hapus leading zero |
| CONVERSION_EXIT_ALPHA_INPUT | Tambah leading zero |

## BSP Pitfalls

- DATA declarations TOP LEVEL ONLY (bukan di dalam IF/CASE)
- ALL string literals MUST be quoted
- get_server_cookie pakai CHANGING (bukan IMPORTING)
- Layout hanya HTML + <%= %> (tidak ada navigation-> atau logic ABAP)
- File encoding PURE ASCII (bukan UTF-8 multi-byte)
- Type Definitions hanya TYPES: (bukan DATA:)
- Page Attributes tidak bisa TABLE OF (chain via Type Definitions)
- Comment WAJIB pakai `"` (double quote), bukan `*` di Event Handler
- SELECT WAJIB pakai koma (New Open SQL) + `@` di host variable
- JavaScript string line break pitfall — use string concatenation
- `REJECT_REASON` ≠ `ZREASON` — beda fungsi, jangan diganti
- COLLECT tidak bisa untuk non-numeric → pakai manual READ TABLE loop
- CONCATENATE integer → convert ke string dulu
- SweetAlert di modal → WAJIB pakai `target: document.getElementById('modalId')`
- DRAW query → jangan JOIN drat (causes SPRAS error), pakai draw langsung

## Referensi
- Referensi BSP: `Referensi BSP/` (Z_MAINT_APP pattern)
- BSP PM: `/mnt/data/files/sap-docs/BSP PM backup/` (Chart.js reference)

---
*Last updated: 01 Juli 2026*
