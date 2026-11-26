import argparse
import asyncio
import glob
import json
import math
import os
import sys
import urllib.parse
import urllib.request

import edge_tts
import whisper
from moviepy import (
    AudioFileClip,
    CompositeAudioClip,
    CompositeVideoClip,
    ImageClip,
    TextClip,
    VideoFileClip,
    concatenate_audioclips,
    concatenate_videoclips,
)

from efek_style import PRESET_15_STYLE, gabung_split_screen, terapkan_efek_style

# === KONFIGURASI DEFAULT ===
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")
FONT_PATH = "C:/Windows/Fonts/arialbd.ttf"
TARGET_W = 1080
TARGET_H = 1920

VOICES = {
    "pria": "id-ID-ArdiNeural",
    "wanita": "id-ID-GadisNeural",
}

PRESET_SUASANA = {
    "horor": {"rate": "-10%", "pitch": "-8Hz"},
    "misteri": {"rate": "-6%", "pitch": "-5Hz"},
    "edukatif": {"rate": "+5%", "pitch": "+0Hz"},
    "storytelling": {"rate": "-3%", "pitch": "-2Hz"},
    "santai": {"rate": "+6%", "pitch": "+2Hz"},
    "sinematik": {"rate": "-5%", "pitch": "-4Hz"},
}


async def _buat_suara_async(teks, file_output, voice_id, rate, pitch):
    communicate = edge_tts.Communicate(teks, voice_id, rate=rate, pitch=pitch)
    await communicate.save(file_output)


def buat_suara(teks, file_output="suara_shorts.mp3", gender="pria", suasana="edukatif"):
    voice_id = VOICES.get(gender.lower(), VOICES["pria"])
    preset = PRESET_SUASANA.get(suasana.lower(), PRESET_SUASANA["edukatif"])
    print(f"[VO AI] Membuat audio ({voice_id}, rate={preset['rate']}, pitch={preset['pitch']})...")
    asyncio.run(_buat_suara_async(teks, file_output, voice_id, preset["rate"], preset["pitch"]))
    print(f"[VO AI] Selesai -> {file_output}")
    return file_output


def cari_dan_download_video(kata_kunci, jumlah=4):
    if not PEXELS_API_KEY:
        print("[ERROR] PEXELS_API_KEY belum diatur. Gunakan --folder-media untuk video/gambar lokal.")
        sys.exit(1)

    query = urllib.parse.quote(kata_kunci)
    url = f"https://api.pexels.com/videos/search?query={query}&orientation=portrait&per_page={jumlah}"
    req = urllib.request.Request(url, headers={"Authorization": PEXELS_API_KEY, "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    file_videos = []
    for idx, vid in enumerate(data.get("videos", [])):
        files = vid.get("video_files", [])
        if not files:
            continue
        files_sorted = sorted(files, key=lambda x: x.get("height", 0), reverse=True)
        link = files_sorted[0]["link"]
        out_name = f"clip_{idx}.mp4"
        print(f"[PEXELS] Mengunduh {out_name}...")
        urllib.request.urlretrieve(link, out_name)
        file_videos.append(out_name)
    return file_videos


def muat_media_lokal(folder_media):
    ekstensi = ("*.mp4", "*.mov", "*.mkv", "*.jpg", "*.jpeg", "*.png", "*.webp")
    daftar = []
    for ext in ekstensi:
        daftar.extend(sorted(glob.glob(os.path.join(folder_media, ext))))
    return daftar


def buat_subtitle_whisper(file_audio, kata_per_baris=3):
    print("[WHISPER] Mentranskripsi audio untuk subtitle...")
    model = whisper.load_model("base")
    result = model.transcribe(file_audio, language="id", word_timestamps=True)

    list_sub = []
    for seg in result.get("segments", []):
        words = seg.get("words", [])
        if not words:
            list_sub.append({"text": seg["text"].strip(), "start": seg["start"], "end": seg["end"]})
            continue
        for i in range(0, len(words), kata_per_baris):
            chunk = words[i : i + kata_per_baris]
            teks = " ".join(w["word"].strip() for w in chunk).strip()
            if teks:
                list_sub.append({
                    "text": teks,
                    "start": chunk[0]["start"],
                    "end": chunk[-1]["end"],
                })
    return list_sub


def siapkan_klip_vertikal(path_media, durasi_gambar=4.0):
    ext = os.path.splitext(path_media)[1].lower()
    if ext in (".jpg", ".jpeg", ".png", ".webp"):
        clip = ImageClip(path_media).with_duration(durasi_gambar)
    else:
        clip = VideoFileClip(path_media).without_audio()

    rasio_target = TARGET_W / TARGET_H
    rasio_asal = clip.w / clip.h
    if rasio_asal > rasio_target:
        clip = clip.resized(height=TARGET_H)
    else:
        clip = clip.resized(width=TARGET_W)

    clip = clip.cropped(
        x_center=clip.w / 2,
        y_center=clip.h / 2,
        width=TARGET_W,
        height=TARGET_H,
    )
    return clip


def render_video(
    file_audio,
    list_media,
    list_sub,
    file_output="hasil_shorts.mp4",
    gaya_sub="karaoke",
    style_id="5",
    split_bawah="",
    bgm_path="",
):
    preset_info = PRESET_15_STYLE.get(str(style_id), PRESET_15_STYLE["5"])
    print(f"[RENDER] Style #{style_id}: {preset_info['nama']} | Subtitle: {gaya_sub} -> {file_output}")

    audio_vo = AudioFileClip(file_audio)
    durasi_audio = audio_vo.duration

    if bgm_path and os.path.exists(bgm_path):
        print(f"[BGM] Mencampur musik latar: {bgm_path}")
        bgm_raw = AudioFileClip(bgm_path)
        ulang = max(1, math.ceil(durasi_audio / max(bgm_raw.duration, 0.5)))
        bgm_loop = concatenate_audioclips([bgm_raw] * ulang).subclipped(0, durasi_audio)
        bgm_pelan = bgm_loop.with_volume_scaled(0.12) if hasattr(bgm_loop, "with_volume_scaled") else bgm_loop.volumex(0.12)
        audio_final = CompositeAudioClip([audio_vo, bgm_pelan])
    else:
        audio_final = audio_vo

    klip_dasar = [siapkan_klip_vertikal(m) for m in list_media]
    if not klip_dasar:
        print("[ERROR] Tidak ada file media untuk dirender.")
        sys.exit(1)

    klip_terkumpul = []
    total_durasi = 0.0
    idx = 0
    while total_durasi < durasi_audio:
        c = klip_dasar[idx % len(klip_dasar)]
        klip_terkumpul.append(c)
        total_durasi += c.duration
        idx += 1

    video_final = concatenate_videoclips(klip_terkumpul, method="compose").subclipped(0, durasi_audio)

    tmp_files = []
    mode_split = (str(style_id) == "9" or bool(split_bawah)) and split_bawah and os.path.exists(split_bawah)
    if mode_split:
        print(f"[SPLIT-SCREEN] Menggabungkan video bawah: {split_bawah}")
        tmp_atas = "_tmp_atas.mp4"
        tmp_split = "_tmp_split.mp4"
        tmp_files.extend([tmp_atas, tmp_split])
        video_final.write_videofile(tmp_atas, fps=30, codec="libx264", audio=False)
        gabung_split_screen(tmp_atas, split_bawah, tmp_split)
        video_final = VideoFileClip(tmp_split).subclipped(0, durasi_audio)

    video_final = video_final.with_audio(audio_final)

    layers = [video_final]
    if gaya_sub != "tanpa" and list_sub:
        pos_y_karaoke = int(TARGET_H * 0.46) if mode_split else int(TARGET_H * 0.72)
        pos_y_minimalis = int(TARGET_H * 0.48) if mode_split else int(TARGET_H * 0.78)
        for item in list_sub:
            dur = max(0.1, item["end"] - item["start"])
            if gaya_sub == "minimalis":
                txt_clip = (
                    TextClip(
                        text=item["text"],
                        font=FONT_PATH,
                        font_size=54,
                        color="white",
                        stroke_color="black",
                        stroke_width=2,
                        method="caption",
                        size=(TARGET_W - 160, None),
                    )
                    .with_start(item["start"])
                    .with_duration(dur)
                    .with_position(("center", pos_y_minimalis))
                )
            else:  # karaoke
                txt_clip = (
                    TextClip(
                        text=item["text"].upper(),
                        font=FONT_PATH,
                        font_size=75,
                        color="yellow",
                        stroke_color="black",
                        stroke_width=4,
                        method="caption",
                        size=(TARGET_W - 120, None),
                    )
                    .with_start(item["start"])
                    .with_duration(dur)
                    .with_position(("center", pos_y_karaoke))
                )
            layers.append(txt_clip)

    tmp_mentah = "_tmp_render_mentah.mp4"
    tmp_files.append(tmp_mentah)

    final = CompositeVideoClip(layers)
    final.write_videofile(tmp_mentah, fps=30, codec="libx264", audio_codec="aac")
    final.close()

    print(f"[POST-FX] Menerapkan efek visual & normalisasi audio Style #{style_id}...")
    terapkan_efek_style(tmp_mentah, file_output, style_id=style_id)

    for f_tmp in tmp_files:
        if os.path.exists(f_tmp):
            try:
                os.remove(f_tmp)
            except OSError:
                pass

    print(f"[SELESAI] Video berhasil dirender: {os.path.abspath(file_output)}")


def parse_args():
    parser = argparse.ArgumentParser(description="Tools Produksi & Render YouTube Shorts Lokal")
    parser.add_argument("--vo-only", action="store_true", help="Hanya membuat Voiceover AI (Tahap 5)")
    parser.add_argument("--render-only", action="store_true", help="Hanya merender video dari audio yang sudah ada (Tahap 7)")
    parser.add_argument("--naskah", type=str, default="", help="Teks naskah langsung")
    parser.add_argument("--naskah-file", type=str, default="", help="Path file teks berisi naskah")
    parser.add_argument("--suasana", type=str, default="edukatif", choices=list(PRESET_SUASANA.keys()))
    parser.add_argument("--suara", type=str, default="pria", choices=list(VOICES.keys()))
    parser.add_argument("--audio", type=str, default="suara_shorts.mp3", help="File audio input/output")
    parser.add_argument("--kata-kunci", type=str, default="", help="Kata kunci pencarian video Pexels")
    parser.add_argument("--folder-media", type=str, default="", help="Folder berisi video/gambar lokal")
    parser.add_argument("--jumlah-klip", type=int, default=4, help="Jumlah klip Pexels yang diunduh")
    parser.add_argument("--style", type=str, default="5", choices=[str(i) for i in range(1, 16)], help="Nomor style video 1-15")
    parser.add_argument("--split-bawah", type=str, default="", help="Video gameplay/satisfying bawah untuk Style 9")
    parser.add_argument("--bgm", type=str, default="", help="File audio BGM latar belakang (opsional)")
    parser.add_argument("--gaya-sub", type=str, default="karaoke", choices=["karaoke", "minimalis", "tanpa"])
    parser.add_argument("--output", type=str, default="hasil_shorts.mp4", help="Nama file MP4 hasil render")
    return parser.parse_args()


if __name__ == "__main__":
    # Kompatibilitas lama: python main.py "<naskah>" "<kata_kunci>" [output.mp4]
    if len(sys.argv) >= 3 and not sys.argv[1].startswith("--"):
        naskah_arg = sys.argv[1]
        kunci_arg = sys.argv[2]
        out_arg = sys.argv[3] if len(sys.argv) >= 4 else "hasil_shorts.mp4"
        audio_path = buat_suara(naskah_arg)
        media = cari_dan_download_video(kunci_arg)
        subs = buat_subtitle_whisper(audio_path)
        render_video(audio_path, media, subs, file_output=out_arg, style_id="8")
        sys.exit(0)

    args = parse_args()

    teks_naskah = args.naskah
    if args.naskah_file and os.path.exists(args.naskah_file):
        with open(args.naskah_file, "r", encoding="utf-8") as f:
            teks_naskah = f.read().strip()

    if not args.render_only:
        if not teks_naskah:
            print("[ERROR] Masukkan --naskah atau --naskah-file untuk membuat Voiceover AI.")
            sys.exit(1)
        buat_suara(teks_naskah, file_output=args.audio, gender=args.suara, suasana=args.suasana)
        if args.vo_only:
            sys.exit(0)

    if not os.path.exists(args.audio):
        print(f"[ERROR] File audio '{args.audio}' tidak ditemukan.")
        sys.exit(1)

    if args.folder_media:
        media_list = muat_media_lokal(args.folder_media)
    elif args.kata_kunci:
        media_list = cari_dan_download_video(args.kata_kunci, jumlah=args.jumlah_klip)
    else:
        print("[ERROR] Tentukan --kata-kunci (Pexels) atau --folder-media (aset lokal).")
        sys.exit(1)

    kata_per_baris = 3 if args.gaya_sub == "karaoke" else 6
    subs = [] if args.gaya_sub == "tanpa" else buat_subtitle_whisper(args.audio, kata_per_baris=kata_per_baris)
    render_video(
        args.audio,
        media_list,
        subs,
        file_output=args.output,
        gaya_sub=args.gaya_sub,
        style_id=args.style,
        split_bawah=args.split_bawah,
        bgm_path=args.bgm,
    )
