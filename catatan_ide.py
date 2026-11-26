import json
import os
import sys
from datetime import datetime

RIWAYAT_FILE = "riwayat_ide.json"

def load_riwayat():
    if not os.path.exists(RIWAYAT_FILE):
        return {"riwayat_tema": [], "sudut_pandang_terpakai": []}
    with open(RIWAYAT_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if isinstance(data, list):
                return {"riwayat_tema": data, "sudut_pandang_terpakai": []}
            data.setdefault("riwayat_tema", [])
            data.setdefault("sudut_pandang_terpakai", [])
            return data
        except json.JSONDecodeError:
            return {"riwayat_tema": [], "sudut_pandang_terpakai": []}

def save_riwayat(data):
    with open(RIWAYAT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def normalisasi(teks: str) -> str:
    return " ".join(teks.lower().strip().split())

def daftar_terlarang():
    data = load_riwayat()
    tema_list = data["riwayat_tema"]
    if not tema_list:
        print("RIWAYAT KOSONG: Belum ada tema yang pernah ditampilkan.")
        return
    print(f"=== DAFTAR {len(tema_list)} TEMA YANG DILARANG DIULANG ===")
    for i, item in enumerate(tema_list, 1):
        judul = item["tema"] if isinstance(item, dict) else str(item)
        status = item.get("status", "ditampilkan") if isinstance(item, dict) else "lama"
        print(f"{i}. [{status}] {judul}")

def simpan_tampil(topik: str, daftar_tema: list):
    data = load_riwayat()
    existing = {
        normalisasi(item["tema"] if isinstance(item, dict) else str(item))
        for item in data["riwayat_tema"]
    }
    ditambahkan = 0
    for tema in daftar_tema:
        norm = normalisasi(tema)
        if norm and norm not in existing:
            data["riwayat_tema"].append({
                "topik": topik,
                "tema": tema.strip(),
                "status": "ditampilkan",
                "tanggal": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            existing.add(norm)
            ditambahkan += 1
    save_riwayat(data)
    print(f"Berhasil mencatat {ditambahkan} tema baru ke {RIWAYAT_FILE} (terkunci agar tidak muncul dua kali).")

def tandai_status(tema_target: str, status_baru: str):
    data = load_riwayat()
    target_norm = normalisasi(tema_target)
    ketemu = False
    for item in data["riwayat_tema"]:
        if isinstance(item, dict) and normalisasi(item["tema"]) == target_norm:
            item["status"] = status_baru
            item["diperbarui"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            ketemu = True
            break
    if not ketemu:
        data["riwayat_tema"].append({
            "topik": "manual",
            "tema": tema_target.strip(),
            "status": status_baru,
            "tanggal": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
    save_riwayat(data)
    print(f"Status tema '{tema_target}' diperbarui menjadi: {status_baru}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Penggunaan:")
        print("  python catatan_ide.py list")
        print("  python catatan_ide.py simpan-tampil <topik> <tema1> <tema2> ...")
        print("  python catatan_ide.py status <tema> <dipilih|selesai>")
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == "list":
        daftar_terlarang()
    elif cmd == "simpan-tampil" and len(sys.argv) >= 4:
        simpan_tampil(sys.argv[2], sys.argv[3:])
    elif cmd == "status" and len(sys.argv) >= 4:
        tandai_status(sys.argv[2], sys.argv[3])
    else:
        print("Argumen tidak valid.")
