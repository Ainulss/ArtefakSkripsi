import streamlit as st

from sections.common import section

# ==========================================================
# ISI HALAMAN METODE
# Ubah teks di bawah ini sesuai kebutuhan.
# Bagian bertanda [isi ...] belum diisi — ganti dengan penjelasanmu.
# ==========================================================

# ---------------- 1. PENGGABUNGAN DATA ----------------
JUDUL_1 = "1. Penggabungan Data"

PARAGRAF_1 = """
Untuk mengatasi keterbatasan jumlah sampel di tiap kabupaten/kota, data dari wilayah lain
dalam tahun yang sama digabungkan ke data wilayah target. Terdapat 3 pendekatan yang digunakan, yaitu.
"""

# (judul kartu, penjelasan singkat)
PENDEKATAN_PENGGABUNGAN = [
    ("Clustering",
     "Pengelompokkan wilayah dengan algoritma K-Means Clustering berdasarkan 5 variabel, yaitu variabel "
     "median pengeluaran makanan, median pengeluaran nonmakanan, Q1 pengeluaran per kapita, Q2 atau median "
     "pengeluaran per kapita dan Q3 pengeluaran per kapita."),
    ("Pooling data berdasarkan hierarki wilayah",
     "Penggabungan data dari kabupaten/kota lain yang berada di provinsi yang sama."),
    ("Pooling data berdasarkan Kullback-Leibler Divergence",
     "Penggabungkan data dari wilayah lain yang memiliki karakteristik pengeluaran yang sama berdasarkan KL divergence."),
]

# (nama skema, keterangan) — sesuai nama skema pada tabel hasil
SKEMA = [
    ("Clustering versi 1", "Jumlah klaster yang terbentuk berdasarkan elbow plot yaitu 7 untuk kabupaten dan kota."),
    ("Clustering versi 2", "Jumlah klaster yang sudah tetap yaitu 20 untuk kabupaten dan 10 untuk kota."),
    ("Pooling versi 1", "Menggabungkan data sebanyak jumlah kabupaten/kota pada provinsi target dengan ketentuan setengah merupakan data kabupaten/kota target. Jumlah data yang dihasilkan adalah sejumlah data Susenas satu provinsi target."),
    ("Pooling versi 2", "Menggabungkan data lima kabupaten/kota dengan tiga kabupaten/kota target dan dua lainnya adalah kabupaten/kota lain dengan pemisahan antara kabupaten dan kota. Jumlah data yang dihasilkan sejumlah 5 kali data Susenas kabupaten."),
    ("Pooling versi 3", "Menggabungkan data lima kabupaten/kota dengan satu kabupaten/kota target dan empat lainnya adalah kabupaten/kota lain di provinsi yang sama. Jumlah data yang dihasilkan sejumlah 5 kali data Susenas kabupaten,"),
    ("Pooling versi 4", "Menggabungkan data sebanyak jumlah observasi kabupaten/kota target (n) dari lima wilayah dengan karakteristik pengeluaran yang sama berdasarkan KL divergence. Jumlah data yang dihasilkan 2 kali data Susenas kabupaten target."),
    ("Pooling versi 5", "Menggabungkan data sebanyak dua kali jumlah observasi kabupaten/kota target (2n) dari lima wilayah dengan karakteristik pengeluaran yang sama berdasarkan KL divergence. Jumlah data yang dihasilkan 3 kali data Susenas kabupaten target."),
]

# ---------------- 2. PEMODELAN PMT ----------------
JUDUL_2 = "2. Pemodelan PMT"

PARAGRAF_2 = """
Model PMT mengestimasi pengeluaran per kapita rumah tangga menggunakan variabel kesejahteraan,
kemudian mengklasifikasikan rumah tangga sebagai miskin atau tidak miskin berdasarkan ambang
batas tertentu. Pemodelan dilakukan dengan dua algoritma berikut.
"""

ALGORITMA = [
    ("XGBoost Regression",
     "Algoritma machine learning berbasis gradient boosting decision tree yang pada penelitian "
     "sebelumnya menghasilkan estimasi pengeluaran lebih baik dibandingkan regresi linear."),
    ("TabPFN",
     "Tabular Prior-data Fitted Network, algoritma deep learning yang dirancang untuk "
     "data tabular berukuran kecil."),
]


# ==========================================================
# TAMPILAN
# ==========================================================
_CSS = """
<style>
.metode-bagian {font-family: 'Roboto Slab', serif; font-size: 20px; font-weight: 700;
                color: #0d1b2a; margin: 26px 0 6px 0;}
.kartu-grid {display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
             gap: 16px; margin: 6px 0 12px 0;}
.kartu {background: #ffffff; border-radius: 10px; padding: 16px 18px;
        border-top: 4px solid #ffc300; box-shadow: 0 1px 4px rgba(0,0,0,0.08);}
.kartu-judul {font-weight: 700; color: #0d1b2a; font-size: 18px; margin-bottom: 6px;}
.kartu-isi {font-size: 14px; color: #374151; line-height: 1.6; text-align: justify; font-size: 18px;}
.tabel-metode-wrap {max-width: 800px; border-radius: 8px; overflow: hidden;
                    box-shadow: 0 1px 4px rgba(0,0,0,0.08); margin: 6px 0 12px 0;}
.tabel-metode {width: 100%; border-collapse: collapse; font-size: 18px; background: #ffffff;}
.tabel-metode th {background: #0d1b2a; color: #ffffff; text-align: center !important; padding: 7px 12px;}
.tabel-metode td {padding: 6px 12px; vertical-align: top; line-height: 1.5;}
.st-key-sec-metode table.tabel-metode td,
.st-key-sec-metode table.tabel-metode th {border: 1px solid #000000 !important;}
.tabel-metode td:first-child {font-weight: 600; color: #0d1b2a; width: 20%;}
.st-key-sec-metode [data-testid="stMarkdown"] p {
    font-size: 18px;        /* ukuran huruf */
    text-align: justify;    /* rata kanan-kiri */
    line-height: 1.8;       /* spasi antarbaris */
}
</style>
"""


def _kartu(daftar: list) -> str:
    isi = "".join(
        f'<div class="kartu"><div class="kartu-judul">{j}</div><div class="kartu-isi">{k}</div></div>'
        for j, k in daftar
    )
    return f'<div class="kartu-grid">{isi}</div>'


def _tabel(kepala: tuple, baris: list) -> str:
    th = "".join(f"<th>{k}</th>" for k in kepala)
    isi = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in baris)
    return f'<table class="tabel-metode"><tr>{th}</tr>{isi}</table>'


def render():
    st.markdown(_CSS, unsafe_allow_html=True)
    with section("metode", "Metode"):
        # 1. Penggabungan data
        st.markdown(f'<div class="metode-bagian">{JUDUL_1}</div>', unsafe_allow_html=True)
        st.markdown(PARAGRAF_1)
        st.markdown(_kartu(PENDEKATAN_PENGGABUNGAN), unsafe_allow_html=True)
        st.markdown("Skenario penggabungan data antarwilayah:")
        st.markdown(_tabel(("Skenario", "Keterangan"), SKEMA), unsafe_allow_html=True)

        # 2. Pemodelan PMT
        st.markdown(f'<div class="metode-bagian">{JUDUL_2}</div>', unsafe_allow_html=True)
        st.markdown(PARAGRAF_2)
        st.markdown(_kartu(ALGORITMA), unsafe_allow_html=True)