# ECM Roadmap — PT. Kayu Mebel Indonesia

**Last Updated:** 04 September 2026  
**Status:** Active Development (V14 - Implementation Tracking)  
**Developer:** Arya Prayogi Utama + Yogi (ECM Dev)

---

## 📍 Posisi Saat Ini

```
KITA DI SINI
     ↓
[■■■■■■■■□□□□□□□□□□□□] ~40%
```

### Sudah Dibangun (Phase 1) ✅

- ✅ DMS (Drawing) — DRW/DBX/DMT, Upload, Status, Preview
- ✅ ECR/ECO Workflow — Create → Approve → ECO → Close
- ✅ Pre-ECR Request (IREQ) — Requester → Admin → ECO
- ✅ Multi-Role — Admin, Drafter, Approver, Viewer, Requester
- ✅ Audit Trail — Semua aktivitas tercatat
- ✅ Print/PDF — Cetak ECR dan IREQ

### Sedang Dibangun (V14 - Implementation Tracking) 🚧
> Mencatat rencana/estimasi eksekusi dari Engineering Change di lapangan.
- Field tambahan di `ZECM_REQ` dan `ZECM_IREQ`: `IMPL_PO` (Next PO/Spesifik), `IMPL_DATE` (Tanggal), `IMPL_REASON` (Alasan).
- Hanya untuk ECR Drawing (CHANGE_SCOPE = 'DRWG').
- Diisi oleh Kepala R&D pada saat persetujuan IREQ (Status REQ → APPR).
- Fitur wajib isi (*mandatory*) sebagai bukti dokumentasi historis, akan tampil pada ECR Detail dan cetakan PDF resmi.

---

## 🎯 Vision: ECM = Change Governance Engine

> **ECM bukan menggantikan cara kerja, tapi mengatur cara GOVERNANCE.**

### Masalah yang Diselesaikan

> **"Berjalan liar, tidak terecord, sulit dipertanggungjawabkan"**

- Request perubahan via WhatsApp, telepon, walk-in
- Tidak ada record siapa yang minta, kapan, kenapa
- Tidak ada approval trail
- Sulit dipertanggungjawabkan

### Solusi: Gatekeeper Approach

```
SEKARANG (Liar):
User ──WhatsApp──▶ BOM Admin ──ubah langsung──▶ SAP
       (tidak tercatat)

SEHARUSNYA (Governed):
User ──▶ ECM ──▶ BOM Admin ──▶ Approval ──▶ SAP
         │                        │
         │                   (tercatat siapa approve,
         │                    kapan, kenapa)
         │
    (tercatat siapa request,
     apa yang diminta, kenapa)
```

### Key Principles

1. **ECM memaksa semua perubahan lewat satu pintu**
2. **ECM tidak mengontrol cara kerja di belakangnya**
3. **Pekerjaan aktual bisa di SAP standard, manual, atau di luar system**
4. **Yang penting: SEBELUM dan SESUDAH ubah, harus lewat ECM**
5. **Tidak boleh ada bypass** — butuh komitmen manajemen

---

## 🏗️ Arsitektur: Hybrid Enforcement

> **Mulai dari yang cepat (Policy), desain data model untuk masa depan (Technical)**

### 3 Level Enforcement

```
┌─────────────────────────────────────────────────────────┐
│              HYBRID ENFORCEMENT                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  LEVEL 1: TECHNICAL (Drawing/DMS)                       │
│  ──────────────────────────────────                     │
│  - Tidak bisa upload tanpa ECM                          │
│  - ECM kontrol penuh                                    │
│  - SUDAH DIBANGUN ✅                                    │
│                                                         │
│  LEVEL 2: SEMI-RIGID (BOM/Routing)                      │
│  ──────────────────────────────────                     │
│  - User submit request di ECM                           │
│  - Admin approve di ECM                                 │
│  - PIC kerjakan di SAP standard                         │
│  - PIC upload bukti (screenshot, dokumen)               │
│  - Bukti wajib + timeout escalate                       │
│  - Kalau tidak ada bukti dalam X hari = escalate        │
│                                                         │
│  LEVEL 3: POLICY (Program/Tooling/Take Time)            │
│  ──────────────────────────────────                     │
│  - User submit request di ECM                           │
│  - PIC kerjakan (di luar system)                        │
│  - PIC update status di ECM                             │
│  - Management decree + audit                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Enforcement Table

| Level | Module | Enforcement | Bisa Di-bypass? | Biaya |
|-------|--------|-------------|:---------------:|:-----:|
| **Technical** | Drawing/DMS | Hapus akses SAP, ECM trigger BAPI | ❌ Tidak | Mahal |
| **Semi-Rigid** | BOM/Routing | Bukti wajib + timeout escalate | ⚠️ Sulit | Medium |
| **Policy** | Program/Tooling/Take Time | Management decree + audit | ✅ Bisa | Murah |

### Evolusi Path

```
Phase sekarang: Policy enforcement (cepat build)
         │
         ▼
Phase berikutnya: Semi-Rigid enforcement (bukti wajib)
         │
         ▼
Phase masa depan: Technical enforcement (ECM trigger SAP)
```

**Data model TETAP SAMA** — hanya enforcement yang berubah.

---

## 🗺️ Grand Vision

```
                          ┌─────────────────────┐
                          │   ENGINEERING CHANGE │
                          │     MANAGEMENT       │
                          └──────────┬──────────┘
                                     │
          ┌──────────┬──────────┬────┴────┬──────────┬──────────┐
          │          │          │         │          │          │
     ┌────▼───┐ ┌────▼───┐ ┌───▼───┐ ┌───▼───┐ ┌───▼───┐ ┌───▼───┐
     │  DMS   │ │  BOM   │ │ROUTING│ │TAKE   │ │PROGRAM│ │TOOLING│
     │Drawing │ │        │ │       │ │ TIME  │ │       │ │       │
     └───┬────┘ └───┬────┘ └───┬───┘ └───┬───┘ └───┬───┘ └───┬───┘
         │          │          │         │         │         │
    ┌────▼───┐ ┌────▼───┐ ┌───▼───┐ ┌───▼───┐ ┌───▼───┐ ┌───▼───┐
    │ DRAWING│ │  BOM   │ │ROUTE  │ │TIME   │ │PROGRAM│ │ TOOL  │
    │ ADMIN  │ │ ADMIN  │ │ ADMIN │ │ ADMIN │ │ ADMIN │ │ ADMIN │
    └────────┘ └────────┘ └───────┘ └───────┘ └───────┘ └───────┘
```

---

## 🛤️ Development Sequence

### Phase 1: Foundation ✅

> DMS + ECR Workflow + Multi-Role

- V01-V03: Basic ECR + List
- V04: Multi-Role + DMS
- V05: Dashboard Redesign
- V06: Viewer + Polish
- V07: Pre-ECR Request (IREQ) + Filter + Cetak PDF

### Phase 2: BOM 🔜

> BOM Change Management dalam ECO

**Approach:** Semi-Rigid (Gatekeeper + Bukti)

**Fitur:**
- BOM Change Request dalam ECO (module_type = 'BOM')
- BOM Admin role (terpisah dari Drawing Admin)
- BOM Approval Flow
- Bukti upload (screenshot perubahan BOM)
- Timeout escalate (kalau bukti tidak upload dalam X hari)
- BOM Comparison (Before vs After) — optional

**Tabel:**
- `ZECM_BOM_REQ` — BOM Change Request (atau extend ZECM_REQ)
- `ZECM_BOM_LOG` — BOM Audit Trail

**SAP Integration:**
- CS01/CS02 — BOM Create/Change (manual oleh BOM Admin)
- STKO, STPO, MAST — BOM tables (read only untuk verification)

### Phase 3: Routing & Take Time 📋

> Process Change + Time Study

**Approach:** Semi-Rigid (Routing) + Policy (Take Time)

**Fitur:**
- Routing Change Request dalam ECO (module_type = 'ROUTING')
- Routing Admin role
- Routing Approval Flow
- Take Time Documentation (upload hasil time study)
- Time Impact Analysis (optional)

**SAP Integration:**
- CR01/CA01 — Routing Create/Change (manual oleh Routing Admin)
- PLKO, PLPO, CRHD — Routing tables (read only)

### Phase 4: Program & Tooling 📋

> CNC Program + Jig/Fixture/Mold

**Approach:** Policy (Gatekeeper)

**Fitur:**
- Program Change Request dalam ECO (module_type = 'PROGRAM')
- Tooling Change Request dalam ECO (module_type = 'TOOLING')
- Program/Tooling Admin role
- Tooling Lifecycle Tracking
- Maintenance Schedule (optional)

### Phase 5: Costing & Approval 📋

> Cost Impact + Multi-Department Approval

**Approach:** Semi-Rigid

**Fitur:**
- Cost Breakdown per ECO (Material + Labor + Overhead)
- Costing Role (Cost Analyst, Cost Approver)
- Cost Approval Workflow
- Cost Report (per ECR, per material, per period)
- Budget Impact Analysis
- Threshold: cost > X butuh approval management

---

## 👥 Admin per Module

| Module | Admin Role | Department | Enforcement |
|--------|------------|------------|:-----------:|
| Drawing/DMS | Drawing Admin | Engineering/R&D | Technical |
| BOM | BOM Admin | Production Planning | Semi-Rigid |
| Routing | Routing Admin | Production/IE | Semi-Rigid |
| Take Time | Time Study Admin | Industrial Engineering | Policy |
| Program | Program Admin | Engineering/CNC | Policy |
| Tooling | Tooling Admin | Engineering/Maintenance | Policy |
| Costing | Cost Analyst | Finance/Accounting | Semi-Rigid |
| Final Approve | Management | Director/VP | - |

---

## 🔄 Approval Flow

```
Requester Submit (Any User)
       │
       ▼
Admin Review (Approve/Reject + Assign Drafter/PIC)
       │
       ▼ ECO Created
PIC Work (Drawing/BOM/Routing/Program/Tooling)
       │
       ▼ Submit + Upload Bukti
┌─────────────────────────────────────┐
│         APPROVAL CHAIN              │
│                                     │
│  Drawing Approve ──▶ (if BOM chg)  │
│       │                    │        │
│       ▼                    ▼        │
│  BOM Approve ──▶ (if Route chg)    │
│       │                    │        │
│       ▼                    ▼        │
│  Routing Approve ──▶ (if cost > X) │
│       │                    │        │
│       ▼                    ▼        │
│  Costing Approve ──▶ Final Approve │
│                            │        │
└────────────────────────────┼────────┘
                               │
                               ▼
                          ECO Released (CLSD)
```

**Approval chain dinamis** — tergantung scope perubahan.

---

## 📊 Module Priority Matrix

| Module | Urgency | Complexity | Impact | Enforcement | Est. Effort |
|--------|:-------:|:----------:|:------:|:-----------:|:-----------:|
| DMS (Drawing) | ✅ Done | Medium | High | Technical | Done |
| ECR/ECO Workflow | ✅ Done | High | High | Technical | Done |
| Pre-ECR Request | ✅ Done | Medium | Medium | Technical | Done |
| **BOM** | 🔜 High | High | High | Semi-Rigid | 4-6 weeks |
| **Costing** | 🔜 High | Medium | High | Semi-Rigid | 3-4 weeks |
| Routing | 📋 Medium | High | Medium | Semi-Rigid | 4-6 weeks |
| Take Time | 📋 Medium | Low | Medium | Policy | 2-3 weeks |
| Program | 📋 Low | Medium | Low | Policy | 3-4 weeks |
| Tooling | 📋 Low | Medium | Low | Policy | 3-4 weeks |

---

## 🏗️ Data Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   ECM DATA MODEL                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  EXISTING (Phase 1):                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ ZECM_REQ    │  │ ZECM_IREQ   │  │ ZECM_LOG    │    │
│  │ (ECR/ECO)   │  │ (Request)   │  │ (Audit)     │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
│  ┌─────────────┐                                        │
│  │ ZECM_USER   │                                        │
│  │ (User/Role) │                                        │
│  └─────────────┘                                        │
│                                                         │
│  EXTEND (Phase 2+):                                     │
│  - Tambah field `module_type` di ZECM_REQ               │
│    (DRAWING/BOM/ROUTING/PROGRAM/TOOLING/COSTING)        │
│  - Tambah field `bukti_url` di ZECM_REQ (untuk semi-    │
│    rigid enforcement)                                   │
│  - Tambah field `escalate_date` di ZECM_REQ             │
│  - Approval chain config di ZECM_USER (per module)      │
│  - Tambah `IMPL_PO`, `IMPL_DATE`, `IMPL_REASON` di      │
│    ZECM_IREQ dan ZECM_REQ (V14 Implementation tracking) │
│                                                         │
│  TIDAK PERLU TABEL BARU — extend yang ada               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📝 Key Insights (dari Brainstorming 30 Jul 2026)

1. **ECM bukan cuma DMS** — mencakup BOM, Routing, Take Time, Program, Tooling, Costing
2. **Masalah utama: GOVERNANCE** — "berjalan liar, tidak terecord"
3. **ECM = Change Governance Engine** — bukan menggantikan cara kerja, tapi mengatur governance
4. **Gatekeeper approach** — memaksa compliance, tapi fleksibel di eksekusi
5. **Hybrid enforcement** — Technical (Drawing), Semi-Rigid (BOM/Routing), Policy (lainnya)
6. **Approval chain dinamis** — tergantung scope perubahan
7. **Tidak boleh ada bypass** — butuh komitmen manajemen
8. **Data model universal** — extend ZECM_REQ, tambah module_type
9. **Evolusi tanpa redesign** — upgrade enforcement tanpa ubah data model

---

## ❓ Open Questions

1. **BOM** — apakah BOM change di SAP standard (CS02) masih dipake?
2. **Costing** — cost estimation dilakukan oleh siapa? Finance sudah punya system?
3. **Take Time** — hasil time study perlu diinput ke SAP routing?
4. **Threshold** — berapa batas cost yang butuh approval management?
5. **PIC Assignment** — bagaimana cara assign PIC per module?
6. **Timeout** — berapa hari batas upload bukti sebelum escalate?

---

## 💡 Quotes Penting

> "ECM bukan menggantikan cara kerja, tapi mengatur cara GOVERNANCE."

> "ECM harus jadi GATEKEEPER, bukan sekadar pencatat. Kalau bisa di-bypass, tetap liar."

> "Berjalan liar, tidak terecord, sulit dipertanggungjawabkan" — masalah utama yang diselesaikan ECM.

> "Hybrid tadi aja aku setuju, dan bisa di-update kalau memang butuh lebih rigid" — keputusan enforcement.

---

*Dicatat: 30 Juli 2026*  
*Source: Brainstorming session Yogi + AI Assistant SAP*

## Phase 3: Routing Change Request (Upcoming)
**Status:** Perencanaan (Brainstorming)
**Deskripsi:** Membangun sistem untuk menangani permintaan perubahan *Routing* (selain BOM dan Drawing).

### 1. Struktur Data & Tabel
- Penambahan field `ROUTING_CHECK` (mirip `BOM_CHECK`) di tabel `ZECM_REQ`.
- Evaluasi kebutuhan tabel tambahan untuk attachment/notes terkait Routing (misal: `ZECM_ROUTING_ATT` jika diperlukan, atau reuse yang ada).
- Update `ZECM_LOG` untuk mencatat log aktivitas terkait Routing.

### 2. Role & UI/UX Dashboard
- Pembuatan/Penyesuaian Role: Apakah Master Data Routing sama dengan Master Data BOM? (Konfirmasi ke Arya).
- Penambahan filter/kategori `Routing` di form *Request Perubahan Baru* (IREQ).
- Penambahan *Routing Gate* (mirip *BOM Gate*) di UI Drafter & Master Data.

### 3. Workflow (To Be Confirmed)
1. **Requester:** Memilih material dan checklist kebutuhan perubahan (BOM / Drawing / Routing).
2. **Admin:** Review dan Approve request (IREQ -> ECO).
3. **Drafter:** Mengerjakan drawing (jika ada).
4. **Master Data (Routing):** Mengupdate routing di SAP (CA02) dan mengupload bukti/catatan.
5. **Approval Routing:** Admin / SPV memastikan routing sudah sesuai sebelum lanjut ke gate berikutnya (Inspection).

*Detail lebih lanjut akan didiskusikan dan di-update di file `ECM_BRAINSTORMING.md`.*
