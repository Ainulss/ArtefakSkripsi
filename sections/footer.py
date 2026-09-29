import streamlit as st
import streamlit.components.v1 as components


def render():
    st.markdown(
        """
<div class="footer-container">
Skripsi Ainul Fatimah 222212468
</div>
""",
        unsafe_allow_html=True,
    )

    # Script:
    # 1) header berubah hitam saat halaman di-scroll
    # 2) menu header yang bagiannya sedang dilihat/dipilih berwarna kuning
    components.html(
        """
<script>
const doc = window.parent.document;

// Warna menu aktif (kuning)
if (!doc.getElementById("gaya-menu-aktif")) {
    const gaya = doc.createElement("style");
    gaya.id = "gaya-menu-aktif";
    gaya.textContent = `
        .header-nav a.active { color: #ffc300 !important; }
        .header-nav a { position: relative; }
        .header-nav a.active::after {
            content: ""; position: absolute; left: 0; right: 0; bottom: -6px;
            height: 2px; background: #ffc300; border-radius: 2px;
        }`;
    doc.head.appendChild(gaya);
}

function attachScroll() {
    const header = doc.getElementById("custom-header");
    if (!header) { setTimeout(attachScroll, 200); return; }
    const links = Array.from(header.querySelectorAll('.header-nav a[href^="#"]'));
    const targets = [
        window.parent,
        doc.querySelector('[data-testid="stAppViewContainer"]'),
        doc.querySelector('[data-testid="stMain"]'),
        doc.querySelector('section.main'),
    ].filter(Boolean);

    // Setelah menu diklik, pilihan dikunci sebentar supaya tidak tertimpa
    // selama halaman bergerak (smooth scroll) ke bagian tujuan
    let kunciSampai = 0;

    function tandai(id) {
        links.forEach(a => a.classList.toggle("active", a.getAttribute("href") === "#" + id));
    }

    function update() {
        let y = window.parent.scrollY || 0;
        targets.forEach(t => { if (t.scrollTop) y = Math.max(y, t.scrollTop); });
        header.classList.toggle("scrolled", y > 50);

        if (Date.now() < kunciSampai) return;

        // Bagian aktif = bagian terakhir yang judulnya sudah melewati 40% tinggi layar
        const batas = window.parent.innerHeight * 0.4;
        let aktif = null;
        links.forEach(a => {
            const id = a.getAttribute("href").slice(1);
            const el = doc.getElementById(id);
            if (el && el.getBoundingClientRect().top <= batas) aktif = id;
        });
        // Sudah mentok di bawah halaman -> bagian terakhir yang aktif
        const sc = targets.find(t => t.scrollHeight && t.scrollHeight > t.clientHeight);
        if (sc && sc.scrollTop + sc.clientHeight >= sc.scrollHeight - 5 && links.length) {
            aktif = links[links.length - 1].getAttribute("href").slice(1);
        }
        tandai(aktif);
    }

    links.forEach(a => a.addEventListener("click", () => {
        tandai(a.getAttribute("href").slice(1));
        kunciSampai = Date.now() + 1500;   // kunci 1,5 detik
    }));
    targets.forEach(t => t.addEventListener("scroll", update, { passive: true }));
    update();
}
attachScroll();
</script>
""",
        height=0,
    )