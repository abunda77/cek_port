# Changelog

Semua perubahan penting pada proyek ini didokumentasikan dalam file ini.

Format mengikuti [Keep a Changelog](https://keepachangelog.com/id/1.0.0/),
dan proyek ini menggunakan [Semantic Versioning](https://semver.org/lang/id/).

## [1.1.0] - 2026-09-16

### Diubah

- Tampilan terminal ditulis ulang: banner panel, tabel port sejajar (PORT/PID/PROSES/ALAMAT), baris status berwarna, dan jeda "Tekan Enter" yang seragam.
- Menu utama memakai `inquirer` bertema khusus dan menampilkan keterangan singkat untuk setiap pilihan.
- Masukan nomor port memakai prompt `inquirer` dengan validasi rentang 1-65535, menggantikan `input()` + `try/except ValueError`.
- Opsi tutup port kini menampilkan proses yang akan dihentikan dan meminta konfirmasi `(y/N)` sebelum bertindak.
- Pesan hasil dikelompokkan menjadi berhasil/gagal dengan detail proses, dan pembatalan (`Ctrl+C`) dilaporkan dalam Bahasa Indonesia.

### Ditambahkan

- Token warna ANSI tersentralisasi (`Tokens`) dengan deteksi otomatis: mati saat bukan terminal, saat `NO_COLOR` diisi, atau saat konsol Windows menolak mode ANSI.
- Dukungan `FORCE_COLOR` untuk memaksa warna dan fallback glyph ASCII saat encoding terminal tidak Unicode.
- `get_listeners()` dan `find_listener(port)` untuk menampilkan PID, nama proses, dan alamat tiap port.
- Tabel adaptif yang menyusut dan memakai elipsis bila terminal sempit.
- `close_port()` menunggu proses berhenti maksimal 3 detik dan mengembalikan `CloseResult(ok, message, detail)`.
- `APP_VERSION` pada banner aplikasi.

## [1.0.0] - 2026-09-16

### Ditambahkan

- Menu interaktif CLI berbasis `inquirer` dengan empat pilihan: tampilkan semua port terbuka, periksa port tertentu, tutup port tertentu, dan keluar.
- `get_open_ports()` untuk menampilkan daftar port berstatus `LISTEN` yang terurut.
- `is_port_open(port)` untuk memeriksa apakah port tertentu terbuka.
- `close_port(port)` untuk menutup port dengan menghentikan proses pemiliknya.
- `clear_screen()` yang kompatibel dengan Windows (`cls`) dan Linux/macOS (`clear`).
- Tampilan informasi sistem dan versi Python saat program dijalankan.
- Penanganan error untuk input port yang tidak valid serta kegagalan `NoSuchProcess`/`PermissionError` saat menutup port.
