# CekPort

CekPort adalah tool CLI sederhana berbasis menu untuk mengelola port jaringan yang terbuka di komputer lokal. Seluruh antarmuka menggunakan Bahasa Indonesia.

## Fitur

- Menampilkan daftar semua port yang sedang terbuka (status `LISTEN`)
- Memeriksa apakah port tertentu terbuka
- Menutup port tertentu dengan mematikan proses pemiliknya
- Menampilkan informasi sistem dan versi Python

## Persyaratan

- Python 3
- [psutil](https://pypi.org/project/psutil/)
- [inquirer](https://pypi.org/project/inquirer/)

```bash
pip install psutil inquirer
```

## Menjalankan

```bash
python cekport.py
```

## Penggunaan

Setelah dijalankan, program menampilkan menu dengan empat pilihan:

1. **Tampilkan semua port terbuka** — menampilkan daftar port berstatus `LISTEN`.
2. **Periksa apakah port tertentu terbuka** — masukkan nomor port untuk dicek.
3. **Tutup port tertentu** — masukkan nomor port untuk ditutup.
4. **Keluar** — keluar dari program.

> **Perhatian:** opsi *Tutup port tertentu* menghentikan **proses** yang memiliki port tersebut, bukan hanya koneksinya. Menutup port dapat mematikan aplikasi yang sedang berjalan.

## Struktur

Seluruh logika berada di `cekport.py`:

- `clear_screen()` — membersihkan layar terminal.
- `get_open_ports()` — mengembalikan daftar port berstatus `LISTEN` yang terurut.
- `is_port_open(port)` — memeriksa apakah `port` termasuk port yang terbuka.
- `close_port(port)` — mencari koneksi `LISTEN` pada port tersebut dan menghentikan proses pemiliknya.
- `main()` — menampilkan info sistem lalu menjalankan loop menu.

## Catatan

- Berjalan di Windows maupun Linux/macOS; `clear_screen()` memilih `cls` atau `clear` berdasarkan `os.name`.
- Menutup port dapat memunculkan `PermissionError` (misalnya proses milik sistem). Pesan kegagalan ditampilkan tanpa menghentikan program.
