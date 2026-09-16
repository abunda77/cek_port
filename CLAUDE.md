# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

CekPort is a single-file, menu-driven CLI tool (`cekport.py`) for managing open network ports on the local machine. All UI text is in Indonesian. The only entry point is `main()`, guarded by `if __name__ == "__main__"`.

There is no test suite, linter config, or build step. The tool is interactive (uses `inquirer.prompt`), so it cannot be meaningfully exercised through a non-interactive shell.

## Running

```bash
python cekport.py
```

## Dependencies

- `psutil` — enumerates and terminates listening connections
- `inquirer` — terminal menu prompt
- stdlib `os` and `platform` only

Both third-party packages are installed globally (this project has no `requirements.txt` or virtualenv). `psutil` on Windows requires no special setup; terminating a listening process may raise `PermissionError`, which the tool already swallows with a user-facing message.

## Structure

Everything lives in `cekport.py`:

- `get_open_ports()` — returns a sorted list of ports whose connections have status `LISTEN`.
- `is_port_open(port)` — membership test via `get_open_ports()`.
- `close_port(port)` — finds the LISTEN connection on that port, terminates its owning process, then reports success/failure.
- `main()` — prints system info, then loops on an `inquirer.List` menu with four choices: list all open ports, check a port, close a port, exit.

There is no module split, config, or data layer — the sole non-UI logic is the three port helpers.

## Notes

- All output messages are in Bahasa Indonesia; keep new UI strings in Indonesian to match.
- `close_port()` terminates the process owning the port (not just the connection) — flag this to the user whenever the behavior of that menu option is discussed.
- The program works on any OS but `clear_screen()` branches on `os.name` to pick `cls` vs `clear`.