# Changelog

Semua perubahan penting pada proyek ini didokumentasikan dalam file ini.

Format mengikuti [Keep a Changelog](https://keepachangelog.com/id/1.0.0/),
dan proyek ini menggunakan [Semantic Versioning](https://semver.org/lang/id/).

## [1.0.0] - 2026-09-16

### Ditambahkan

- Menu interaktif CLI berbasis `inquirer` dengan empat pilihan: tampilkan semua port terbuka, periksa port tertentu, tutup port tertentu, dan keluar.
- `get_open_ports()` untuk menampilkan daftar port berstatus `LISTEN` yang terurut.
- `is_port_open(port)` untuk memeriksa apakah port tertentu terbuka.
- `close_port(port)` untuk menutup port dengan menghentikan proses pemiliknya.
- `clear_screen()` yang kompatibel dengan Windows (`cls`) dan Linux/macOS (`clear`).
- Tampilan informasi sistem dan versi Python saat program dijalankan.
- Penanganan error untuk input port yang tidak valid serta kegagalan `NoSuchProcess`/`PermissionError` saat menutup port.
