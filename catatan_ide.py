from datetime import datetime

waktu = datetime.now().strftime("%Y-%m-%d %H:%M")
judul = input("Masukkan ide judul atau topik video: ")
hook = input("Masukkan draf hook (kosongkan jika belum ada): ")

with open("daftar_ide.txt", "a", encoding="utf-8") as file:
    file.write(f"[{waktu}] {judul}\n")
    if hook.strip():
        file.write(f"   Hook: {hook}\n")
    file.write("-" * 40 + "\n")

print("\nIde berhasil disimpan ke daftar_ide.txt!")
