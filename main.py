import subprocess
import sys

menu = {
    "1": ("Hitung Durasi Naskah", "hitung_durasi.py"),
    "2": ("Pecah Naskah Jadi Per Baris", "pecah_naskah.py"),
    "3": ("Buat Template Deskripsi & Hashtag", "template_deskripsi.py"),
    "4": ("Cek Durasi Hook Pembuka", "cek_hook.py"),
    "5": ("Catat Ide Konten Baru", "catatan_ide.py"),
    "6": ("Cek Panjang Karakter Judul", "cek_judul.py"),
    "7": ("Cari / Tampilkan Daftar Ide", "cari_ide.py"),
}

while True:
    print("\n" + "=" * 42)
    print("        TOOLS VIDEO SHORTS - MENU")
    print("=" * 42)
    for kunci, (label, _) in menu.items():
        print(f"{kunci}. {label}")
    print("0. Keluar")
    print("=" * 42)

    pilihan = input("Pilih nomor menu: ").strip()

    if pilihan == "0":
        print("Selesai! Sampai ketemu di project berikutnya.")
        break
    elif pilihan in menu:
        label, file_skrip = menu[pilihan]
        print(f"\n--- Menjalankan {label} ---\n")
        subprocess.run([sys.executable, file_skrip])
        input("\nTekan Enter untuk kembali ke menu...")
    else:
        print("Pilihan tidak valid, coba masukkan angka 0-7.")
