import streamlit as st

from sections.common import section


def render():
    with section("pendahuluan", "Pendahuluan"):
        st.markdown(
            """
Penetapan penerima bantuan sosial di Indonesia melalui metode Proxy Means Test (PMT) masih menghadapi tantangan ketepatan sasaran 
akibat keterbatasan jumlah sampel Susenas di tingkat kabupaten/kota. Penggabungan data antar tahun memunculkan permasalahan baru, 
yaitu distribution shift akibat dampak inflasi. Untuk mengatasi hal tersebut, penelitian ini mengembangkan model PMT berbasis penggabungan 
data antarwilayah dalam tahun yang sama dengan memanfaatkan teknik clustering dan pooling data antarwilayah, serta membandingkan performa algoritma 
XGBoost Regression dan Tabular Prior-data Fitted Network (TabPFN). Selain mengevaluasi performa model secara keseluruhan, penelitian ini juga menganalisis 
hasil klasifikasi pada rumah tangga dengan jumlah sampel sedikit, yaitu rumah tamgga dengan satu anggota, Kepala Rumah Tangga (KRT) perempuan, keberadaan lansia, 
dan rumah tangga dengan lebih dari satu keluarga. Oleh karena itu, penelitian ini bertujuan untuk meningkatkan kinerja model PMT agar mampu menghasilkan estimasi 
kesejahteraan yang lebih akurat dan representatif bagi seluruh lapisan masyarakat.
"""
        )
