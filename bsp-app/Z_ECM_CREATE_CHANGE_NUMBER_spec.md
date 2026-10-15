# Rumusan: Z_ECM_CREATE_CHANGE_NUMBER

## Tujuan
Create Change Number (AENR) secara programmatic tanpa CC01 BDC, untuk dipanggil dari BSP approver_list saat approve ECR.

---

## 1. Interface (SE37)

### Importing Parameters

| Parameter | Type | Optional | Keterangan |
|-----------|------|----------|------------|
| `IV_ECR_NO` | `ZECM_ECR_NO` (NUMC10) | Required | Nomor ECR |
| `IV_TITLE` | `AENR-TEXT1` (CHAR40) | Required | Deskripsi perubahan |
| `IV_REASON` | `AENR-GRUND` (CHAR40) | Optional | Alasan perubahan |
| `IV_MATNR` | `MATNR` (CHAR18) | Optional | Material FG (untuk object link) |
| `IV_DOKAR` | `DOKAR` (CHAR3) | Optional | Tipe dokumen DRW/DBX/DMT |
| `IV_DOKNR` | `DOKNR` (CHAR25) | Optional | Nomor DMS (untuk object link) |
| `IV_DOKVR` | `DOKVR` (CHAR2) | Optional | Versi DMS |
| `IV_DOKTL` | `DOKTL_D` (CHAR3) | Optional | Part DMS |

### Exporting Parameters

| Parameter | Type | Keterangan |
|-----------|------|------------|
| `EV_AENNR` | `AENNR` (CHAR12) | Change Number yang di-generate |
| `EV_SUCCESS` | `ABAP_BOOL` | Berhasil/gagal |
| `EV_MESSAGE` | `STRING` | Pesan error/sukses |

---

## 2. Tabel yang Di-insert

| # | Tabel | Key | Fields yang diisi |
|---|-------|-----|-------------------|
| 1 | **AENR** | AENNR | CCART, TEXT1, DATUV, GRUND, AENST, ERNAM, ERDAT, AENAM |
| 2 | **AENR_STATUS** | AENNR + STAT | STAT (status code), USNAM, DATUM, ZEIT |
| 3 | **AEOI** | AENNR + OBJTP + OBJKY | OBJTP='MARA' (Material), OBJKY=matnr |
| 4 | **AEOI** | AENNR + OBJTP + OBJKY | OBJTP='DRAW' (Document), OBJKY=doknr |

---

## 3. Logic Flow

```
START
│
├─ 1. VALIDATE input
│     └─ IF IV_ECR_NO IS INITIAL → RETURN error
│
├─ 2. GENERATE number
│     └─ CALL FUNCTION 'NUMBER_GET_NEXT'
│          EXPORTING object = 'AENNR' nr_range_nr = '01'
│          IMPORTING number = lv_aennr
│
├─ 3. CONVERSION_EXIT_ALPHA_INPUT lv_aennr
│
├─ 4. INSERT AENR (header)
│     ├─ AENNR = lv_aennr
│     ├─ CCART = 'ZECR' (Change Type — cek TCC11)
│     ├─ TEXT1 = IV_TITLE
│     ├─ DATUV = sy-datum (Valid-from)
│     ├─ GRUND = IV_REASON
│     ├─ AENST = '01' (CRTD — status awal)
│     ├─ ERNAM = sy-uname
│     ├─ ERDAT = sy-datum
│     └─ AENAM = sy-uname
│
├─ 5. INSERT AENR_STATUS (status log)
│     ├─ AENNR = lv_aennr
│     ├─ STAT = '01' (CRTD)
│     ├─ USNAM = sy-uname
│     ├─ DATUM = sy-datum
│     └─ ZEIT = sy-uzeit
│
├─ 6. INSERT AEOI — Material Link (jika IV_MATNR diisi)
│     ├─ AENNR = lv_aennr
│     ├─ OBJTP = 'MARA'
│     └─ OBJKY = IV_MATNR (ALPHA_INPUT)
│
├─ 7. INSERT AEOI — Document Link (jika IV_DOKNR diisi)
│     ├─ AENNR = lv_aennr
│     ├─ OBJTP = 'DRAW'
│     └─ OBJKY = IV_DOKNR
│
├─ 8. UPDATE ZECM_REQ
│     └─ UPDATE zecm_req SET aennr = lv_aennr WHERE ecr_no = IV_ECR_NO
│
├─ 9. COMMIT WORK
│
└─ 10. RETURN
       ├─ EV_AENNR = lv_aennr
       ├─ EV_SUCCESS = 'X'
       └─ EV_MESSAGE = 'Change Number berhasil dibuat'
```

---

## 4. Error Handling

| Step | Error | Action |
|------|-------|--------|
| 1 | ECR_NO kosong | RETURN EV_SUCCESS = '' |
| 2 | Number range habis | ROLLBACK, RETURN error |
| 4 | INSERT AENR gagal | ROLLBACK, RETURN error |
| 8 | UPDATE ZECM_REQ gagal | ROLLBACK, RETURN error |

---

## 5. Cara Integrasi di Approver Event Handler

```abap
" Di approve_ecr, SETELAH DMS release dan SEBELUM ECR update:

CALL FUNCTION 'Z_ECM_CREATE_CHANGE_NUMBER'
  EXPORTING
    iv_ecr_no = lv_ecr_no
    iv_title  = ls_ecr-title
    iv_reason = ls_ecr-zreason
    iv_matnr  = ls_ecr-matnr_fg
    iv_dokar  = lv_dokar
    iv_doknr  = lv_doknr
    iv_dokvr  = lv_dokvr
    iv_doktl  = lv_doktl
  IMPORTING
    ev_aennr  = lv_change_no
    ev_success = lv_ecm_ok
    ev_message = lv_ecm_msg.

IF lv_ecm_ok = abap_true.
  " Change Number berhasil — lanjut update ECR
  MV_MESSAGE = |ECR approved. Change No: { lv_change_no }|.
ELSE.
  " Change Number gagal — tapi ECR tetap di-update
  MV_MESSAGE = |ECR approved (WARNING: ECM gagal - { lv_ecm_msg })|.
ENDIF.
```

---

## 6. Prerequisites (Cek di SAP)

| # | Item | TCode | Status |
|---|------|-------|--------|
| 1 | Number Range AENNR | SNRO | ❓ Cek object AENNR, nr 01 |
| 2 | Change Type ZECR | TCC11 / SPRO | ❓ Cek CCART value |
| 3 | AENR table structure | SE11 | ❓ Cek field lengkap |
| 4 | AENR_STATUS structure | SE11 | ❓ Cek field STAT values |
| 5 | AEOI structure | SE11 | ❓ Cek OBJTP values |

---

## 7. Test Plan

| # | Test | Expected | Cek |
|---|------|----------|-----|
| 1 | Approve ECR 13 | AENNR terisi di ZECM_REQ | SE16N ZECM_REQ |
| 2 | Cek AENR | Record baru ada | SE16N AENR |
| 3 | Cek AEOI | Material + DMS link ada | SE16N AEOI |
| 4 | Cek AENR_STATUS | Status tercatat | SE16N AENR_STATUS |
| 5 | CC03 | Display Change Number | CC03 |

---

*Dibuat: 02 Juli 2026*
*Untuk: V05_h — Approve Flow Enhancement*
