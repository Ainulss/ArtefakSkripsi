import streamlit as st

from sections import data, footer, hasil, header, metode, pendahuluan, style

st.set_page_config(
    page_title="Optimalisasi Proxy Means Test",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Urutan tampilan dari atas ke bawah
style.render()
header.render()
pendahuluan.render()
data.render()
metode.render()
hasil.render()
footer.render()
