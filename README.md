# CekPort

CekPort adalah tool CLI sederhana berbasis menu untuk mengelola port jaringan yang terbuka di komputer lokal. Seluruh antarmuka menggunakan Bahasa Indonesia.

## Fitur

- Menampilkan daftar semua port yang sedang terbuka (status `LISTEN`) dalam tabel sejajar berisi port, PID, nama proses, dan alamat
- Memeriksa apakah port tertentu terbuka, lengkap dengan info proses pemiliknya
- Menutup port tertentu dengan mematikan proses pemiliknya, diawali konfirmasi
- Menampilkan informasi sistem dan versi Python
- Antarmuka berwarna dengan glyph kotak; otomatis turun ke mode polos/ASCII bila terminal tidak mendukung

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

1. **Tampilkan semua port terbuka** — menampilkan tabel port berstatus `LISTEN` beserta PID, nama proses, dan alamatnya.
2. **Periksa apakah port tertentu terbuka** — masukkan nomor port untuk dicek; hasilnya disertai info proses pemilik.
3. **Tutup port tertentu** — masukkan nomor port, tinjau proses yang akan dihentikan, lalu jawab konfirmasi `(y/N)`.
4. **Keluar** — keluar dari program.

> **Perhatian:** opsi *Tutup port tertentu* menghentikan **proses** yang memiliki port tersebut, bukan hanya koneksinya. Menutup port dapat mematikan aplikasi yang sedang berjalan.

## Struktur

Seluruh logika berada di `cekport.py`:

- `clear_screen()` — membersihkan layar terminal.
- `configure_appearance()` — memilih token warna dan glyph sesuai kemampuan terminal.
- `print_banner()` / `print_section()` / `print_table()` / `print_status()` — primitif tampilan (banner, judul tindakan, tabel, baris status).
- `get_open_ports()` — mengembalikan daftar port berstatus `LISTEN` yang terurut.
- `is_port_open(port)` — memeriksa apakah `port` termasuk port yang terbuka.
- `get_listeners()` / `find_listener(port)` — daftar port beserta PID, nama proses, dan alamatnya.
- `close_port(port)` — mencari koneksi `LISTEN` pada port tersebut, menghentikan proses pemiliknya, dan mengembalikan `CloseResult(ok, message, detail)`.
- `main()` — menampilkan info sistem lalu menjalankan loop menu.

## Catatan

- Berjalan di Windows maupun Linux/macOS; `clear_screen()` memilih `cls` atau `clear` berdasarkan `os.name`.
- Warna ANSI dinonaktifkan otomatis saat keluaran dialihkan (bukan terminal). Isi `NO_COLOR=1` untuk mematikan paksa, atau `FORCE_COLOR=1` untuk memaksa warna.
- Glyph kotak (`╭─╮`) turun otomatis ke ASCII (`+-+`) bila encoding terminal tidak mendukung Unicode.
- Menutup port dapat memunculkan `PermissionError`/`AccessDenied` (misalnya proses milik sistem). Pesan kegagalan ditampilkan tanpa menghentikan program.
- `close_port()` menunggu maksimal 3 detik; bila proses belum berhenti, program melaporkan bahwa permintaan sudah dikirim.
