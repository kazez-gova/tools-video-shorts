judul = input("Masukkan judul video Shorts: ")
panjang = len(judul)

print(f"\nPanjang judul: {panjang} karakter")

if panjang <= 40:
    print("Ideal! Judul bakal tampil penuh tanpa terpotong di layar HP.")
elif panjang <= 100:
    print("Aman, tapi bagian belakang judul berpotensi terpotong di tampilan Shorts.")
else:
    print("Terlalu panjang! Batas maksimal judul YouTube adalah 100 karakter.")
