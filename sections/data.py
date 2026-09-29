import streamlit as st

from sections.common import section

# ==========================================================
# ISI HALAMAN DATA
# Ubah teks / isi tabel di bawah ini sesuai kebutuhan.
# Untuk nilai yang lebih dari satu baris, pisahkan dengan "<br>".
# ==========================================================
PARAGRAF_PEMBUKA = """
Penelitian ini menggunakan data Survei Sosial Ekonomi Nasional (Susenas) yang
diperoleh dari Badan Pusat Statistik (BPS). Data yang digunakan merupakan gabungan dari dua
kuesioner Susenas, yaitu kuesioner Kor dan modul Konsumsi/Pengeluaran (KP). Kuesioner Kor
mencakup keterangan individu dan rumah tangga seperti karakteristik demografi, pendidikan,
kesehatan, dan perumahan, sedangkan modul KP mencakup pengeluaran rumah tangga. 
"""


PARAGRAF_VARIABEL = """
Model PMT dibangun menggunakan variabel yang menggambarkan tingkat kesejahteraan rumah tangga, 
sedangkan clustering menggunakan variabel pengeluaran. Rincian kedua kelompok variabel tersebut disajikan pada tabel berikut.
"""

VARIABEL_INDIVIDU = [
    ("Umur", "Numerik"),
    ("Jenis kelamin", "1 = Laki-laki<br>2 = Perempuan"),
    ("Status pendidikan", "1 = Tidak/belum pernah bersekolah<br>2 = Masih bersekolah<br>"
                          "3 = Tidak bersekolah lagi"),
    ("Ijazah tertinggi", "1–5 = SD sederajat<br>6–10 = SMP sederajat<br>11–17 = SMA sederajat<br>"
                         "18–19 = Diploma<br>20–24 = Strata<br>25 = Tidak punya ijazah SD"),
    ("Status perkawinan", "1 = Belum kawin<br>2 = Kawin<br>3 = Cerai hidup<br>4 = Cerai mati"),
    ("Pekerjaan utama", "1–6 = Pertanian<br>7–9, 11 = Nonpertanian<br>10, 12–26 = Jasa"),
    ("Status dalam pekerjaan utama", "1 = Berusaha sendiri<br>2 = Berusaha dibantu buruh tidak tetap<br>"
                                     "3 = Berusaha dibantu buruh tetap<br>4 = Buruh/karyawan/pegawai<br>"
                                     "5 = Pekerja bebas<br>6 = Pekerja keluarga"),
]

VARIABEL_RUMAH_TANGGA = [
    ("Status kepemilikan rumah", "1 = Milik sendiri<br>2 = Kontrak/sewa<br>3 = Bebas sewa<br>"
                                 "4 = Rumah dinas<br>5 = Lainnya"),
    ("Jenis lantai", "1 = Marmer/granit<br>2 = Keramik<br>3 = Parket/vinil/karpet<br>"
                     "4 = Ubin/tegel/teraso<br>5 = Kayu/papan<br>6 = Semen/bata merah<br>"
                     "7 = Bambu<br>8 = Tanah<br>9 = Lainnya"),
    ("Jenis dinding", "1 = Tembok<br>2 = Plesteran anyaman bambu/kawat<br>"
                      "3 = Kayu/papan/gypsum/GRC/calciboard<br>4 = Anyaman bambu<br>"
                      "5 = Batang kayu<br>6 = Bambu<br>7 = Lainnya"),
    ("Jenis atap", "1 = Beton<br>2 = Genteng<br>3 = Seng<br>4 = Asbes<br>5 = Bambu<br>"
                   "6 = Kayu/sirap<br>7 = Jerami/ijuk/daun-daunan/rumbia<br>8 = Lainnya"),
    ("Sumber air minum", "1 = Air kemasan bermerk<br>2 = Air isi ulang<br>3 = Leding<br>"
                         "4 = Sumur bor/pompa<br>5 = Sumur terlindung<br>6 = Sumur tak terlindung<br>"
                         "7 = Mata air terlindung<br>8 = Mata air tak terlindung<br>"
                         "9 = Air permukaan<br>10 = Air hujan<br>11 = Lainnya"),
    ("Sumber listrik", "1 = Listrik PLN dengan meteran<br>2 = Listrik PLN tanpa meteran<br>"
                       "3 = Listrik non-PLN<br>4 = Bukan listrik"),
    ("Daya listrik", "1 = 450 watt<br>2 = 900 watt<br>3 = 1.300 watt atau lebih"),
    ("Jenis bahan bakar untuk memasak", "1 = Listrik<br>2 = Gas elpiji 5,5 kg<br>3 = Gas elpiji 12 kg<br>"
                                        "4 = Gas elpiji 3 kg<br>5 = Gas kota/meteran PGN<br>6 = Biogas<br>"
                                        "7 = Minyak tanah<br>8 = Briket<br>9 = Arang<br>10 = Kayu bakar<br>"
                                        "11 = Lainnya<br>0 = Tidak memasak di rumah"),
    ("Jenis toilet", "1 = Leher angsa<br>2 = Plengsengan dengan tutup<br>3 = Plengsengan tanpa tutup<br>"
                     "4 = Cemplung/cubluk"),
    ("Jenis sanitasi", "1 = Tangki septik<br>2 = IPAL<br>3 = Kolam/sawah/sungai/danau/laut<br>"
                       "4 = Lubang tanah<br>5 = Pantai/tanah lapang/kebun<br>6 = Lainnya"),
    ("Kepemilikan aset", "Tabung gas 5,5 kg atau lebih · Kulkas · AC · Pemanas air · Telepon rumah · "
                         "Komputer · Emas · Sepeda motor · Perahu · Perahu motor · Mobil · TV · "
                         "Tanah · Telepon seluler"),
    ("Jumlah keluarga", "Numerik"),
    ("Luas lantai", "Numerik"),
]

VARIABEL_PENGELUARAN = [
    ("Pengeluaran makanan", "Numerik"),
    ("Pengeluaran nonmakanan", "Numerik"),
    ("Pengeluaran per kapita", "Numerik"),
]

# True = kode nilai ditulis berderet dalam satu paragraf (tabel lebih pendek)
# False = satu kode per baris
NILAI_BERDERET = False



# ==========================================================
# TAMPILAN
# ==========================================================
_CSS = """
<style>
/* ---- Ukuran tabel: ubah angka di bawah ini ---- */
.tabel-wrap {max-width: 1250px; margin: 0 auto;}          /* lebar maksimum tabel */
.tabel-scroll {max-height: 420px; overflow-y: auto; border-radius: 0px;   /* tinggi area scroll */
               box-shadow: 0 1px 4px rgba(0,0,0,0.08); background: #ffffff;}
.tabel-data {width: 100%; border-collapse: collapse; font-size: 18px; background: #ffffff;}
.tabel-data th {background: #0d1b2a; color: #ffffff; text-align: center !important; padding: 6px 10px;
                font-weight: 600; position: sticky; top: -1px; z-index: 1;}   /* judul kolom tetap terlihat */
.tabel-data td {padding: 5px 10px; vertical-align: top;
                line-height: 1.4;}
.tabel-data td.var {font-weight: 600; color: #0d1b2a; width: 28%;}
.tabel-data td.ket {color: #374151; width: 16%; background: #f7f8fa; font-weight: 600;
                    vertical-align: middle; text-align: center;}
/* Garis tabel (semua sisi). !important supaya tidak tertimpa gaya bawaan Streamlit */
.st-key-sec-data table.tabel-data td,
.st-key-sec-data table.tabel-data th {border: 1px solid #000000 !important;}
.tabel-judul {font-weight: 700; color: #0d1b2a; margin: 6px 0 6px 0; font-size: 14px;}
.tabel-sumber {font-size: 11px; color: #6b7280; margin: 4px 0 16px 0;}
.st-key-sec-data button[data-baseweb="tab"] p {font-size: 18px !important;}   /* tulisan tab */
</style>
"""


def _nilai(n: str) -> str:
    return n.replace("<br>", "; ") if NILAI_BERDERET else n


def _tabel(kepala: tuple, baris: list) -> str:
    """Tabel 2 kolom: Variabel | Nilai."""
    th = "".join(f"<th>{k}</th>" for k in kepala)
    isi = "".join(f'<tr><td class="var">{v}</td><td>{_nilai(n)}</td></tr>' for v, n in baris)
    return (
        f'<div class="tabel-wrap">'
        f'<div class="tabel-scroll"><table class="tabel-data"><tr>{th}</tr>{isi}</table></div></div>'
    )


def _tabel_pmt(kelompok: list) -> str:
    """Tabel 3 kolom: Variabel | Keterangan | Nilai.
    kelompok = [(keterangan, daftar_variabel), ...]; sel Keterangan digabung per kelompok."""
    isi = ""
    for ket, daftar in kelompok:
        for i, (v, n) in enumerate(daftar):
            sel_ket = f'<td class="ket" rowspan="{len(daftar)}">{ket}</td>' if i == 0 else ""
            isi += f'<tr><td class="var">{v}</td>{sel_ket}<td>{_nilai(n)}</td></tr>'
    return (
        f'<div class="tabel-wrap">'
        f'<div class="tabel-scroll"><table class="tabel-data"><tr><th>Variabel</th><th>Keterangan</th><th>Nilai</th></tr>{isi}</table></div></div>'
    )


def render():
    st.markdown(_CSS, unsafe_allow_html=True)
    with section("data", "Data"):
        st.markdown(PARAGRAF_PEMBUKA)

        st.markdown(PARAGRAF_VARIABEL)
        tab1, tab2 = st.tabs(["Variabel PMT", "Variabel Clustering"])
        with tab1:
            st.markdown(
                _tabel_pmt([
                    ("Variabel individu", VARIABEL_INDIVIDU),
                    ("Variabel rumah tangga", VARIABEL_RUMAH_TANGGA),
                ]),
                unsafe_allow_html=True,
            )
        with tab2:
            st.markdown(
                _tabel( ("Variabel", "Nilai"), VARIABEL_PENGELUARAN),
                unsafe_allow_html=True,
            )