import psutil
import platform
import inquirer
import os

def clear_screen():
    """Membersihkan layar terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_open_ports():
    """Mengambil daftar port yang terbuka."""
    open_ports = set()
    for conn in psutil.net_connections():
        if conn.status == 'LISTEN':
            open_ports.add(conn.laddr.port)
    return sorted(open_ports)

def is_port_open(port):
    """Memeriksa apakah port tertentu terbuka."""
    open_ports = get_open_ports()
    return port in open_ports

def close_port(port):
    """Menutup port tertentu."""
    for conn in psutil.net_connections():
        if conn.laddr.port == port and conn.status == 'LISTEN':
            try:
                process = psutil.Process(conn.pid)
                process.terminate()
                print(f"Port {port} berhasil ditutup")
                return
            except (psutil.NoSuchProcess, PermissionError) as e:
                print(f"Gagal menutup port {port}: {str(e)}")
                return
    print(f"Port {port} tidak ditemukan atau tidak terbuka")

def main():
    clear_screen()
    print(f"System: {platform.system()} {platform.release()}")
    print(f"Python Version: {platform.python_version()}")
    print("\nSelamat datang di CekPort!")

    while True:
        questions = [
            inquirer.List('pilihan',
                          message="Pilih tindakan:",
                          choices=[
                              ('Tampilkan semua port terbuka', '1'),
                              ('Periksa apakah port tertentu terbuka', '2'),
                              ('Tutup port tertentu', '3'),
                              ('Keluar', '4'),
                          ]),
        ]
        jawaban = inquirer.prompt(questions)
        pilihan = jawaban['pilihan']

        if pilihan == '1':
            clear_screen()
            ports = get_open_ports()
            if ports:
                print("\nDaftar port yang terbuka:")
                for port in ports:
                    print(f"Port {port}")
            else:
                print("Tidak ada port yang terbuka.")
            input("\nTekan Enter untuk melanjutkan...")
            clear_screen()

        elif pilihan == '2':
            clear_screen()
            try:
                port = int(input("Masukkan nomor port yang ingin diperiksa: "))
                if is_port_open(port):
                    print(f"Port {port} terbuka")
                else:
                    print(f"Port {port} tidak terbuka")
            except ValueError:
                print("Masukkan nomor port yang valid.")
            input("\nTekan Enter untuk melanjutkan...")
            clear_screen()

        elif pilihan == '3':
            clear_screen()
            try:
                port = int(input("Masukkan nomor port yang ingin ditutup: "))
                close_port(port)
            except ValueError:
                print("Masukkan nomor port yang valid.")
            input("\nTekan Enter untuk melanjutkan...")
            clear_screen()

        elif pilihan == '4':
            print("Keluar dari program")
            break

        else:
            print("Pilihan tidak valid. Silakan coba lagi.")

if __name__ == "__main__":
    main()
