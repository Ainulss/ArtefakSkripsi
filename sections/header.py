import streamlit as st

JUDUL = "Optimalisasi Proxy Means Test pada Kondisi Limited Sample Size"


def render():
    # Header: transparan di atas gambar, jadi hitam saat di-scroll
    st.markdown(
        """
<div id="custom-header" style="justify-content: center;">
<div class="header-nav">
<a href="#pendahuluan">PENDAHULUAN</a>
<a href="#data">DATA</a>
<a href="#metode">METODE</a>
<a href="#hasil">HASIL</a>
</div>
</div>
""",
        unsafe_allow_html=True,
    )

    # Hero / tampilan awal
    st.markdown(
        f"""
<div class="hero">
<div class="hero-title" style="margin-top: 60px">{JUDUL}</div>
</div>
""",
        unsafe_allow_html=True,
    )