# ECM Bug Fix Insight — DMS Cross-Contamination (v06_g, 17 Jul 2026)

## Bug Description
Drafter submit ECR 20 (material 30012282) tapi DMS yang dipakai adalah DMS 200436 (material 30013453 milik ECR 21). Akibatnya DMS milik ECR 21 hilang karena status berubah dari IA ke AP.

## Root Cause
Logic `submit_ecr` di `drafter_list_event_handler.txt` menggunakan approach yang SALAH untuk deteksi DMS.

### ❌ Salah (lama — V04 approach):
```abap
SELECT doknr FROM draw WHERE dokst = 'IA' AND dokar IN ('DRW','DBX','DMT').
  SELECT SINGLE objky FROM drad WHERE doknr = lv_doknr.
  IF objky = material_ecr → MATCH!
ENDSELECT.
```

Masalah:
1. Loop SEMUA dokumen DMS dengan status 'IA'
2. `SELECT SINGLE` dari DRAD mengembalikan SATU baris ACAK dari 35 entries
3. Tidak filter by material (OBJKY) atau object type (DOKOB)
4. DRAD entries bukan link ke material spesifik — satu DMS bisa punya 35 entries

### ✅ Benar (v06_g — sama dengan UI/OnInit):
```abap
SELECT SINGLE a~doknr, a~dokar, a~dokvr, a~doktl, b~dokst
  FROM drad AS a INNER JOIN draw AS b ON ...
  WHERE a~objky = @lv_matnr_conv
    AND a~dokob = 'MARA'
    AND a~dokar IN ('DRW','DBX','DMT')
    AND b~dokst = 'IA'.
```

Kelebihan:
1. Query langsung ke DRAD by material (OBJKY)
2. Filter object type = MARA (Material Master)
3. Filter kategori dan status
4. ALPHA fallback untuk handle leading zeros

## Key Learnings

1. **DRAD table structure**: Satu DMS document bisa di-link ke BANYAK object (35+ entries). SELECT SINGLE tanpa filter OBJKY mengembalikan baris acak.

2. **Konsistensi UI vs Logic**: Kalau UI (OnInit) dan Event Handler pakai approach berbeda untuk data yang sama, pasti ada yang salah. UI sudah benar, submit yang salah.

3. **DMS detection pattern yang benar**:
   - Query DRAD langsung by material (OBJKY)
   - Filter DOKOB = 'MARA' (Material Master)
   - Filter DOKAR = kategori (DRW/DBX/DMT)
   - Filter DOKST = status target (IA untuk submit)
   - ALPHA fallback untuk handle leading zeros

4. **Testing scenario**: Submit 2 ECR dengan material BERBEDA secara berurutan. Kalau DMS tertukar, berarti detection logic salah.

## Affected Files
- `drafter_list_event_handler.txt` — submit_ecr action (line 238-278)

## Version
- v06_g (17 Jul 2026)

---
*Documented: 17 Juli 2026*
