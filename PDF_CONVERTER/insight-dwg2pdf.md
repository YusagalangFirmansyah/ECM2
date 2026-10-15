# Insight: DWG to PDF Conversion Research

**Tanggal:** 16 Juli 2026
**Status:** ❌ Belum berhasil (butuh alternatif lain)

---

## Eksperimen yang Sudah Dicoba

| # | Tool | Pipeline | Hasil | Catatan |
|---|------|----------|-------|---------|
| 1 | **ConvertAPI** | DWG → PDF (cloud) | ✅ Berhasil | Berbayar, butuh internet, limit 2500/bulan |
| 2 | **QCAD Trial** | DWG → PDF | ❌ | PDF export = Pro feature (bayar ~€33/tahun) |
| 3 | **FreeCAD** | DWG → PDF | ❌ | Tidak bisa baca DWG tanpa ODA |
| 4 | **LibreOffice** | DWG → PDF | ❌ | Tidak bisa buka DWG langsung |
| 5 | **ODA File Converter** | DWG → DXF/PDF | ❌ | GUI only, butuh display (tidak headless) |
| 6 | **LibreDWG + LibreOffice** | DWG → DXF → PDF | ❌ | DXF→PDF gagal, PDF kosong/blank |
| 7 | **ezdxf** (Python) | DWG → DXF | ❌ | Hanya bisa baca DXF, bukan DWG |

---

## Detail Eksperimen #6: LibreDWG + LibreOffice

### Pipeline
```
DWG → (dwg2dxf) → DXF → (libreoffice --headless) → PDF
```

### Apa yang Terjadi
- **Step 1 (DWG → DXF):** ✅ Berhasil, file DXF 10.5MB terbentuk
  - Banyak warning tentang "Unhandled Class objects" (normal untuk DWG kompleks)
  - Tapi DXF berhasil di-generate
- **Step 2 (DXF → PDF):** ❌ Gagal render
  - PDF terbentuk (61KB) tapi **isi kosong/hampir kosong**
  - LibreOffice Draw tidak bisa render DXF dengan benar
  - Drawing kompleks (dengan layer, block, dimension) hilang

### Root Cause
LibreOffice Draw memiliki **support terbatas** untuk format DXF:
- Tidak support semua entity type (LINE, ARC, CIRCLE OK, tapi BLOCK/INSERT/DIMENSION bermasalah)
- Tidak support AutoCAD-specific features (dynamic blocks, parametric constraints)
- Rendering quality sangat buruk untuk technical drawing

---

## Eksperimen #5: ODA File Converter

### Status
- ✅ Ter-install di srv168 (`/usr/bin/ODAFileConverter`)
- ✅ Bisa convert DWG → DXF (offline, kualitas bagus)
- ❌ **GUI only** — tidak bisa headless tanpa display
- ❌ Xvfb + automation terlalu ribet

### Potensi
ODA File Converter sebenarnya adalah tool terbaik untuk DWG conversion:
- Support semua DWG version
- Kualitas conversion tinggi
- Offline, gratis
- Tapi butuh GUI automation (xdotools)

---

## Rekomendasi untuk Next Time

### Opsi 1: QCAD Pro (~€33/tahun = ~Rp 550rb) ⭐ REKOMENDED
- Headless, scriptable
- DWG → PDF langsung
- Kualitas tinggi
- Sudah terbukti di production

### Opsi 2: ODA File Converter + xdotools automation
- Tool gratis, kualitas tinggi
- Butuh script automation untuk GUI
- Complexity: sedang-tinggi
- Bisa dicoba lagi kalau ada waktu

### Opsi 3: LibreDWG + tool render lain
- LibreDWG sudah bisa convert DWG → DXF ✅
- Cari DXF → PDF converter yang lebih bagus:
  - `dxfgrabber` + `reportlab` (Python)
  - `QCAD` (command line)
  - `Ghostscript` + custom renderer

### Opsi 4: Tetap pakai ConvertAPI
- Sudah jalan, tinggal pakai
- Bayar tapi reliable
- Fokus ke hal lain yang lebih penting

---

## Tool yang Sudah Ter-install di srv168

| Tool | Path | Status |
|------|------|--------|
| LibreDWG (dwg2dxf) | `/usr/local/bin/dwg2dxf` | ✅ Compiled & installed |
| LibreOffice | `/usr/bin/libreoffice` | ✅ Sudah ada |
| ODA File Converter | `/usr/bin/ODAFileConverter` | ✅ Installed (GUI only) |
| xdotool | `/usr/bin/xdotool` | ✅ Installed |
| ezdxf (Python) | pip package | ✅ Installed (DXF only) |
| FreeCAD | `/usr/bin/freecad` | ✅ Installed (no DWG support) |

---

## Script yang Sudah Dibuat

| Script | Path | Fungsi |
|--------|------|--------|
| `dwg2pdf.py` | `/mnt/data/files/sap-docs/ecm/bsp-ecm-app/PDF_CONVERTER/dwg2pdf.py` | Pipeline LibreDWG + LibreOffice (tidak dipakai) |
| `dashboard.py` | `/mnt/data/files/sap-docs/ecm/bsp-ecm-app/PDF_CONVERTER/dashboard.py` | Sudah di-patch pakai `convert_dwg_local` |

---

## Catatan untuk Next Session

1. **Jangan buang waktu** dengan LibreOffice untuk CAD conversion
2. **ODA File Converter** adalah solusi terbaik (gratis + kualitas tinggi), tapi butuh automation
3. **QCAD Pro** adalah solusi termudah (bayar tapi langsung jalan)
4. **ConvertAPI** masih jadi fallback yang reliable
5. Kalau mau coba lagi, fokus ke:
   - ODA + xdotools automation
   - LibreDWG + DXF renderer Python (dxfgrabber + reportlab)

---

*Dibuat: 16 Juli 2026, 18:15 WIB*
