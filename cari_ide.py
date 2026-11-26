import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
import os
import sys
import random

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RIWAYAT_FILE = "riwayat_ide.json"

SUDUT_PANDANG = [
    "{topik}",
    "fakta unik {topik}",
    "misteri {topik}",
    "sejarah {topik}",
    "fenomena {topik}",
    "sisi gelap {topik}",
    "rahasia {topik}",
    "{topik} terbaru",
    "kasus {topik}",
    "penemuan {topik}",
]

def normalisasi(teks: str) -> str:
    return " ".join(teks.lower().strip().split())

def load_judul_lama():
    if not os.path.exists(RIWAYAT_FILE):
        return set()
    try:
        with open(RIWAYAT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return set()

    lama = set()
    items = data.get("riwayat_tema", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
    for item in items:
        if isinstance(item, dict):
            teks = item.get("tema") or item.get("judul") or ""
        else:
            teks = str(item)
        if teks:
            lama.add(normalisasi(teks))
    return lama

def fetch_rss(query_str):
    query = urllib.parse.quote(query_str)
    url = f"https://news.google.com/rss/search?q={query}&hl=id&gl=ID&ceid=ID:id"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            xml_data = resp.read()
        root = ET.fromstring(xml_data)
        hasil = []
        for item in root.findall(".//item"):
            title_el = item.find("title")
            pub_el = item.find("pubDate")
            if title_el is not None and title_el.text:
                judul_bersih = title_el.text.rsplit(" - ", 1)[0].strip()
                hasil.append({
                    "judul": judul_bersih,
                    "tanggal": pub_el.text if pub_el is not None else "",
                })
        return hasil
    except Exception:
        return []

def cari_google_news(topik, jumlah=15):
    judul_lama = load_judul_lama()
    sudah_ambil = set(judul_lama)
    hasil_unik = []

    pola_list = [SUDUT_PANDANG[0]] + random.sample(SUDUT_PANDANG[1:], len(SUDUT_PANDANG) - 1)
    for pola in pola_list:
        if len(hasil_unik) >= jumlah:
            break
        kueri = pola.format(topik=topik)
        for item in fetch_rss(kueri):
            norm = normalisasi(item["judul"])
            if norm and norm not in sudah_ambil:
                sudah_ambil.add(norm)
                hasil_unik.append(item)
                if len(hasil_unik) >= jumlah:
                    break
    return hasil_unik

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Penggunaan: python cari_ide.py \"<topik>\" [jumlah]")
        sys.exit(1)

    topik = sys.argv[1]
    jumlah = int(sys.argv[2]) if len(sys.argv) >= 3 else 15
    hasil = cari_google_news(topik, jumlah=jumlah)

    if not hasil:
        print("Tidak ada hasil RSS baru ditemukan. Claude silakan kembangkan 10 tema unik baru dari basis pengetahuan (pastikan tidak bentrok dengan riwayat_ide.json).")
        sys.exit(0)

    print(f"=== {len(hasil)} BAHAN REFERENSI SEGAR UNTUK TOPIK: {topik} ===")
    for i, item in enumerate(hasil, 1):
        print(f"{i}. {item['judul']}")
