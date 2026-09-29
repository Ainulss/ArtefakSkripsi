"""Menampilkan tabel Excel apa adanya (termasuk sel gabungan/merge) di halaman web.

Pemakaian:
    from sections.tabel_excel import CSS_TABEL_EXCEL, tabel_excel
    st.markdown(CSS_TABEL_EXCEL, unsafe_allow_html=True)      # sekali saja, terpisah
    st.markdown(tabel_excel("data/klaster.xlsx", baris_header=3), unsafe_allow_html=True)

- baris_header : jumlah baris teratas yang dijadikan judul kolom (header)
- Sel gabungan (merge) di Excel otomatis ikut digabung di web.
"""

import html
from pathlib import Path

import streamlit as st
from openpyxl import load_workbook

CSS_TABEL_EXCEL = """
<style>
.xl-scroll {max-height: 480px; overflow: auto; background: #ffffff;
            box-shadow: 0 1px 4px rgba(0,0,0,0.08); margin: 6px 0 16px 0;}
.xl-tabel {border-collapse: separate; border-spacing: 0; font-size: 18px; background: #ffffff;
           white-space: nowrap; width: 100%;}
.xl-tabel th, .xl-tabel td {border-right: 1px solid #000000; border-bottom: 1px solid #000000;
                            padding: 6px 12px;}
.xl-tabel tr > :first-child {border-left: 1px solid #000000;}
.xl-tabel thead tr:first-child th {border-top: 1px solid #000000;}
.xl-tabel thead {position: sticky; top: 0; z-index: 2;}        /* header tetap terlihat saat scroll */
.xl-tabel th {background: #0d1b2a; color: #ffffff; text-align: center; font-weight: 600;
              vertical-align: middle; font-size: 18px !important;}
.xl-tabel td {text-align: center; color: #1f2937;}
.xl-tabel tbody tr:nth-child(even) td {background: #f7f8fa;}
</style>
"""


def _teks(v) -> str:
    """Format isi sel: bilangan bulat diberi titik ribuan (91095 -> 91.095)."""
    if v is None:
        return ""
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, int) or (isinstance(v, float) and v.is_integer()):
        return f"{int(v):,}".replace(",", ".")
    if isinstance(v, float):
        return f"{v:g}"                            # tampil seperti di Excel (pakai titik)         # desimal pakai koma
    return html.escape(str(v))

def _teks_polos(v) -> str:
    """Tampilkan apa adanya tanpa pemisah ribuan (3471.0 -> 3471)."""
    if v is None:
        return ""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return html.escape(str(v))

@st.cache_data
def _baca(path: str, sheet, waktu_ubah: float):
    wb = load_workbook(path, data_only=True)
    ws = wb[sheet] if isinstance(sheet, str) else wb.worksheets[sheet]

    # Batas tabel: baris & kolom terakhir yang berisi
    maks_baris = max((c.row for row in ws.iter_rows() for c in row if c.value is not None), default=0)
    maks_kolom = max((c.column for row in ws.iter_rows() for c in row if c.value is not None), default=0)

    # Peta sel gabungan: sel kiri-atas -> (rowspan, colspan); sel lain di dalamnya dilewati
    gabung, dilewati = {}, set()
    for rg in ws.merged_cells.ranges:
        gabung[(rg.min_row, rg.min_col)] = (rg.max_row - rg.min_row + 1, rg.max_col - rg.min_col + 1)
        for r in range(rg.min_row, rg.max_row + 1):
            for c in range(rg.min_col, rg.max_col + 1):
                if (r, c) != (rg.min_row, rg.min_col):
                    dilewati.add((r, c))

    sel = [[ws.cell(r, c).value for c in range(1, maks_kolom + 1)] for r in range(1, maks_baris + 1)]
    return sel, gabung, dilewati


def tabel_excel(path, sheet=0, baris_header: int = 3, tinggi: int = 480) -> str:
    path = Path(path)
    if not path.exists():
        return f'<div style="color:#b91c1c">File <b>{html.escape(path.name)}</b> tidak ditemukan.</div>'

    sel, gabung, dilewati = _baca(str(path), sheet, path.stat().st_mtime)

    def baris_html(r, tag):
        isi = ""
        for c, v in enumerate(sel[r - 1], start=1):
            if (r, c) in dilewati:
                continue
            rs, cs = gabung.get((r, c), (1, 1))
            # sel gabungan di header tidak boleh menjorok ke bagian data (dan sebaliknya)
            if tag == "th":
                rs = min(rs, baris_header - r + 1)
            atribut = (f' rowspan="{rs}"' if rs > 1 else "") + (f' colspan="{cs}"' if cs > 1 else "")
            isi_sel = _teks_polos(v) if c == 1 else _teks(v)   # kolom pertama = teks
            isi += f"<{tag}{atribut}>{isi_sel}</{tag}>"
        return f"<tr>{isi}</tr>"

    kepala = "".join(baris_html(r, "th") for r in range(1, min(baris_header, len(sel)) + 1))
    badan = "".join(
        baris_html(r, "td") for r in range(baris_header + 1, len(sel) + 1)
        if any(v is not None for v in sel[r - 1])
    )
    return (
        f'<div class="xl-scroll" style="max-height:{tinggi}px">'
        f'<table class="xl-tabel"><thead>{kepala}</thead><tbody>{badan}</tbody></table></div>'
    )