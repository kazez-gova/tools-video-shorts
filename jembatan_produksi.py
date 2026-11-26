import argparse
import datetime
import json
import os
import re
import shutil
import sqlite3
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(ROOT_DIR)
DIR_3D = os.path.join(PARENT_DIR, "visual-storytelling-3d")
DIR_UPLOADER = os.path.join(PARENT_DIR, "yt-ai-uploader")
PAKET_FILE = os.path.join(ROOT_DIR, "paket_produksi.json")


def muat_paket():
    if not os.path.exists(PAKET_FILE):
        return {
            "topik": "",
            "tema": "",
            "total_part": 1,
            "durasi_detik": 60,
            "suasana": "horor",
            "style_id": "5",
            "style_nama": "Dark Cinematic Horor",
            "gaya_sub": "karaoke",
            "parts": [],
        }
    with open(PAKET_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def simpan_paket(data):
    with open(PAKET_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def buat_captions_estimasi(teks_naskah, durasi_total=60.0):
    bersih = re.sub(r"\[.*?\]", " ", teks_naskah)
    kata_list = [k.strip() for k in bersih.split() if k.strip()]
    if not kata_list:
        return []
    segmen = []
    kelompok = [kata_list[i : i + 3] for i in range(0, len(kata_list), 3)]
    step = durasi_total / max(len(kelompok), 1)
    for idx, grp in enumerate(kelompok):
        mulai = round(idx * step, 2)
        selesai = round(min((idx + 1) * step, max(durasi_total - 0.35, 0.5)), 2)
        segmen.append({"start": mulai, "end": selesai, "text": " ".join(grp).upper()})
    return segmen


def map_profil_3d(suasana):
    s = (suasana or "").lower()
    if any(k in s for k in ["horor", "misteri", "gelap", "investigatif"]):
        return {
            "lighting_profile": 1,
            "lighting_name": "Low-Key Atmospheric",
            "camera_preset": "handheld_tense" if "horor" in s else "dolly_push",
        }
    if any(k in s for k in ["edukatif", "fakta", "sains", "medis", "santai"]):
        return {
            "lighting_profile": 0,
            "lighting_name": "Daylight & Studio Cutaway",
            "camera_preset": "cutaway_orbit",
        }
    return {
        "lighting_profile": 1,
        "lighting_name": "Low-Key Atmospheric",
        "camera_preset": "reveal_pull",
    }


def cmd_ekspor_3d(part_num):
    if not os.path.isdir(DIR_3D):
        print(f"[ERROR] Folder visual-storytelling-3d tidak ditemukan di: {DIR_3D}")
        sys.exit(1)

    paket = muat_paket()
    handoff_dir = os.path.join(DIR_3D, "handoff_shorts")
    os.makedirs(handoff_dir, exist_ok=True)

    profil = map_profil_3d(paket.get("suasana", ""))
    part_data = next((p for p in paket.get("parts", []) if p.get("part") == part_num), {})

    naskah_file = os.path.join(ROOT_DIR, f"naskah_part{part_num}.txt")
    teks_naskah = part_data.get("naskah", "")
    if not teks_naskah and os.path.exists(naskah_file):
        with open(naskah_file, "r", encoding="utf-8") as f:
            teks_naskah = f.read().strip()

    audio_src = part_data.get("audio") or os.path.join(ROOT_DIR, f"suara_part{part_num}.mp3")
    audio_dst = ""
    if os.path.exists(audio_src):
        audio_dst = os.path.join(handoff_dir, f"voice_part{part_num}.mp3")
        shutil.copy2(audio_src, audio_dst)

    captions = buat_captions_estimasi(teks_naskah, float(paket.get("durasi_detik", 60)))
    captions_path = os.path.join(handoff_dir, f"captions_part{part_num}.json")
    with open(captions_path, "w", encoding="utf-8") as f:
        json.dump(captions, f, ensure_ascii=False, indent=2)

    payload_3d = {
        "source": "tools-video-shorts",
        "series_id": re.sub(r"[^a-z0-9]+", "-", paket.get("tema", "shorts").lower()).strip("-") or "shorts-3d",
        "topik": paket.get("topik", ""),
        "tema": paket.get("tema", ""),
        "part": part_num,
        "total_part": paket.get("total_part", 1),
        "durasi_target_detik": paket.get("durasi_detik", 60),
        "suasana": paket.get("suasana", ""),
        "lighting_profile": profil["lighting_profile"],
        "lighting_name": profil["lighting_name"],
        "camera_preset": profil["camera_preset"],
        "naskah": teks_naskah,
        "audio_file": audio_dst,
        "captions_file": captions_path,
        "judul_seo": part_data.get("judul_seo", ""),
        "deskripsi_seo": part_data.get("deskripsi_seo", ""),
    }

    handoff_json = os.path.join(handoff_dir, f"handoff_part{part_num}.json")
    with open(handoff_json, "w", encoding="utf-8") as f:
        json.dump(payload_3d, f, ensure_ascii=False, indent=2)

    print("=== HANDOFF KE VISUAL-STORYTELLING-3D BERHASIL ===")
    print(f"File paket 3D : {handoff_json}")
    print(f"Captions JSON : {captions_path}")
    if audio_dst:
        print(f"Audio VO      : {audio_dst}")
    print(f"Preset Kamera : {profil['camera_preset']} | Lighting: {profil['lighting_name']}")
    print("\nLangkah lanjut di Claude / Terminal visual-storytelling-3d:")
    print(f'  cd ../visual-storytelling-3d && /visual-storytelling-3d lanjut dari handoff_shorts/handoff_part{part_num}.json')


def cmd_ekspor_uploader(part_num, video_custom=""):
    if not os.path.isdir(DIR_UPLOADER):
        print(f"[ERROR] Folder yt-ai-uploader tidak ditemukan di: {DIR_UPLOADER}")
        sys.exit(1)

    paket = muat_paket()
    part_data = next((p for p in paket.get("parts", []) if p.get("part") == part_num), {})

    kandidat_video = [
        video_custom,
        part_data.get("video", ""),
        os.path.join(ROOT_DIR, f"hasil_part{part_num}.mp4"),
        os.path.join(DIR_3D, "out", f"part{part_num}.mp4"),
        os.path.join(DIR_3D, "out", "final.mp4"),
    ]
    video_src = next((v for v in kandidat_video if v and os.path.exists(v)), "")

    videos_dir = os.path.join(DIR_UPLOADER, "videos")
    os.makedirs(videos_dir, exist_ok=True)

    slug = re.sub(r"[^a-z0-9]+", "_", paket.get("tema", "shorts").lower()).strip("_")[:40] or "shorts"
    video_dst = ""
    if video_src:
        video_dst = os.path.join(videos_dir, f"{slug}_part{part_num}.mp4")
        shutil.copy2(video_src, video_dst)

    judul = part_data.get("judul_seo") or f"{paket.get('tema', 'Video Shorts')} [Part {part_num}/{paket.get('total_part', 1)}]"
    deskripsi = part_data.get("deskripsi_seo") or part_data.get("naskah", "")[:300]
    tags = part_data.get("tags") or ["shorts", "youtubeshorts", paket.get("topik", "fakta")]

    manifest_path = os.path.join(videos_dir, f"{slug}_part{part_num}_metadata.json")
    manifest = {
        "video_path": video_dst,
        "is_shorts": True,
        "title": judul,
        "description": deskripsi,
        "tags": tags,
        "thumbnail_text": part_data.get("thumbnail_text", "WAJIB TONTON!"),
        "part": part_num,
        "total_part": paket.get("total_part", 1),
    }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    db_path = os.path.join(DIR_UPLOADER, "content_tracker.db")
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [r[0] for r in cur.fetchall()]
            if "contents" in tables:
                cur.execute(
                    "INSERT INTO contents (title, platform, status, notes, created_at) VALUES (?, ?, ?, ?, ?)",
                    (judul, "Shorts", "Siap Upload", f"File: {video_dst or 'Menunggu render'}", datetime.datetime.now().isoformat()),
                )
                conn.commit()
            conn.close()
        except Exception as e:
            print(f"[INFO] Catatan DB tracker dilewati: {e}")

    print("=== HANDOFF KE YT-AI-UPLOADER BERHASIL ===")
    print(f"Metadata JSON : {manifest_path}")
    if video_dst:
        print(f"File Video    : {video_dst}")
    else:
        print("[INFO] File .mp4 belum ditemukan; metadata sudah disiapkan di folder videos/.")
    print("\nJalankan dashboard uploader dengan:")
    print("  cd ../yt-ai-uploader && streamlit run app.py")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Jembatan Produksi tools-video-shorts")
    sub = parser.add_subparsers(dest="aksi", required=True)

    p3d = sub.add_parser("ke-3d", help="Ekspor paket part ke visual-storytelling-3d")
    p3d.add_argument("--part", type=int, default=1, help="Nomor part (default: 1)")

    pup = sub.add_parser("ke-uploader", help="Ekspor video & SEO ke yt-ai-uploader")
    pup.add_argument("--part", type=int, default=1, help="Nomor part (default: 1)")
    pup.add_argument("--video", type=str, default="", help="Path file mp4 opsional")

    args = parser.parse_args()
    if args.aksi == "ke-3d":
        cmd_ekspor_3d(args.part)
    elif args.aksi == "ke-uploader":
        cmd_ekspor_uploader(args.part, args.video)
