from pathlib import Path

import streamlit as st
import base64
from pathlib import Path
from sections import peta
from sections.common import section
from sections.tabel_excel import CSS_TABEL_EXCEL, tabel_excel

# ==========================================================
# PENGATURAN HALAMAN HASIL
# Bagian bertanda [isi ...] belum diisi — ganti dengan teksmu.
# ==========================================================
DATA_DIR = Path(__file__).parent.parent / "data"

UKURAN_FONT = 18         # ukuran huruf paragraf, tab, dan tabel (piksel)
UKURAN_SUBJUDUL = 20     # ukuran huruf subjudul 1, 2, 3 (piksel)
TINGGI_TABEL = 480       # tinggi area scroll tabel (piksel)

# ---------------- 1. PENGGABUNGAN DATA ANTARWILAYAH ----------------
JUDUL_1 = "1. Penggabungan Data Antarwilayah"
PARAGRAF_1 = """
Hasil penggabungan data antarwilayah untuk setiap pendekatan disajikan pada tabel berikut.
"""
# Tab: (nama tab, file Excel di folder data/, jumlah baris header)
TAB_PENGGABUNGAN = [
    ("Clustering", DATA_DIR / "klaster.xlsx", 3),
    ("Pooling", DATA_DIR / "pooling.xlsx", 3),
]

# ---------------- 2. MODELING DAN EVALUASI PMT ----------------
JUDUL_2 = "2. Modeling dan Evaluasi PMT"
TAMPILKAN_PETA = True    # peta hasil evaluasi per kabupaten/kota

# Kotak kesimpulan di akhir bagian 2 (kosongkan "" kalau tidak ingin ditampilkan)
KESIMPULAN_2 = (
    "Berdasarkan evaluasi IE/EE dan RMSE, model terbaik diperoleh dari <b>pooling versi 1 "
    "dengan algoritma TabPFN</b>. Hasil ini menunjukkan bahwa penggabungan data kabupaten/kota lain dalam "
    "provinsi yang sama menghasilkan estimasi pengeluaran per kapita dan klasifikasi rumah "
    "tangga miskin yang lebih baik dibandingkan penggabungan data lintas tahun maupun "
    "penggunaan data satu tahun. Selain itu, TabPFN yang dirancang untuk data berukuran kecil "
    "menunjukkan kinerja lebih baik dibanding XGBoost Regression."
)

# ---------------- 3. ANALISIS MODEL PMT ----------------
JUDUL_3 = "3. Analisis Model PMT"
PARAGRAF_3 = """
"""
# Folder gambar grafik (buat folder "gambar" sejajar dengan LandingPage.py)
GAMBAR_DIR = Path(__file__).parent.parent / "Gambar"

# Setiap karakteristik: judul, gambar EE (kiri), gambar IE (kanan),
# kotak kesimpulan di bawah masing-masing gambar, lalu satu kotak kesimpulan utuh.
# Kosongkan teks "" kalau kotaknya tidak ingin ditampilkan.
KARAKTERISTIK = [
    {
        "judul": "Jumlah Anggota Rumah Tangga",
        "folder": "Anggota", 
        "gambar_ee": "EE.png",
        "gambar_ie": "IE.png",
        "kesimpulan_ee": "Rumah tangga miskin dengan 1 anggota secara konsisten memiliki risiko salah klasifikasi yang lebih tinggi dibandingkan rumah tangga dengan lebih dari 1 anggota.",
        "kesimpulan_ie": "Rumah tangga tidak miskin dengan 1 anggota menghasilkan kesalahan klasifikasi yang lebih rendah dibandingkan rumah tangga dengan lebih dari 1 anggota.",
        "kesimpulan": "Karakteristik rumah tangga tidak miskin yang diklasifikasikan sebagai miskin adalah rumah tangga yang menggunakan minyak tanah, briket, arang atau kayu bakar "
        "untuk memasak. Selain itu, rumah tangga tersebut juga menggunakan listrik 450 kWh dan minum dengan air sumur bor, sumur terlindungi, atau mata air terlindungi. Karakteristik tersebut "
        "mendorong pengeluaran mereka rendah sehingga diklasifikasikan ke desil 1 hingga 4. <br><br>Karakteristik rumah tangga dengan 1 anggota yang mengalami exclusion error yaitu sedikit anggota "
        "yang bekerja di sektor pertanian, jumlah anggota keluarga berjenis kelamin perempuan sedikit, dan tidak menggunakna listrik 450 kWh. ",
    },
    {
        "judul": "Jenis Kelamin Kepala Rumah Tangga",
        "folder": "KRT", 
        "gambar_ee": "EE.png",
        "gambar_ie": "IE.png",
        "kesimpulan_ee": "Rumah tangga miskin dengan KRT perempuan secara konsisten memiliki risiko salah klasifikasi yang lebih tinggi dibandingkan rumah tangga dengan KRT laki-laki.",
        "kesimpulan_ie": "Rumah tangga tidak miskin dengan KRT perempuan lebih jarang mengalami salah klasifikasi dibandingkan rumah tangga dengan KRT laki-laki.",
        "kesimpulan": "Exclusion error pada rumah tangga dengan KRT perempuan banyak terjadi pada rumah tangga dengan jumlah anggota yang sedikit, sedikit yang bekerja "
        "di sektor pertanian, rumah tangga yang memiliki motor, kulkas, dan lantai yang luas. Model mengestimasi rumah tangga tersebut memiliki pengeluaran yang tinggi,"
        "padahal kondisi ekonomi sebenarnya berada pada kelompok pengeluaran rendah. <br><br>Rumah tangga tidak miskin dengan KRT perempuan yang mengalami inclusion error memiliki "
        "karakteristik jumlah anggota yang lebih banyak, memiliki banyak anggota yang berusaha di sektor pertanian, rumah tangga yang tidak memiliki motor, kulkas, dan "
        "lantai yang kecil. Karakteristik tersebut oleh model diestimasi memiliki pengeluaran yang rendah, padahal kondisi ekonomi sebenarnya memiliki penghasilan yang "
        "tinggi. ",
    },
    {
        "judul": "Keberadaan Lansia Dalam Rumah Tangga",
        "folder": "Lansia", 
        "gambar_ee": "EE.png",
        "gambar_ie": "IE.png",
        "kesimpulan_ee": "Keberadaan lansia dalam rumah tangga meningkatkan risiko kesalahan klasifikasi pada threshold menengah dan tinggi, tetapi menghasilkan risiko yang lebih kecil pada threshold rendah.",
        "kesimpulan_ie": "Keberadaan lansia tidak memberikan perbedaan kesalahan yang sangat berbeda terhadap inclusion error, meskipun rumah tangga dengan lansia cenderung memiliki risiko kesalahan yang sedikit lebih rendah di setiap threshold.",
        "kesimpulan": "Rumah tangga dengan lansia yang mengalami exclusion error memiliki karakteristik rumah tangga dengan jumlah anggota yang sedikit, memiliki sedikit anggota yang bekerja di sektor pertanian, "
        "jumlah anggota perempuan yang sedikit, rumah tangga yang memiliki motor, kulkas, dan lantai yang luas. Model mengestimasi rumah tangga tersebut memiliki pengeluaran yang tinggi, padahal kondisi ekonomi sebenarnya "
        "berada pada kelompok pengeluaran rendah. <br><br>Rumah tangga tidak miskin dengan lansia yang mengalami inclusion error memiliki karakteristik yang sama dengan rumah tangga tidak miskin dengan KRT perempuan, yaitu rumah tangga dengan jumlah "
        "anggota yang lebih banyak, memiliki banyak anggota yang berusaha di sektor pertanian, rumah tangga yang tidak memiliki motor, kulkas, dan lantai yang kecil.",
    },
    {
        "judul": "Jumlah Keluarga Dalam Rumah Tangga",
        "folder": "Keluarga", 
        "gambar_ee": "EE.png",
        "gambar_ie": "IE.png",
        "kesimpulan_ee": "Rumah tangga miskin dengan lebih dari 1 keluarga memiliki risiko salah klasifikasi yang lebih rendah dibandingkan rumah tangga dengan 1 keluarga.",
        "kesimpulan_ie": "Rumah tangga tidak miskin dengan lebih dari 1 keluarga memiliki risiko salah klasifikasi yang lebih tinggi dibandingkan rumah tangga dengan 1 keluarga.",
        "kesimpulan": "Exclusion error pada rumah tangga dengan lebih dari 1 keluarga memiliki karakteristik jumlah anggota rumah tangga yang sedikit dan jumlah anggota yang bekerja "
        "di sektor pertanian yang sedikit. Kelompok ini juga ditemukan memiliki aset berupa motor dan kulkas. Selain itu, rumah tangga dengan lantai yang luas dan menggunakan marmer, "
        "keramik, atau parket diestimasi memiliki pengeluaran yang lebih tinggi. <br><br>Rumah tangga tidak miskin dengan lebih dari 1 keluarga yang mengalami inclusion error umumnya "
        "memiliki jumlah anggota rumah tangga yang lebih banyak. Karakteristik lainnya yang banyak ditemukan adalah jumlah anggota yang bekerja di sektor pertanian, anggota perempuan, "
        "dan anggota yang belum menikah yang banyak. Selain itu, rumah tangga yang tidak memiliki motor, kulkas, dan lantai yang tidak luas diestimasi memiliki pengeluaran yang lebih rendah.",
    },
]


# ==========================================================
# TAMPILAN
# ==========================================================
def _css() -> str:
    return f"""
<style>
.hasil-subjudul {{font-family: 'Roboto Slab', serif; font-size: {UKURAN_SUBJUDUL}px; font-weight: 700;
                 color: #0d1b2a; margin: 28px 0 6px 0;}}
.st-key-sec-hasil [data-testid="stMarkdown"] p {{font-size: {UKURAN_FONT}px !important;
                                                text-align: justify; line-height: 1.8;}}
.st-key-sec-hasil button[data-baseweb="tab"] p {{font-size: {UKURAN_FONT}px !important;}}
.st-key-sec-hasil [data-testid="stSelectbox"] label p {{font-size: {UKURAN_FONT}px !important;}}
.st-key-sec-hasil .xl-tabel th, .st-key-sec-hasil .xl-tabel td {{font-size: {UKURAN_FONT}px !important;}}
.kotak-kesimpulan {{background: #0d1b2a; color: #ffffff; border-radius: 12px;
                   border-left: 6px solid #ffc300; padding: 20px 24px; margin: 20px 0;
                   font-size: {UKURAN_FONT}px; line-height: 1.8; text-align: justify;
                   box-shadow: 0 2px 8px rgba(0,0,0,0.12);}}
.kotak-kesimpulan b {{color: #ffc300;}}
.karakteristik-judul {{font-size: {UKURAN_FONT}px; font-weight: 700; text-align: center;
                      color: #0d1b2a; margin: 32px 0 12px 0;}}
.label-gambar {{font-size: {UKURAN_FONT}px; font-weight: 700; text-align: center;
               color: #0d1b2a; margin-bottom: 6px;}}
.gambar-grafik {{width: 100%; height: auto; display: block; border: 1px solid #d1d5db;
                background: #ffffff;}}
.gambar-kosong {{border: 1px dashed #9ca3af; padding: 40px 12px; text-align: center;
                color: #6b7280; font-size: 16px; background: #f9fafb;}}
</style>
"""

@st.cache_data
def _gambar_base64(path: str, waktu_ubah: float) -> str:
    return base64.b64encode(Path(path).read_bytes()).decode()


def _gambar(nama_file: str, label: str):
    """Label (EE/IE) + gambar selebar kolom. Kalau file belum ada, tampil kotak petunjuk."""
    path = GAMBAR_DIR / nama_file
    if path.exists():
        jenis = "svg+xml" if path.suffix.lower() == ".svg" else path.suffix.lower().lstrip(".").replace("jpg", "jpeg")
        data = _gambar_base64(str(path), path.stat().st_mtime)
        isi = f'<img class="gambar-grafik" src="data:image/{jenis};base64,{data}">'
    else:
        isi = f'<div class="gambar-kosong">Gambar belum ada.<br>Simpan sebagai <code>gambar/{nama_file}</code></div>'
    st.markdown(f'<div class="label-gambar">{label}</div>{isi}', unsafe_allow_html=True)


def _kotak(teks: str):
    if teks:
        st.markdown(f'<div class="kotak-kesimpulan">{teks}</div>', unsafe_allow_html=True)

def _subjudul(teks: str):
    st.markdown(f'<div class="hasil-subjudul">{teks}</div>', unsafe_allow_html=True)


def render():
    # CSS harus di st.markdown tersendiri (terpisah dari tabel)
    st.markdown(CSS_TABEL_EXCEL, unsafe_allow_html=True)
    st.markdown(_css(), unsafe_allow_html=True)

    with section("hasil", "Hasil"):
        # ---------- 1. Penggabungan data antarwilayah ----------
        _subjudul(JUDUL_1)
        st.markdown(PARAGRAF_1)
        tabs = st.tabs([nama for nama, _, _ in TAB_PENGGABUNGAN])
        for tab, (nama, file, header) in zip(tabs, TAB_PENGGABUNGAN):
            with tab:
                if file.exists():
                    st.markdown(tabel_excel(file, baris_header=header, tinggi=TINGGI_TABEL),
                                unsafe_allow_html=True)
                else:
                    st.info(f"Tabel {nama} belum tersedia. Simpan file Excel-nya sebagai "
                            f"`data/{file.name}`.")

        # ---------- 2. Modeling dan evaluasi PMT ----------
        _subjudul(JUDUL_2)
        if TAMPILKAN_PETA:
            peta.render()
        if KESIMPULAN_2:
            st.markdown(
                f'<div class="kotak-kesimpulan">{KESIMPULAN_2}</div>',
                unsafe_allow_html=True,
            )

        # ---------- 3. Analisis model PMT ----------
        _subjudul(JUDUL_3)
        if PARAGRAF_3.strip():
            st.markdown(PARAGRAF_3)
        for k in KARAKTERISTIK:
            st.markdown(f'<div class="karakteristik-judul">{k["judul"]}</div>', unsafe_allow_html=True)
            kiri, kanan = st.columns(2, gap="large")
            with kiri:
                _gambar(f'{k["folder"]}/{k["gambar_ee"]}', "Exclusion Error (EE)")
                _kotak(k["kesimpulan_ee"])
            with kanan:
                _gambar(f'{k["folder"]}/{k["gambar_ie"]}', "Inclusion Error (IE)")
                _kotak(k["kesimpulan_ie"])
            _kotak(k["kesimpulan"])