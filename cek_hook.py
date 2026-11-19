hook = input("Masukkan kalimat pembuka (hook) video: ")
jumlah_kata = len(hook.split())
estimasi_detik = round((jumlah_kata / 130) * 60, 1)

print(f"\nJumlah kata hook: {jumlah_kata} kata")
print(f"Estimasi durasi: {estimasi_detik} detik")

if estimasi_detik <= 3.0:
    print("Aman! Hook padat dan pas buat 3 detik pertama.")
else:
    print("Terlalu panjang! Coba pangkas biar bisa dibaca di bawah 3 detik.")
