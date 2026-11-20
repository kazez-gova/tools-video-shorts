import os

nama_file = "daftar_ide.txt"

if not os.path.exists(nama_file):
    print("Belum ada catatan ide. Jalankan catatan_ide.py dulu buat nyimpen ide pertama!")
else:
    kata_kunci = input("Masukkan kata kunci pencarian (kosongkan untuk tampilkan semua): ").strip().lower()
    
    with open(nama_file, "r", encoding="utf-8") as file:
        isi = file.read().strip()
        
    daftar = [item.strip() for item in isi.split("-" * 40) if item.strip()]
    hasil = [item for item in daftar if kata_kunci in item.lower()]
    
    print(f"\nDitemukan {len(hasil)} ide:")
    print("=" * 40)
    for item in hasil:
        print(item)
        print("-" * 40)
