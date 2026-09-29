"""Peta interaktif hasil evaluasi per kabupaten/kota.

Peta tampil selebar halaman. Pilih metrik di atas peta, lalu klik wilayah:
popup menampilkan nilai metrik tersebut untuk setiap skema dan model
(XGBoost, TabPFN, ...), beserta train size dan test size.

File yang dipakai (folder data/):
  - wilayah.geojson  -> batas wilayah. Properti: "kode", "wilayah", "provinsi".
  - DATA_FILE        -> file Excel hasil evaluasi dengan HEADER 3 BARIS:
        baris 1: nama kolom identitas (district_train, district_test, train, test)
                 dan nama metrik (IE20, IE40, RMSE, Akurasi 20%, Taudc1, ...,
                 train_size, test_size) — boleh sel gabungan (merge)
        baris 2: nama model (XGBoost, TabPFN, ...) — boleh sel gabungan
        baris 3: nama skema (baseline 1, baseline 2, C V1, P V1, ...)
     Data mulai baris 4, satu baris per kabupaten/kota (per pasangan tahun).
"""

import copy
import html
import json
from pathlib import Path

import folium
import pandas as pd
import streamlit as st
from folium import plugins
from streamlit_folium import st_folium

# ==========================================================
# PENGATURAN — sesuaikan dengan data kamu
# ==========================================================
DATA_DIR = Path(__file__).parent.parent / "data"
GEOJSON_FILE = DATA_DIR / "wilayah.geojson"
DATA_FILE = DATA_DIR / "indikator_wilayah.xlsx"   # file Excel hasil evaluasi (header 3 baris)
NAMA_SHEET = 0                                    # 0 = sheet pertama, atau tulis nama sheet

# Nama kolom identitas di baris header pertama
KOLOM_KODE_DATA = "district_test"   # kode kab/kota yang dicocokkan dengan peta
KOLOM_TRAIN = "train"               # tahun data latih
KOLOM_TEST = "test"                 # tahun data uji
KOLOM_TRAIN_SIZE = "train_size"     # (per skema) jumlah data latih
KOLOM_TEST_SIZE = "test_size"       # jumlah data uji

# Arah "lebih baik" tiap metrik, dicocokkan dari awal nama metrik.
# "rendah" = makin kecil makin baik, "tinggi" = makin besar makin baik.
ARAH_METRIK = {
    "IE": "rendah",
    "RMSE": "rendah",
    "Akurasi": "tinggi",
    "Tau": "tinggi",
}

# Pilihan di dropdown peta: {nama pilihan: [metrik yang ditampilkan di popup]}
# Nama metrik harus sama persis dengan header Excel. Urutan = urutan dropdown.
GRUP_METRIK = {
    "IE/EE Threshold 20%": ["IE20"],
    "IE/EE Threshold 40%": ["IE40"],
    "IE/EE Threshold 60%": ["IE60"],
    "RMSE": ["RMSE"],
}

# Nama kolom di GeoJSON
KOLOM_KODE = "kode"
KOLOM_WILAYAH = "wilayah"

# ---------------- Tampilan peta ----------------
# Pilihan peta dasar (bisa diganti lewat tombol layer di pojok kanan atas peta).
# Yang pertama = tampilan awal. Isi [] untuk peta TANPA peta dasar.
PETA_DASAR = [
    ("OpenStreetMap", "OpenStreetMap"),
]
# Tambahan lain yang bisa dimasukkan ke daftar di atas kalau diperlukan:
#   ("CartoDB positron", "Peta terang (CARTO)"),
#   ("Esri.WorldImagery", "Citra satelit (Esri)"),

WARNA_LATAR_PETA = "#eef2f6"   # warna latar kalau tanpa peta dasar
WARNA_WILAYAH = "#3b7fbf"      # warna wilayah yang punya data
WARNA_TANPA_DATA = "#c7ccd3"   # warna wilayah yang tidak ada di file Excel
TRANSPARANSI_WARNA = 0.85      # 0 = bening, 1 = pekat
WARNA_GARIS_BATAS = "#333333"  # garis batas antar wilayah
TAMPILKAN_NAMA_WILAYAH = False # True = tulis nama wilayah di tengah poligon
TINGGI_PETA = 600              # tinggi peta (piksel); lebarnya selalu penuh

# (Opsional) tampilkan hanya provinsi tertentu, pakai kode provinsi 2 digit.
# Contoh: ["34"] = hanya DI Yogyakarta. Kosongkan ([]) untuk seluruh Indonesia.
FILTER_KODE_PROV = []

# Keterangan sumber batas wilayah (ditampilkan kecil di bawah peta).

# (Opsional) titik lokasi. File harus punya kolom "lat" dan "lon".
TITIK_FILE = DATA_DIR / "titik_sampel.xlsx"   # boleh .xlsx atau .csv
WARNA_TITIK = "#e8401c"


# ==========================================================
# MEMBACA DATA
# ==========================================================
def _rapikan_kode(x) -> str:
    """Samakan format kode: 3471, "3471", 3471.0, "34.71" -> "3471"."""
    s = str(x).strip()
    if s.endswith(".0"):
        s = s[:-2]
    return s.replace(".", "")


def _teks(x) -> str:
    return "" if pd.isna(x) else str(x).strip()


# Argumen waktu_ubah (waktu terakhir file diubah) membuat cache otomatis
# diperbarui saat file diganti/diedit.
@st.cache_data
def load_geojson(waktu_ubah: float = 0, filter_prov: tuple = ()) -> dict:
    gj = json.loads(GEOJSON_FILE.read_text(encoding="utf-8"))
    for f in gj["features"]:
        f["properties"][KOLOM_KODE] = _rapikan_kode(f["properties"][KOLOM_KODE])
    if filter_prov:
        gj["features"] = [
            f for f in gj["features"]
            if str(f["properties"].get("kode_prov", f["properties"][KOLOM_KODE][:2])) in filter_prov
        ]
    return gj


@st.cache_data
def load_hasil(waktu_ubah: float = 0) -> pd.DataFrame:
    """Baca Excel ber-header 3 baris menjadi tabel panjang:
    kode | train | test | test_size | metrik | model | skema | nilai
    """
    if DATA_FILE.suffix.lower() in (".xlsx", ".xls"):
        raw = pd.read_excel(DATA_FILE, sheet_name=NAMA_SHEET, header=None, dtype=object)
    else:
        raw = pd.read_csv(DATA_FILE, header=None, dtype=object, sep=None, engine="python",
                          encoding="utf-8-sig")
    if len(raw) < 4:
        raise ValueError(f"`{DATA_FILE.name}` harus punya 3 baris header dan minimal 1 baris data.")

    # --- Susun header 3 baris (isi sel gabungan yang kosong) ---
    baris1 = raw.iloc[0].map(_teks).replace("", pd.NA).ffill().fillna("")
    baris2, baris3 = [], []
    model_sebelumnya, grup_sebelumnya = "", None
    for j in range(raw.shape[1]):
        grup = baris1.iloc[j]
        m = _teks(raw.iat[1, j])
        if grup != grup_sebelumnya:          # metrik baru -> model mulai dari kosong
            model_sebelumnya = ""
        if m:
            model_sebelumnya = m
        baris2.append(model_sebelumnya)
        baris3.append(_teks(raw.iat[2, j]))
        grup_sebelumnya = grup

    kolom = list(zip(baris1.str.strip(), baris2, baris3))
    data = raw.iloc[3:].dropna(how="all").reset_index(drop=True)

    def cari(nama):
        for j, (a, b, c) in enumerate(kolom):
            if a.lower() == nama.lower() and not b and not c:
                return j
        return None

    j_kode, j_train, j_test, j_ts = (cari(KOLOM_KODE_DATA), cari(KOLOM_TRAIN),
                                     cari(KOLOM_TEST), cari(KOLOM_TEST_SIZE))
    if j_kode is None:
        raise ValueError(
            f"Kolom `{KOLOM_KODE_DATA}` tidak ditemukan di baris header pertama `{DATA_FILE.name}`. "
            f"Kolom identitas yang terbaca: {', '.join(a for a, b, c in kolom if a and not b and not c)}"
        )

    identitas = pd.DataFrame({
        "kode": data.iloc[:, j_kode].map(_rapikan_kode),
        "train": data.iloc[:, j_train].map(_rapikan_kode) if j_train is not None else "",
        "test": data.iloc[:, j_test].map(_rapikan_kode) if j_test is not None else "",
        "test_size": pd.to_numeric(data.iloc[:, j_ts], errors="coerce") if j_ts is not None else pd.NA,
    })

    # --- Ubah kolom metrik menjadi baris (format panjang) ---
    potongan = []
    for j, (metrik, model, skema) in enumerate(kolom):
        if not skema:                          # kolom identitas / test_size
            continue
        nilai = pd.to_numeric(
            data.iloc[:, j].astype(str).str.strip().str.replace(",", ".", regex=False),
            errors="coerce",
        )
        potongan.append(identitas.assign(metrik=metrik, model=model, skema=skema, nilai=nilai.values))
    if not potongan:
        raise ValueError(f"Tidak ada kolom metrik yang terbaca di `{DATA_FILE.name}`. Cek 3 baris header.")
    return pd.concat(potongan, ignore_index=True)


@st.cache_data
def load_titik(waktu_ubah: float = 0) -> pd.DataFrame:
    """Baca file titik lokasi (kolom wajib: lat, lon)."""
    if TITIK_FILE.suffix.lower() in (".xlsx", ".xls"):
        t = pd.read_excel(TITIK_FILE)
    else:
        t = pd.read_csv(TITIK_FILE, sep=None, engine="python", encoding="utf-8-sig")
    t.columns = t.columns.str.strip().str.lower()
    t = t.rename(columns={"latitude": "lat", "longitude": "lon", "lng": "lon", "long": "lon"})
    if not {"lat", "lon"} <= set(t.columns):
        return pd.DataFrame()
    for k in ("lat", "lon"):
        t[k] = pd.to_numeric(t[k].astype(str).str.replace(",", ".", regex=False), errors="coerce")
    return t.dropna(subset=["lat", "lon"])


# ==========================================================
# FORMAT & POPUP
# ==========================================================
def _arah(metrik: str) -> str:
    for awalan, arah in ARAH_METRIK.items():
        if metrik.lower().startswith(awalan.lower()):
            return arah
    return "tinggi"


def _angka(nilai, metrik: str) -> str:
    if nilai is None or pd.isna(nilai):
        return "-"
    if metrik == "_bulat":
        return f"{nilai:,.0f}".replace(",", ".")
    if metrik.upper().startswith("RMSE") or abs(nilai) >= 1000:
        return f"{nilai:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")   # 623.229,54
    return f"{nilai:.4f}"


def _html_popup(props: dict, baris: pd.DataFrame, metrik_grup: list) -> str:
    """Popup: nama wilayah + tabel (baris = skema, kolom = metrik x model).
    Nilai terbaik tiap metrik ditandai kuning."""
    kepala = (
        f'<div class="pp-judul">{html.escape(str(props.get(KOLOM_WILAYAH, "")))} '
        f'({html.escape(str(props.get(KOLOM_KODE, "")))})</div>'
    )
    if baris.empty:
        return kepala + '<div class="pp-kosong">Tidak ada data untuk wilayah ini.</div>'

    d = baris[baris["metrik"].isin(metrik_grup)].drop_duplicates(["skema", "metrik", "model"])
    metrik_ada = [m for m in metrik_grup if m in set(d["metrik"])]
    model_list = list(dict.fromkeys(d["model"]))
    ukuran = baris[baris["metrik"].str.lower() == KOLOM_TRAIN_SIZE.lower()]
    ts = ukuran.drop_duplicates("skema").set_index("skema")["nilai"]
    skema_list = list(dict.fromkeys(list(ts.index) + list(d["skema"])))
    nilai = d.set_index(["skema", "metrik", "model"])["nilai"]

    terbaik = {}
    for m in metrik_ada:
        v = d.loc[d["metrik"] == m, "nilai"].dropna()
        if not v.empty:
            terbaik[m] = v.min() if _arah(m) == "rendah" else v.max()

    banyak_metrik = len(metrik_ada) > 1
    if banyak_metrik:   # header 2 baris: metrik, lalu model
        h1 = '<th rowspan="2">Skema</th>' + "".join(
            f'<th colspan="{len(model_list)}">{html.escape(m)}</th>' for m in metrik_ada)
        h1 += '<th rowspan="2">Train size</th>' if not ts.empty else ""
        h2 = "".join(f"<th>{html.escape(mo)}</th>" for _ in metrik_ada for mo in model_list)
        kepala_tabel = f'<tr class="pp-head">{h1}</tr><tr class="pp-head">{h2}</tr>'
    else:
        h1 = "<th>Skema</th>" + "".join(f"<th>{html.escape(mo)}</th>" for mo in model_list)
        h1 += "<th>Train size</th>" if not ts.empty else ""
        kepala_tabel = f'<tr class="pp-head">{h1}</tr>'

    isi = ""
    for s in skema_list:
        sel = ""
        for m in metrik_ada:
            for mo in model_list:
                v = nilai.get((s, m, mo))
                best = v is not None and pd.notna(v) and m in terbaik and v == terbaik[m]
                kelas = ' class="pp-best"' if best else ""
                sel += f"<td{kelas}>{_angka(v, m)}</td>"
        if not ts.empty:
            sel += f"<td class='pp-n'>{_angka(ts.get(s), '_bulat')}</td>"
        isi += f"<tr><th class='pp-skema'>{html.escape(s)}</th>{sel}</tr>"

    return kepala + f'<table class="pp-tabel">{kepala_tabel}{isi}</table>'


# ==========================================================
# PETA
# ==========================================================
def _titik_tengah(geometry: dict) -> tuple[float, float]:
    """Titik tengah (centroid) poligon terbesar, untuk posisi label nama wilayah."""
    polys = geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
    terbaik, luas_maks = None, -1.0
    for poly in polys:
        ring = poly[0]
        a = cx = cy = 0.0
        for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
            k = x1 * y2 - x2 * y1
            a += k; cx += (x1 + x2) * k; cy += (y1 + y2) * k
        if abs(a) > luas_maks:
            luas_maks = abs(a)
            terbaik = (cy / (3 * a), cx / (3 * a)) if a else (ring[0][1], ring[0][0])
    return terbaik


def _buat_peta(geojson: dict, hasil: pd.DataFrame, metrik_grup: list) -> folium.Map:
    per_kode = {k: g for k, g in hasil.groupby("kode")}
    kosong = hasil.iloc[0:0]
    gj = copy.deepcopy(geojson)
    for f in gj["features"]:
        p = f["properties"]
        baris = per_kode.get(p[KOLOM_KODE], kosong)
        p["_ada"] = not baris.empty
        p["_html"] = _html_popup(p, baris, metrik_grup)

    m = folium.Map(
        tiles=None,
        attributionControl=bool(PETA_DASAR),
        zoom_control=True,
        scrollWheelZoom=False,
        zoom_snap=0.25,
    )
    for i, (tiles, nama) in enumerate(PETA_DASAR):
        extra = {}
        if tiles == "OpenStreetMap":
            # Keterangan sumber versi singkat (wajib ada menurut lisensi OpenStreetMap)
            extra["attr"] = '<a href="https://www.openstreetmap.org/copyright">© OpenStreetMap</a>'
        folium.TileLayer(tiles, name=nama, overlay=False, control=True, show=(i == 0), **extra).add_to(m)

    css = (
        ".leaflet-control-attribution a[href*='leafletjs'],"
        ".leaflet-control-attribution a[href*='leafletjs'] + span{display:none!important;}"
        ".leaflet-control-attribution{font-size:10px!important;background:rgba(255,255,255,.6)!important;}"
        ".leaflet-control-attribution a{color:#374151!important;}"
        ".leaflet-popup-content{margin:12px 14px;font:13px/1.35 'Segoe UI',Arial,sans-serif;color:#1f2937;}"
        ".leaflet-popup-content table{margin:0;}"
        ".pp-judul{font-weight:700;font-size:15px;color:#0d1b2a;}"
        ".pp-info{color:#6b7280;font-size:12px;margin-top:2px;}"
        ".pp-kosong{margin-top:8px;color:#6b7280;font-style:italic;}"
        ".pp-metrik{margin:10px 0 6px;font-weight:700;}"
        ".pp-metrik span{font-weight:400;color:#6b7280;font-size:11px;}"
        ".pp-tabel{border-collapse:collapse;width:100%;}"
        ".pp-tabel th,.pp-tabel td{border-bottom:1px solid #e5e7eb;padding:3px 8px;"
        "text-align:right;white-space:nowrap;font-size:12px;}"
        ".pp-tabel tr:first-child th{background:#f3f4f6;font-weight:600;}"
        ".pp-tabel th.pp-skema,.pp-tabel tr:first-child th:first-child{text-align:left;font-weight:600;}"
        ".pp-tabel td.pp-n{color:#6b7280;}"
        ".pp-best{background:#fff3c4;font-weight:700;}"
        ".pp-tabel tr.pp-head th{background:#f3f4f6;font-weight:600;text-align:center;}"
        "path.leaflet-interactive:focus{outline:none;}"
        ".label-wilayah{font:600 12px/1.1 'Segoe UI',Arial,sans-serif;color:#1f2937;"
        "text-shadow:-1px -1px 0 #fff,1px -1px 0 #fff,-1px 1px 0 #fff,1px 1px 0 #fff;"
        "white-space:nowrap;transform:translate(-50%,-50%);pointer-events:none;}"
    )
    if not PETA_DASAR:
        css += f".leaflet-container{{background:{WARNA_LATAR_PETA};}}"
    m.get_root().header.add_child(folium.Element(f"<style>{css}</style>"))

    ada_prov = bool(gj["features"]) and "provinsi" in gj["features"][0]["properties"]

    def style(feature):
        return {
            "fillColor": WARNA_WILAYAH if feature["properties"]["_ada"] else WARNA_TANPA_DATA,
            "fillOpacity": TRANSPARANSI_WARNA,
            "color": WARNA_GARIS_BATAS,
            "weight": 1,
        }

    lapisan_wilayah = folium.GeoJson(
        gj,
        name="Wilayah",
        style_function=style,
        highlight_function=lambda f: {"weight": 2.5, "color": "#0d1b2a"},
        tooltip=folium.GeoJsonTooltip(
            fields=[KOLOM_WILAYAH, *(["provinsi"] if ada_prov else [])],
            aliases=["Wilayah", *(["Provinsi"] if ada_prov else [])],
            sticky=True,
        ),
        popup=folium.GeoJsonPopup(fields=["_html"], labels=False, max_width=900),
    ).add_to(m)

    if TAMPILKAN_NAMA_WILAYAH:
        lapisan_label = folium.FeatureGroup(name="Nama wilayah", show=True)
        for f in gj["features"]:
            lat, lon = _titik_tengah(f["geometry"])
            folium.Marker(
                [lat, lon],
                icon=folium.DivIcon(
                    html=f'<div class="label-wilayah">{html.escape(f["properties"][KOLOM_WILAYAH])}</div>',
                    icon_size=(0, 0),
                ),
                interactive=False,
            ).add_to(lapisan_label)
        lapisan_label.add_to(m)

    titik = load_titik(TITIK_FILE.stat().st_mtime) if TITIK_FILE.exists() else None
    if titik is not None and not titik.empty:
        lapisan_titik = folium.FeatureGroup(name=f"Titik lokasi ({len(titik)})", show=True)
        kolom_info = [c for c in titik.columns if c not in ("lat", "lon")]
        for _, r in titik.iterrows():
            popup = "<br>".join(f"<b>{c}</b>: {r[c]}" for c in kolom_info) or None
            folium.CircleMarker(
                [r["lat"], r["lon"]], radius=5, color="#7a1d0c", weight=1,
                fill=True, fill_color=WARNA_TITIK, fill_opacity=0.95,
                popup=folium.Popup(popup, max_width=250) if popup else None,
            ).add_to(lapisan_titik)
        lapisan_titik.add_to(m)

    plugins.Search(
        layer=lapisan_wilayah,
        search_label=KOLOM_WILAYAH,
        placeholder="Cari wilayah...",
        collapsed=True,
        position="topleft",
    ).add_to(m)
    folium.LayerControl(position="topright", collapsed=True).add_to(m)

    # Zoom otomatis ke seluruh wilayah yang ditampilkan
    lons, lats = [], []

    def _kumpulkan(c):
        if isinstance(c[0], (int, float)):
            lons.append(c[0]); lats.append(c[1])
        else:
            for x in c:
                _kumpulkan(x)

    for f in gj["features"]:
        _kumpulkan(f["geometry"]["coordinates"])
    m.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]])
    return m


# ==========================================================
# TAMPILAN DI HALAMAN
# ==========================================================
def render():

    geojson = load_geojson(GEOJSON_FILE.stat().st_mtime, tuple(FILTER_KODE_PROV))
    if not DATA_FILE.exists():
        st.error(f"File data `{DATA_FILE.name}` tidak ditemukan di folder `data`.")
        return
    try:
        hasil = load_hasil(DATA_FILE.stat().st_mtime)
    except ValueError as e:
        st.error(f"Peta belum bisa ditampilkan. {e}")
        return

    kode_peta = {f["properties"][KOLOM_KODE] for f in geojson["features"]}
    tidak_cocok = sorted(set(hasil["kode"]) - kode_peta)
    hasil = hasil[hasil["kode"].isin(kode_peta)]
    if hasil.empty:
        st.error(
            f"Tidak ada kode `{KOLOM_KODE_DATA}` di `{DATA_FILE.name}` yang cocok dengan peta.\n\n"
            f"- Contoh kode di peta: {', '.join(sorted(kode_peta)[:5])}\n"
            f"- Contoh kode di data: {', '.join(tidak_cocok[:5]) or '(kosong)'}"
        )
        return

    ada = set(hasil["metrik"])
    grup_ada = {g: [m for m in daftar if m in ada] for g, daftar in GRUP_METRIK.items()}
    grup_ada = {g: d for g, d in grup_ada.items() if d}
    if not grup_ada:
        st.error("Tidak ada metrik di GRUP_METRIK yang ditemukan di header Excel.")
        return
    metrik_list = list(grup_ada)

    pasangan = hasil[["train", "test"]].drop_duplicates().reset_index(drop=True)
    if len(pasangan) > 1:
        c1, c2 = st.columns(2)
        metrik = c1.selectbox("Pilih metrik yang akan ditampilkan", metrik_list, key="metrik_peta")
        label = [f"Train {r.train} → Test {r.test}" for r in pasangan.itertuples()]
        i = c2.selectbox("Tahun", range(len(label)), format_func=lambda k: label[k], key="tahun_peta")
        hasil = hasil[(hasil["train"] == pasangan.at[i, "train"]) & (hasil["test"] == pasangan.at[i, "test"])]
    else:
        metrik = st.selectbox("Pilih metrik yang akan ditampilkan", metrik_list, key="metrik_peta")

    metrik_grup = grup_ada[metrik]
    # Sudut peta siku (tidak membulat)
    st.markdown("<style>iframe[title='streamlit_folium.st_folium']{border-radius:0 !important;}</style>",
                unsafe_allow_html=True)
    peta = _buat_peta(geojson, hasil, metrik_grup)
    st_folium(
        peta,
        key="peta_wilayah",
        height=TINGGI_PETA,
        use_container_width=True,
        returned_objects=[],   # interaksi peta tidak memuat ulang halaman
    )


    if tidak_cocok:
        st.warning(
            f"{len(tidak_cocok)} kode di data tidak ditemukan di peta: "
            + ", ".join(tidak_cocok[:10]) + (" ..." if len(tidak_cocok) > 10 else "")
        )

    # ---------- Tabel semua wilayah ----------
    # (gaya tabel memakai CSS_TABEL_EXCEL yang dimuat di hasil.py)
    st.markdown(
        f'<div class="sub-title" style="font-size:20px;">Tabel {html.escape(metrik)} '
        f'Seluruh Kabupaten/Kota</div>',
        unsafe_allow_html=True,
    )
    st.markdown(_tabel_semua_wilayah(geojson, hasil, metrik_grup), unsafe_allow_html=True)


def _tabel_semua_wilayah(geojson: dict, hasil: pd.DataFrame, metrik_grup: list, tinggi: int = 480) -> str:
    """Tabel HTML: header 1 = algoritma, header 2 = skenario; baris = kabupaten/kota."""
    nama = {f["properties"][KOLOM_KODE]: f["properties"][KOLOM_WILAYAH] for f in geojson["features"]}
    d = hasil[hasil["metrik"].isin(metrik_grup)].drop_duplicates(["kode", "metrik", "model", "skema"])
    metrik = metrik_grup[0]
    model_list = list(dict.fromkeys(d["model"]))
    skema_per_model = {m: list(dict.fromkeys(d.loc[d["model"] == m, "skema"])) for m in model_list}
    nilai = d.set_index(["kode", "model", "skema"])["nilai"]

    h1 = '<th rowspan="2">Kode</th><th rowspan="2">Kabupaten/Kota</th>'
    h1 += "".join(f'<th colspan="{len(skema_per_model[m])}">{html.escape(m)}</th>' for m in model_list)
    h2 = "".join(f"<th>{html.escape(s)}</th>" for m in model_list for s in skema_per_model[m])

    baris = ""
    for kode in sorted(d["kode"].unique()):
        sel = f'<td>{html.escape(kode)}</td><td style="text-align:left">{html.escape(nama.get(kode, ""))}</td>'
        for m in model_list:
            for s in skema_per_model[m]:
                sel += f"<td>{_angka(nilai.get((kode, m, s)), metrik)}</td>"
        baris += f"<tr>{sel}</tr>"

    return (
        f'<div class="xl-scroll" style="max-height:{tinggi}px">'
        f'<table class="xl-tabel"><thead><tr>{h1}</tr><tr>{h2}</tr></thead>'
        f"<tbody>{baris}</tbody></table></div>"
    )