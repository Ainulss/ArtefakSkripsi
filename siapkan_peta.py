"""
Ubah file SHP kabupaten/kota menjadi data/wilayah.geojson untuk peta.

Cukup dijalankan SEKALI (atau setiap kali file SHP berganti):
    python siapkan_peta.py

Butuh paket: pip install geopandas
"""

from pathlib import Path

import geopandas as gpd

# ==========================================================
# PENGATURAN — sesuaikan dengan file SHP kamu
# ==========================================================
# Lokasi file .shp (file .shx, .dbf, .prj harus ada di folder yang sama)
FILE_SHP = "data/shp/Administrasi_Kabupaten.shp"

# Nama kolom di SHP yang berisi kode dan nama kab/kota.
# Kalau belum tahu, biarkan saja lalu jalankan skrip ini:
# daftar kolom SHP akan ditampilkan.
KOLOM_KODE_SHP = "kodekab"
KOLOM_NAMA_SHP = "nmkab"

# (Opsional) hanya ambil wilayah dengan awalan kode tertentu,
# misalnya "34" untuk DI Yogyakarta. Kosongkan ("") untuk semua wilayah.
FILTER_AWALAN_KODE = ""

# Penyederhanaan garis batas agar peta ringan (derajat).
# 0.001 ~ 100 m. Perbesar (0.005) jika peta masih berat, 0 untuk tanpa penyederhanaan.
TOLERANSI_SIMPLIFY = 0.001

FILE_OUTPUT = "data/wilayah.geojson"


def main():
    base = Path(__file__).parent
    gdf = gpd.read_file(base / FILE_SHP)
    print(f"Terbaca {len(gdf)} wilayah dari {FILE_SHP}")

    for kolom in (KOLOM_KODE_SHP, KOLOM_NAMA_SHP):
        if kolom not in gdf.columns:
            print(f"\n[!] Kolom '{kolom}' tidak ada di SHP.")
            print("Kolom yang tersedia:", [c for c in gdf.columns if c != "geometry"])
            print("\nContoh isi 3 baris pertama:")
            print(gdf.drop(columns="geometry").head(3).to_string())
            print("\nUbah KOLOM_KODE_SHP / KOLOM_NAMA_SHP di bagian atas skrip ini.")
            return

    # Samakan format kode (hilangkan spasi, titik, dan ".0")
    kode = (
        gdf[KOLOM_KODE_SHP].astype(str).str.strip()
        .str.replace(r"\.0$", "", regex=True)
        .str.replace(".", "", regex=False)
    )
    gdf = gpd.GeoDataFrame(
        {"kode": kode, "wilayah": gdf[KOLOM_NAMA_SHP].astype(str).str.strip()},
        geometry=gdf.geometry,
        crs=gdf.crs,
    )

    if FILTER_AWALAN_KODE:
        gdf = gdf[gdf["kode"].str.startswith(FILTER_AWALAN_KODE)]
        print(f"Setelah filter awalan '{FILTER_AWALAN_KODE}': {len(gdf)} wilayah")

    # Perbaiki poligon yang rusak (sering terjadi di SHP batas wilayah)
    gdf["geometry"] = gdf.geometry.make_valid()

    # Satu baris per kode (SHP kadang memecah satu kab/kota jadi beberapa baris)
    if gdf["kode"].duplicated().any():
        gdf = gdf.dissolve(by="kode", as_index=False, aggfunc="first")

    # Peta web butuh koordinat lintang/bujur (EPSG:4326)
    if gdf.crs is None:
        print("[!] SHP tidak punya info proyeksi (.prj). Dianggap EPSG:4326.")
        gdf = gdf.set_crs(4326)
    gdf = gdf.to_crs(4326)

    if TOLERANSI_SIMPLIFY > 0:
        gdf["geometry"] = gdf.geometry.simplify(TOLERANSI_SIMPLIFY, preserve_topology=True)

    out = base / FILE_OUTPUT
    out.parent.mkdir(parents=True, exist_ok=True)
    gdf[["kode", "wilayah", "geometry"]].to_file(out, driver="GeoJSON", COORDINATE_PRECISION=5)

    print(f"\nSelesai: {out} ({out.stat().st_size / 1024:.0f} KB, {len(gdf)} wilayah)")
    print("Contoh kode:", ", ".join(gdf["kode"].head(5)))
    print("Pastikan kolom 'kode' di data/indikator_wilayah.csv memakai format yang sama.")


if __name__ == "__main__":
    main()
