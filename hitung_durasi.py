naskah = input("Masukkan teks naskah voice-over: ")
jumlah_kata = len(naskah.split())
estimasi_detik = round((jumlah_kata / 130) * 60, 1)

print(f"Jumlah kata: {jumlah_kata} kata")
print(f"Estimasi durasi bicara: {estimasi_detik} detik")
if estimasi_detik > 60:
    print("Peringatan: Durasi berpotensi melebihi batas 60 detik untuk Shorts.")
