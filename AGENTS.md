# Panduan Agen

- Proyek ini adalah CLI interaktif satu file; entrypoint-nya `cekport.py:main()` dan guard `if __name__ == "__main__"`.
- Instal dependensi dari `requirements.txt` (`psutil`, `inquirer`) sebelum menjalankan program: `python -m pip install -r requirements.txt`.
- Jalankan aplikasi dengan `python cekport.py`; alur utamanya membutuhkan terminal interaktif sehingga tidak bermakna diuji lewat shell non-interaktif.
- Logika port berada di `cekport.py`: `get_open_ports()` hanya mengambil koneksi berstatus `LISTEN`, sedangkan `is_port_open()` memindai ulang koneksi.
- `close_port()` menghentikan proses pemilik port melalui `psutil.Process.terminate()`, bukan sekadar menutup koneksi; operasi dapat gagal karena `PermissionError` atau proses sudah tidak ada.
- Pertahankan seluruh teks antarmuka baru dalam Bahasa Indonesia dan dukung pembersihan layar lintas platform (`cls` di Windows, `clear` selain Windows).
- Tidak ada test suite, konfigurasi linter/type-checker, build step, atau codegen yang terdeteksi; verifikasi perubahan dilakukan dengan inspeksi dan bila relevan menjalankan aplikasi secara interaktif.
- `README.md` dan `CLAUDE.md` adalah referensi repository yang ada; jika instruksinya bertentangan dengan file eksekusi atau `requirements.txt`, ikuti sumber eksekusi.
