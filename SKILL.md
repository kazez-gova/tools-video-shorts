---
name: tools-video-shorts
description: "Kumpulan utilitas Python untuk mempercepat produksi konten video Shorts, mulai dari cek durasi naskah, pecah baris voice-over, cek hook 3 detik, cek panjang judul, template deskripsi, hingga pencatatan ide."
---

# Tools Video Shorts

Gunakan kumpulan skrip Python di dalam paket skill ini untuk membantu pengguna menyiapkan naskah, judul, deskripsi, dan ide konten video Shorts secara cepat.

## Daftar Skrip & Fungsi

1. `main.py` [G Menu utama interaktif untuk menjalankan seluruh alat dari satu layar terminal.
2. `hitung_durasi.py` [G Menghitung estimasi durasi baca naskah agar sesuai batas waktu video singkat.
3. `pecah_naskah.py` [G Memecah paragraf panjang menjadi kalimat pendek per baris agar mudah dibaca saat rekaman *voice-over*.
4. `template_deskripsi.py` [G Menyusun format deskripsi video dan *hashtag* otomatis dari judul dan kata kunci.
5. `cek_hook.py` [G Mengukur jumlah kata dan estimasi waktu kalimat pembuka agar padat di bawah 3 detik pertama.
6. `catatan_ide.py` [G Menyimpan draf ide judul dan *hook* beserta catatan waktu ke file `daftar_ide.txt`.
7. `cek_judul.py` [G Mengecek panjang karakter judul agar tidak terpotong di layar HP (ideal maksimal 40 karakter).
8. `cari_ide.py` [G Mencari dan menampilkan kembali draf ide konten yang tersimpan di `daftar_ide.txt` berdasarkan kata kunci.

## Cara Menggunakan

- Jika pengguna meminta pengecekan naskah, *hook*, atau judul secara langsung di *chat*, terapkan logika dan batasan yang sama seperti pada skrip terkait.
- Jika pengguna ingin menjalankan skrip secara lokal, arahkan untuk menjalankan `python main.py` atau `python <nama_file>.py` di dalam direktori proyek.
