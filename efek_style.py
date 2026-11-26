import shutil
import subprocess

PRESET_15_STYLE = {
    "1": {"nama": "3D Storytelling", "jalur": "3d", "filter": ""},
    "2": {
        "nama": "Anime / 2D Ilustrasi",
        "jalur": "media_ai",
        "filter": "scale=w='1080*(1+0.07*abs(sin(t*0.35)))':h='1920*(1+0.07*abs(sin(t*0.35)))':eval=frame,crop=1080:1920,eq=saturation=1.18:contrast=1.05",
    },
    "3": {
        "nama": "Komik / Manga / Stickman",
        "jalur": "media_ai",
        "filter": "scale=w='1080*(1+0.08*abs(sin(t*0.4)))':h='1920*(1+0.08*abs(sin(t*0.4)))':eval=frame,crop=1080:1920,eq=contrast=1.15",
    },
    "4": {
        "nama": "Claymation / Miniatur 3D",
        "jalur": "media_ai",
        "filter": "scale=w='1080*(1+0.06*abs(sin(t*0.3)))':h='1920*(1+0.06*abs(sin(t*0.3)))':eval=frame,crop=1080:1920,eq=saturation=1.12",
    },
    "5": {
        "nama": "Dark Cinematic Horor",
        "jalur": "media_ai",
        "filter": "scale=w='1080*(1+0.09*abs(sin(t*0.3)))':h='1920*(1+0.09*abs(sin(t*0.3)))':eval=frame,crop=1080:1920,vignette=PI/4,noise=alls=12:allf=t+u,eq=brightness=-0.06:contrast=1.18:saturation=0.75",
    },
    "6": {
        "nama": "Dokumenter Arsip / Vintage",
        "jalur": "media_ai",
        "filter": "scale=w='1080*(1+0.06*abs(sin(t*0.3)))':h='1920*(1+0.06*abs(sin(t*0.3)))':eval=frame,crop=1080:1920,colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131,noise=alls=18:allf=t",
    },
    "7": {
        "nama": "Found Footage (VHS / CCTV)",
        "jalur": "media_ai",
        "filter": "vignette=PI/3.5,noise=alls=24:allf=t+u,eq=saturation=0.45:contrast=1.25",
    },
    "8": {
        "nama": "Stock Footage / B-Roll Cepat",
        "jalur": "pexels",
        "filter": "eq=contrast=1.06:saturation=1.08",
    },
    "9": {"nama": "Split-Screen Gameplay / Satisfying", "jalur": "split", "filter": ""},
    "10": {"nama": "Chat Story / POV Layar HP", "jalur": "3d", "filter": ""},
    "11": {"nama": "Motion Graphic & Tipografi Kinetik", "jalur": "3d", "filter": ""},
    "12": {"nama": "Peta & Timeline (Map Animation)", "jalur": "3d", "filter": ""},
    "13": {
        "nama": "Listicle / Ranking & Vs Battle",
        "jalur": "media_ai",
        "filter": "eq=contrast=1.1:saturation=1.12",
    },
    "14": {
        "nama": "Talking Head + B-Roll Hybrid",
        "jalur": "lokal",
        "filter": "eq=contrast=1.04:saturation=1.05",
    },
    "15": {
        "nama": "Aesthetic / Slow Cinematic (ASMR)",
        "jalur": "pexels",
        "filter": "eq=brightness=0.02:contrast=0.96:saturation=0.92",
    },
}


def get_ffmpeg_bin():
    ff = shutil.which("ffmpeg")
    if ff:
        return ff
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def terapkan_efek_style(video_in, video_out, style_id="5"):
    preset = PRESET_15_STYLE.get(str(style_id), PRESET_15_STYLE["5"])
    vf = preset["filter"]
    cmd = [get_ffmpeg_bin(), "-y", "-i", video_in]
    if vf:
        cmd += ["-vf", vf]
    cmd += [
        "-af",
        "loudnorm=I=-14:TP=-1.5:LRA=11",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        video_out,
    ]
    subprocess.run(cmd, check=True)
    return preset["nama"]


def gabung_split_screen(video_atas, video_bawah, video_out):
    cmd = [
        get_ffmpeg_bin(),
        "-y",
        "-i",
        video_atas,
        "-stream_loop",
        "-1",
        "-i",
        video_bawah,
        "-filter_complex",
        "[0:v]scale=1080:960:force_original_aspect_ratio=increase,crop=1080:960[top];"
        "[1:v]scale=1080:960:force_original_aspect_ratio=increase,crop=1080:960[bot];"
        "[top][bot]vstack=inputs=2[v]",
        "-map",
        "[v]",
        "-map",
        "0:a?",
        "-shortest",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        video_out,
    ]
    subprocess.run(cmd, check=True)
