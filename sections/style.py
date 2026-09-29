import base64
from pathlib import Path

import streamlit as st

# Nama file gambar background (taruh di folder yang sama dengan app.py)
HERO_IMAGE = "gambar.jpg"


def _load_image_base64(path: str) -> str:
    file = Path(__file__).parent.parent / path
    if not file.exists():
        return ""
    ext = file.suffix.lower().replace(".", "")
    mime = "jpeg" if ext in ("jpg", "jpeg") else ext
    data = base64.b64encode(file.read_bytes()).decode()
    return f"data:image/{mime};base64,{data}"


def render():
    img_src = _load_image_base64(HERO_IMAGE)
    hero_bg = f"url('{img_src}')" if img_src else "linear-gradient(135deg, #0d1b2a, #1b263b)"

    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&family=Roboto+Slab:ital,wght@0,700;1,400&display=swap');

/* Sembunyikan elemen bawaan Streamlit */
#MainMenu, footer, header[data-testid="stHeader"] {{display: none !important;}}
[data-testid="stToolbar"], [data-testid="stDecoration"] {{display: none !important;}}

.block-container, [data-testid="stMainBlockContainer"] {{
    padding: 0 !important;
    max-width: 100% !important;
}}
/* Tanpa jarak antar blok utama (gambar menempel ke atas, section menempel satu sama lain) */
[data-testid="stMainBlockContainer"] [data-testid="stVerticalBlock"] {{gap: 0 !important;}}
html, [data-testid="stAppViewContainer"], [data-testid="stMain"], section.main {{
    scroll-behavior: smooth;
}}

/* ---------------- HEADER ---------------- */
#custom-header {{
    position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
    display: flex; justify-content: space-between; align-items: center;
    padding: 28px 60px;
    background-color: transparent;
    transition: background-color 0.4s ease, padding 0.4s ease, box-shadow 0.4s ease;
}}
#custom-header.scrolled {{
    background-color: #000000;
    padding: 16px 60px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.4);
}}
.header-logo {{
    font-family: 'Montserrat', sans-serif;
    color: #ffc300; font-size: 24px; font-weight: 700;
}}
.header-nav {{display: flex; gap: 55px;}}
.header-nav a {{
    font-family: 'Montserrat', sans-serif;
    color: #ffffff !important; text-decoration: none !important;
    font-size: 20px; font-weight: 800; letter-spacing: 1.5px;
    transition: color 0.2s;
}}
.header-nav a:hover {{color: #ffc300 !important;}}

/* ---------------- HERO ---------------- */
.hero {{
    height: 100vh; width: 100%;
    background-image: linear-gradient(rgba(0,0,0,0.55), rgba(0,0,0,0.55)), {hero_bg};
    background-size: cover; background-position: center;
    display: flex; flex-direction: column; justify-content: center; align-items: center;
    text-align: center; padding: 0 40px;
}}
.hero-subtitle {{
    font-family: 'Roboto Slab', serif; font-style: italic;
    color: #ffffff; font-size: 40px; margin-bottom: 20px;
    text-shadow: 0 2px 8px rgba(0,0,0,0.6);
}}
.hero-title {{
    font-family: 'Roboto Slab', serif; font-weight: 700;
    color: #ffffff; font-size: 48px; line-height: 1.25; max-width: 1100px;
    text-shadow: 0 2px 8px rgba(0,0,0,0.6);
}}

/* ---------------- SECTION ----------------
   Setiap section adalah st.container(key="sec-...") sehingga
   Streamlit memberi class "st-key-sec-..." yang bisa di-style. */
[class*="st-key-sec-"] {{
    padding: 80px 60px !important;
    gap: 1.2rem !important;
    font-family: 'Montserrat', sans-serif;
    color: #333;
}}
[data-testid="stVerticalBlock"][class*="st-key-sec-"],
[class*="st-key-sec-"] [data-testid="stVerticalBlock"] {{gap: 0.6rem !important;}}
[class*="st-key-sec-"] p {{font-size: 16px; line-height: 1.8;}}
.st-key-sec-pendahuluan p {{
    font-size: 20px;         /* ukuran huruf */
    text-align: justify;     /* rata kanan-kiri */
    line-height: 1.8;        /* spasi antarbaris */
    margin-bottom: 16px;     /* jarak antarparagraf */
    letter-spacing: 0px;     /* jarak antarhuruf */
    word-spacing: 0px;       /* jarak antarkata (tambahan) */
}}
.st-key-sec-data [data-testid="stMarkdown"] p {{
    font-size: 20px;         /* ukuran huruf */
    text-align: justify;      /* rata tengah */
    line-height: 1.8;        /* spasi antarbaris */
    margin-bottom: 16px;     /* jarak antarparagraf */
}}
.st-key-sec-data, .st-key-sec-hasil {{background-color: #f7f8fa;}}
.anchor {{scroll-margin-top: 150px;}}
.section-title {{
    font-family: 'Roboto Slab', serif; font-size: 32px; font-weight: 700;
    color: #0d1b2a; border-bottom: 4px solid #ffc300;
    display: inline-block; padding-bottom: 8px; margin-bottom: 8px;
}}
.sub-title {{
    font-family: 'Roboto Slab', serif; font-size: 20px; font-weight: 700;
    color: #0d1b2a; margin: 20px 0 14px 0;
}}
.note {{font-size: 13px; color: #6b7280; font-style: italic;}}

/* Kartu metrik di bagian hasil */
[class*="st-key-sec-"] [data-testid="stMetric"] {{
    background: #ffffff; border-radius: 10px; padding: 18px 20px;
    border-left: 5px solid #ffc300;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}}

/* ---------------- PETA ---------------- */
.st-key-map-info {{
    background: #ffffff; border-radius: 12px; padding: 22px !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}}
.st-key-map-info [data-testid="stMetric"] {{
    box-shadow: none !important; padding: 10px 12px !important; background: #f7f8fa !important;
}}
.map-info-title {{
    font-family: 'Roboto Slab', serif; font-size: 22px; font-weight: 700; color: #0d1b2a;
}}
.map-info-list div {{
    display: flex; justify-content: space-between;
    padding: 8px 0; border-bottom: 1px solid #eef0f3; font-size: 14px;
}}
.map-info-list span {{color: #6b7280;}}
.map-info-list b {{color: #0d1b2a;}}
iframe[title="streamlit_folium.st_folium"] {{border-radius: 12px;}}
.map-legend {{font-size: 13px; color: #374151; margin: 4px 0 24px 0;}}
.map-legend .lg-title {{font-weight: 600; margin-bottom: 6px;}}
.map-legend .lg-row {{display: flex; flex-wrap: wrap; gap: 6px 16px;}}
.map-legend .lg-item {{display: flex; align-items: center; gap: 6px;}}
.map-legend .lg-item span {{width: 18px; height: 12px; border-radius: 3px; display: inline-block;}}

/* ---------------- FOOTER ---------------- */
.footer-container {{
    background-color: #000000; color: #f1f1f1; text-align: center;
    padding: 28px 20px; font-family: 'Montserrat', sans-serif; font-size: 14px;
}}

/* Elemen CSS & header tidak memakan ruang (supaya gambar menempel ke atas) */
[data-testid="stElementContainer"]:has(style),
[data-testid="stElementContainer"]:has(#custom-header) {{
    height: 0 !important; min-height: 0 !important; margin: 0 !important; overflow: visible;
}}

/* Iframe script tidak memakan ruang */
[data-testid="stElementContainer"]:has(iframe[title="st.iframe"]) {{height: 0 !important; margin: 0 !important;}}

@media (max-width: 768px) {{
    #custom-header {{padding: 18px 20px; flex-direction: column; gap: 10px;}}
    .header-nav {{gap: 16px;}}
    .header-nav a {{font-size: 12px;}}
    .hero-subtitle {{font-size: 26px;}}
    .hero-title {{font-size: 28px;}}
    [class*="st-key-sec-"] {{padding: 50px 20px !important;}}
}}
</style>
""",
        unsafe_allow_html=True,
    )
