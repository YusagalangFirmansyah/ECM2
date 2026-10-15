#!/usr/bin/env python3
"""
DWG to PDF Converter — LibreDWG + LibreOffice Pipeline
Self-hosted, no external API needed.

Usage:
    python3 dwg2pdf.py input.dwg [output.pdf]

Pipeline: DWG → (LibreDWG) → DXF → (LibreOffice) → PDF
"""

import subprocess
import sys
import os
import tempfile
import shutil
from pathlib import Path


def dwg_to_dxf(input_dwg: str, output_dxf: str) -> bool:
    """Convert DWG to DXF using LibreDWG dwg2dxf."""
    try:
        result = subprocess.run(
            ["dwg2dxf", input_dwg, "-o", output_dxf],
            capture_output=True,
            text=True,
            timeout=120
        )
        # dwg2dxf outputs many warnings, check if output file exists
        if os.path.exists(output_dxf) and os.path.getsize(output_dxf) > 0:
            return True
        else:
            print(f"ERROR: dwg2dxf failed - no output file", file=sys.stderr)
            if result.stderr:
                print(f"STDERR: {result.stderr[:500]}", file=sys.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("ERROR: dwg2dxf timed out after 120s", file=sys.stderr)
        return False
    except FileNotFoundError:
        print("ERROR: dwg2dxf not found. Install LibreDWG first.", file=sys.stderr)
        return False


def dxf_to_pdf(input_dxf: str, output_pdf: str) -> bool:
    """Convert DXF to PDF using LibreOffice Draw."""
    try:
        output_dir = os.path.dirname(output_pdf) or "."
        result = subprocess.run(
            ["libreoffice", "--headless", "--convert-to", "pdf",
             input_dxf, "--outdir", output_dir],
            capture_output=True,
            text=True,
            timeout=120
        )
        # LibreOffice names output based on input filename
        input_stem = Path(input_dxf).stem
        lo_output = os.path.join(output_dir, f"{input_stem}.pdf")

        if os.path.exists(lo_output):
            # Rename if output path differs
            if lo_output != output_pdf:
                shutil.move(lo_output, output_pdf)
            return True
        else:
            print(f"ERROR: LibreOffice failed - no output file", file=sys.stderr)
            if result.stderr:
                print(f"STDERR: {result.stderr[:500]}", file=sys.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("ERROR: LibreOffice timed out after 120s", file=sys.stderr)
        return False
    except FileNotFoundError:
        print("ERROR: libreoffice not found. Install LibreOffice first.", file=sys.stderr)
        return False


def convert_dwg_to_pdf(input_dwg: str, output_pdf: str = None) -> bool:
    """
    Convert DWG file to PDF.
    
    Args:
        input_dwg: Path to input DWG file
        output_pdf: Path to output PDF file (optional, defaults to same name with .pdf)
    
    Returns:
        True if successful, False otherwise
    """
    if not os.path.exists(input_dwg):
        print(f"ERROR: Input file not found: {input_dwg}", file=sys.stderr)
        return False

    if output_pdf is None:
        output_pdf = str(Path(input_dwg).with_suffix(".pdf"))

    # Use temp directory for intermediate DXF
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_dxf = os.path.join(tmpdir, "temp_output.dxf")

        # Step 1: DWG → DXF
        print(f"[1/2] Converting DWG → DXF...")
        if not dwg_to_dxf(input_dwg, tmp_dxf):
            return False
        print(f"      DXF created: {os.path.getsize(tmp_dxf) / 1024:.1f} KB")

        # Step 2: DXF → PDF
        print(f"[2/2] Converting DXF → PDF...")
        if not dxf_to_pdf(tmp_dxf, output_pdf):
            return False
        print(f"      PDF created: {os.path.getsize(output_pdf) / 1024:.1f} KB")

    print(f"\n✅ Success: {output_pdf}")
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 dwg2pdf.py <input.dwg> [output.pdf]")
        print("\nExample:")
        print("  python3 dwg2pdf.py drawing.dwg")
        print("  python3 dwg2pdf.py drawing.dwg output.pdf")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    success = convert_dwg_to_pdf(input_file, output_file)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
