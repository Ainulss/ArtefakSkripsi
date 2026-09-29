import streamlit as st


def section(section_id: str, title: str):
    """Buat container section dengan anchor (untuk navigasi header) dan judul.

    Pemakaian:
        with section("data", "Data"):
            st.write("...")
    """
    container = st.container(key=f"sec-{section_id}")
    container.markdown(
        f'<div id="{section_id}" class="anchor"></div>'
        f'<div class="section-title">{title}</div>',
        unsafe_allow_html=True,
    )
    return container
