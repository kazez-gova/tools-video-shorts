naskah = input("Masukkan paragraf naskah: ")
kalimat = [k.strip() for k in naskah.split(".") if k.strip()]

print("\nHasil potongan per baris:")
for nomor, baris in enumerate(kalimat, 1):
    print(f"{nomor}. {baris}.")
