"""CekPort — periksa dan kelola port yang sedang terbuka di komputer lokal.

Antarmuka teks berbahasa Indonesia dengan warna ANSI, tabel sejajar, dan
konfirmasi sebelum menghentikan proses. Warna otomatis dimatikan bila
keluaran bukan terminal, bila variabel lingkungan ``NO_COLOR`` diisi, atau
bila konsol Windows menolak mode ANSI. Glyph kotak otomatis turun ke versi
ASCII bila encoding terminal tidak mendukung Unicode.
"""

from __future__ import annotations

import os
import platform
import shutil
import sys
from collections import namedtuple

import inquirer
import psutil
from inquirer import themes as inquirer_themes

APP_NAME = "CekPort"
APP_TAGLINE = "Pemeriksa & pengelola port lokal"
APP_VERSION = "1.1.0"

Listener = namedtuple("Listener", "port pid process address")
CloseResult = namedtuple("CloseResult", "ok message detail")


# ---------------------------------------------------------------------------
# Token tampilan
# ---------------------------------------------------------------------------


class Tokens:
    """Token gaya ANSI.

    Seluruh warna dan atribut dirujuk melalui atribut kelas ini sehingga
    tidak ada kode escape mentah yang tersebar di badan kode. Saat warna
    dinonaktifkan, semua token bernilai string kosong.
    """

    def __init__(self, enabled: bool = True) -> None:
        def esc(*codes: int) -> str:
            return "\x1b[" + ";".join(str(code) for code in codes) + "m" if enabled else ""

        self.bold = esc(1)
        self.title = esc(1, 96)
        self.accent = esc(96)
        self.ok = esc(92)
        self.warn = esc(93)
        self.error = esc(91)
        self.muted = esc(90)
        self.reset = esc(0)
        self.enabled = enabled


UNICODE_GLYPHS = {
    "tl": "\u256d",
    "tr": "\u256e",
    "bl": "\u2570",
    "br": "\u256f",
    "h": "\u2500",
    "v": "\u2502",
    "tick": "\u2713",
    "cross": "\u2717",
    "dot": "\u00b7",
    "caret": "\u276f",
    "warn": "!",
    "ellipsis": "\u2026",
}

ASCII_GLYPHS = {
    "tl": "+",
    "tr": "+",
    "bl": "+",
    "br": "+",
    "h": "-",
    "v": "|",
    "tick": "v",
    "cross": "x",
    "dot": "-",
    "caret": ">",
    "warn": "!",
    "ellipsis": "...",
}

T = Tokens(enabled=False)
G = dict(ASCII_GLYPHS)


def _enable_windows_ansi() -> bool:
    """Mengaktifkan pemrosesan escape ANSI pada konsol Windows."""
    if os.name != "nt":
        return True
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        ok = False
        for handle_id in (-11, -12):  # STD_OUTPUT_HANDLE, STD_ERROR_HANDLE
            handle = kernel32.GetStdHandle(handle_id)
            mode = ctypes.c_uint32()
            if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                continue
            if kernel32.SetConsoleMode(handle, mode.value | 0x0004):
                ok = True
        return ok
    except Exception:
        return False


def _supports_color(stream) -> bool:
    """Menentukan apakah keluaran layak diberi warna."""
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    if os.environ.get("TERM") == "dumb":
        return False
    if not hasattr(stream, "isatty") or not stream.isatty():
        return False
    return _enable_windows_ansi()


def _supports_unicode() -> bool:
    """Menentukan apakah terminal mampu mencetak glyph kotak Unicode."""
    encoding = getattr(sys.stdout, "encoding", None) or "ascii"
    try:
        "".join(UNICODE_GLYPHS.values()).encode(encoding)
    except (UnicodeEncodeError, LookupError):
        return False
    return True


def configure_appearance() -> None:
    """Menetapkan token warna dan glyph sesuai kemampuan terminal."""
    global T, G
    T = Tokens(enabled=_supports_color(sys.stdout))
    G = dict(UNICODE_GLYPHS if _supports_unicode() else ASCII_GLYPHS)


# ---------------------------------------------------------------------------
# Primitif tata letak
# ---------------------------------------------------------------------------


def clear_screen() -> None:
    """Membersihkan layar terminal."""
    os.system("cls" if os.name == "nt" else "clear")


def terminal_width(default: int = 80) -> int:
    """Lebar terminal aktif, minimal 40 kolom, agar tabel tetap terbaca."""
    try:
        columns = shutil.get_terminal_size((default, 24)).columns
    except Exception:
        columns = default
    return max(columns, 40)


def truncate(text: str, width: int) -> str:
    """Memotong teks agar muat pada kolom tabel, memakai penanda elipsis."""
    if width <= 0:
        return ""
    text = str(text)
    if len(text) <= width:
        return text
    ellipsis = G["ellipsis"]
    if width <= len(ellipsis):
        return text[:width]
    return text[: width - len(ellipsis)] + ellipsis


def print_banner() -> None:
    """Menampilkan banner aplikasi beserta informasi sistem."""
    title = f"{APP_NAME}  {G['dot']}  v{APP_VERSION}"
    subtitle = APP_TAGLINE
    width = min(max(len(title), len(subtitle)) + 2, terminal_width() - 4)

    print()
    print(f"  {T.accent}{G['tl']}{G['h'] * width}{G['tr']}{T.reset}")
    print(f"  {T.accent}{G['v']}{T.reset} {T.title}{title.ljust(width - 2)}{T.reset} {T.accent}{G['v']}{T.reset}")
    print(f"  {T.accent}{G['v']}{T.reset} {T.muted}{subtitle.ljust(width - 2)}{T.reset} {T.accent}{G['v']}{T.reset}")
    print(f"  {T.accent}{G['bl']}{G['h'] * width}{G['br']}{T.reset}")
    print()
    system = f"{platform.system()} {platform.release()}"
    print(f"  {T.muted}{system}  {G['dot']}  Python {platform.python_version()}{T.reset}")
    print()


def print_section(title: str, subtitle: str | None = None) -> None:
    """Judul tindakan yang sedang dijalankan."""
    print()
    print(f"  {T.title}{title}{T.reset}")
    if subtitle:
        print(f"  {T.muted}{subtitle}{T.reset}")
    print()


def print_status(ok: bool, message: str, detail: str | None = None) -> None:
    """Satu baris hasil dengan glyph status berwarna."""
    color = T.ok if ok else T.error
    glyph = G["tick"] if ok else G["cross"]
    print(f"  {color}{glyph}{T.reset}  {message}")
    if detail:
        print(f"     {T.muted}{detail}{T.reset}")


def print_note(message: str) -> None:
    """Catatan netral tanpa status berhasil/gagal."""
    print(f"  {T.muted}{G['dot']} {message}{T.reset}")


def pause() -> None:
    """Menahan layar sampai pengguna menekan Enter."""
    print()
    try:
        input(f"  {T.muted}Tekan Enter untuk kembali ke menu...{T.reset}")
    except (EOFError, KeyboardInterrupt):
        print()


def _clear_line() -> None:
    print("\r" + " " * (terminal_width() - 1) + "\r", end="", flush=True)


def _pad(text: str, width: int, align: str) -> str:
    text = truncate(text, width)
    return text.rjust(width) if align == "right" else text.ljust(width)


def print_table(headers, rows, aligns=None, indent: str = "  ", gap: str = "  ") -> None:
    """Mencetak tabel sejajar yang menyusut mengikuti lebar terminal."""
    if not rows:
        return
    aligns = aligns or ["left"] * len(headers)
    rows = [["-" if cell is None else str(cell) for cell in row] for row in rows]
    widths = [max([len(headers[i])] + [len(row[i]) for row in rows]) for i in range(len(headers))]

    available = terminal_width() - len(indent) - 1
    while sum(widths) + len(gap) * (len(widths) - 1) > available:
        shrinkable = [i for i, width in enumerate(widths) if width > 8]
        if not shrinkable:
            break
        widths[max(shrinkable, key=lambda i: widths[i])] -= 1

    header_cells = []
    for i, header in enumerate(headers):
        text = _pad(header, widths[i], aligns[i]) if i < len(headers) - 1 else truncate(header, widths[i])
        header_cells.append(f"{T.muted}{text}{T.reset}")
    print(f"{indent}{T.bold}{gap.join(header_cells)}{T.reset}")
    print(f"{indent}{T.muted}{G['h'] * (sum(widths) + len(gap) * (len(widths) - 1))}{T.reset}")

    for row in rows:
        cells = []
        for i, value in enumerate(row):
            text = truncate(value, widths[i])
            if aligns[i] == "right":
                text = text.rjust(widths[i])
            elif i < len(row) - 1:
                text = text.ljust(widths[i])
            if i == 0:
                cells.append(f"{T.accent}{text}{T.reset}")
            elif i == 1 and text.strip() in ("", "-"):
                cells.append(f"{T.muted}{text}{T.reset}")
            else:
                cells.append(text)
        print(f"{indent}{gap.join(cells)}")


def build_theme(enabled: bool):
    """Tema inquirer yang memakai token warna yang sama dengan tabel."""
    theme = inquirer_themes.Default()
    theme.Question.mark_color = T.accent if enabled else ""
    theme.Question.brackets_color = T.muted if enabled else ""
    theme.Question.default_color = T.muted if enabled else ""
    theme.List.selection_color = T.accent if enabled else ""
    theme.List.unselected_color = ""
    theme.List.selection_cursor = G["caret"]
    theme.Checkbox.selection_color = T.accent if enabled else ""
    theme.Checkbox.selected_color = T.ok if enabled else ""
    theme.Checkbox.unselected_color = ""
    return theme


def ask(questions):
    """Membungkus inquirer.prompt agar pembatalan tetap berbahasa Indonesia."""
    try:
        return inquirer.prompt(questions, theme=build_theme(T.enabled), raise_keyboard_interrupt=True)
    except KeyboardInterrupt:
        print()
        print_note("Dibatalkan.")
        return None


# ---------------------------------------------------------------------------
# Logika port
# ---------------------------------------------------------------------------


def get_open_ports():
    """Mengambil daftar port yang terbuka."""
    open_ports = set()
    for conn in psutil.net_connections():
        if conn.status == "LISTEN":
            open_ports.add(conn.laddr.port)
    return sorted(open_ports)


def is_port_open(port):
    """Memeriksa apakah port tertentu terbuka."""
    open_ports = get_open_ports()
    return port in open_ports


def format_address(address) -> str:
    """Menyusun alamat ``host:port`` dari ``conn.laddr``."""
    host = getattr(address, "ip", None)
    port = getattr(address, "port", None)
    if port is None:
        return ""
    if isinstance(host, (tuple, list)):
        host = host[0] if host else ""
    host = host or "0.0.0.0"
    return f"[{host}]:{port}" if ":" in host else f"{host}:{port}"


def process_name(pid) -> str:
    """Nama proses pemilik port, atau '-' bila tidak dapat dibaca."""
    if not pid:
        return "-"
    try:
        return psutil.Process(pid).name()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, OSError):
        return "-"


def get_listeners():
    """Daftar koneksi LISTEN, satu baris per port, lengkap dengan prosesnya."""
    grouped: dict = {}
    for conn in psutil.net_connections(kind="inet"):
        if conn.status != "LISTEN":
            continue
        try:
            port = conn.laddr.port
        except AttributeError:
            continue
        entry = grouped.setdefault(port, {"pids": [], "addresses": []})
        address = format_address(conn.laddr)
        if address and address not in entry["addresses"]:
            entry["addresses"].append(address)
        if conn.pid and conn.pid not in entry["pids"]:
            entry["pids"].append(conn.pid)

    listeners = []
    for port, entry in grouped.items():
        pid = entry["pids"][0] if entry["pids"] else None
        listeners.append(
            Listener(
                port=port,
                pid=pid,
                process=process_name(pid),
                address=", ".join(entry["addresses"]),
            )
        )
    return sorted(listeners, key=lambda listener: listener.port)


def find_listener(port):
    """Mencari satu listener berdasarkan nomor port."""
    for listener in get_listeners():
        if listener.port == port:
            return listener
    return None


def describe_listener(listener: Listener) -> str:
    """Ringkasan satu baris: proses, PID, dan alamat."""
    pid = listener.pid if listener.pid else "-"
    parts = [listener.process or "-", f"PID {pid}"]
    if listener.address:
        parts.append(listener.address)
    return f" {G['dot']} ".join(parts)


def close_port(port):
    """Menutup port tertentu dengan menghentikan proses pemiliknya."""
    for conn in psutil.net_connections():
        if not conn.laddr or conn.laddr.port != port or conn.status != "LISTEN":
            continue
        if not conn.pid:
            return CloseResult(False, f"Port {port} tidak dapat ditutup", "PID pemilik port tidak diketahui.")
        try:
            process = psutil.Process(conn.pid)
            name = process_name(conn.pid)
            process.terminate()
            try:
                process.wait(timeout=3)
            except psutil.TimeoutExpired:
                return CloseResult(
                    True,
                    f"Permintaan penutupan port {port} sudah dikirim",
                    f"Proses {name} (PID {conn.pid}) belum berhenti — periksa kembali sebentar lagi.",
                )
            return CloseResult(True, f"Port {port} berhasil ditutup", f"Proses {name} (PID {conn.pid}) dihentikan.")
        except psutil.NoSuchProcess:
            return CloseResult(False, f"Proses pemilik port {port} sudah tidak berjalan", None)
        except (PermissionError, psutil.AccessDenied):
            return CloseResult(
                False,
                f"Gagal menutup port {port}",
                "Akses ditolak — jalankan ulang sebagai administrator/root.",
            )
    return CloseResult(False, f"Port {port} tidak ditemukan atau tidak terbuka", None)


# ---------------------------------------------------------------------------
# Alur antarmuka
# ---------------------------------------------------------------------------

MENU = (
    ("1", "Tampilkan semua port terbuka", "Daftar port berstatus LISTEN beserta proses pemiliknya"),
    ("2", "Periksa port tertentu", "Cek apakah satu nomor port sedang terbuka"),
    ("3", "Tutup port tertentu", "Hentikan proses yang memiliki port tersebut"),
    ("4", "Keluar", "Tutup aplikasi CekPort"),
)


def prompt_menu():
    """Menampilkan menu utama dan mengembalikan kode pilihan."""
    choices = []
    hints = {}
    for key, label, hint in MENU:
        text = f"{T.accent}{key}{T.reset}  {label}" if T.enabled else f"{key}  {label}"
        choices.append((text, key))
        hints[(text, key)] = hint
    answers = ask([inquirer.List("pilihan", message="Pilih tindakan", choices=choices, hints=hints)])
    return answers["pilihan"] if answers else None


def prompt_port(message: str):
    """Meminta nomor port yang valid (1-65535)."""

    def validate(_, value):
        value = (value or "").strip()
        if not value.isdigit():
            raise inquirer.errors.ValidationError("", reason="Masukkan angka port, contoh: 3000")
        if not 1 <= int(value) <= 65535:
            raise inquirer.errors.ValidationError("", reason="Rentang port yang valid adalah 1-65535")
        return True

    answers = ask([inquirer.Text("port", message=message, validate=validate)])
    answer = str((answers or {}).get("port", "")).strip()
    return int(answer) if answer.isdigit() and 1 <= int(answer) <= 65535 else None


def scan_listeners():
    """Memindai koneksi sambil menampilkan indikator singkat."""
    if T.enabled:
        print(f"  {T.muted}{G['dot']} Memindai koneksi...{T.reset}", end="\r", flush=True)
    try:
        return get_listeners()
    finally:
        if T.enabled:
            _clear_line()


def action_list() -> None:
    print_section("Port yang sedang terbuka", "Hanya koneksi berstatus LISTEN yang ditampilkan.")
    listeners = scan_listeners()
    if not listeners:
        print_note("Tidak ada port yang terbuka saat ini.")
        return
    rows = [
        (str(l.port), str(l.pid) if l.pid else "-", l.process or "-", l.address or "-") for l in listeners
    ]
    print_table(("PORT", "PID", "PROSES", "ALAMAT"), rows, aligns=("right", "right", "left", "left"))
    print()
    print_note(f"{len(listeners)} port terbuka.")


def action_check() -> None:
    print_section("Periksa port tertentu")
    port = prompt_port("Nomor port yang ingin diperiksa")
    if port is None:
        return
    print()
    listener = find_listener(port)
    if listener:
        print_status(True, f"Port {port} TERBUKA", describe_listener(listener))
    else:
        print_status(False, f"Port {port} tertutup", "Tidak ada koneksi LISTEN pada port tersebut.")


def action_close() -> None:
    print_section("Tutup port tertentu", "Proses pemilik port akan dihentikan, bukan hanya koneksinya.")
    port = prompt_port("Nomor port yang ingin ditutup")
    if port is None:
        return

    print()
    listener = find_listener(port)
    if listener is None:
        print_status(False, f"Port {port} tidak terbuka", "Tidak ada proses yang perlu dihentikan.")
        return

    print(f"  {T.warn}{G['warn']}{T.reset}  {describe_listener(listener)}")
    answers = ask(
        [
            inquirer.Confirm(
                "lanjut",
                message=f"Hentikan proses tersebut dan tutup port {port}",
                default=False,
            )
        ]
    )
    if not answers or not answers.get("lanjut"):
        print()
        print_note(f"Port {port} tidak diubah.")
        return

    print()
    if T.enabled:
        print(f"  {T.muted}{G['dot']} Menghentikan proses...{T.reset}", end="\r", flush=True)
    try:
        result = close_port(port)
    finally:
        if T.enabled:
            _clear_line()
    print_status(result.ok, result.message, result.detail)


ACTIONS = {
    "1": action_list,
    "2": action_check,
    "3": action_close,
}


def main() -> None:
    configure_appearance()
    clear_screen()
    print_banner()

    while True:
        choice = prompt_menu()

        if choice is None or choice == "4":
            clear_screen()
            print()
            print(f"  {T.muted}Sampai jumpa.{T.reset}")
            print()
            break

        action = ACTIONS.get(choice)
        if action is None:
            print_note("Pilihan tidak valid.")
            continue

        try:
            action()
        except (psutil.Error, OSError) as error:
            print()
            print_status(False, "Gagal membaca data port", str(error))

        pause()
        clear_screen()
        print_banner()


if __name__ == "__main__":
    main()
