judul = input("Masukkan judul video Shorts: ")
topik = input("Masukkan kata kunci topik (pisahkan dengan koma): ")

tags = " ".join([f"#{t.strip().replace(' ', '')}" for t in topik.split(",") if t.strip()])

print("\n--- HASIL DESKRIPSI ---")
print(f"{judul}\n")
print("Jangan lupa subscribe biar nggak ketinggalan video singkat lainnya!")
print(f"\n#Shorts #YouTubeShorts {tags}")
