from __future__ import annotations
import os
import sys
import shlex
import subprocess
from pathlib import Path
from typing import Any, Callable, List, Optional


def enable_virtual_terminal() -> None:
    """Enables virtual terminal processing (ANSI color codes) in Windows console."""
    if os.name != "nt":
        return
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        h_stdout = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_ulong()
        if kernel32.GetConsoleMode(h_stdout, ctypes.byref(mode)):
            kernel32.SetConsoleMode(h_stdout, mode.value | 0x0004)
    except Exception:
        pass


def ensure_standalone_console() -> None:
    """If running interactively on Windows inside Windows Terminal/PowerShell tab,
    relaunch in a dedicated standalone console window so the Aurora logo appears in the taskbar."""
    if os.name != "nt":
        return
    if len(sys.argv) == 1 and os.environ.get("WT_SESSION") and os.environ.get("AURORA_STANDALONE") != "1":
        conhost = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32", "conhost.exe")
        if os.path.exists(conhost):
            env = os.environ.copy()
            env["AURORA_STANDALONE"] = "1"
            if getattr(sys, "frozen", False):
                cmd = [conhost, sys.executable]
            else:
                main_script = Path(sys.argv[0]).resolve()
                cmd = [conhost, sys.executable, str(main_script)]
            subprocess.Popen(cmd, env=env)
            sys.exit(0)


def set_window_icon() -> None:
    """Sets the console window and taskbar icon on Windows using aurora.ico if available."""
    if os.name != "nt":
        return
    try:
        import ctypes
        from ctypes import wintypes

        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("aurora.vcs.bash.1.0")
        except Exception:
            pass

        # Find icon path (support both PyInstaller bundle and script location)
        base_dir = getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)
        icon_path = Path(base_dir) / "aurora.ico"
        if not icon_path.exists():
            icon_path = Path(sys.argv[0]).resolve().parent / "aurora.ico"
        if not icon_path.exists():
            return

        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if not hwnd:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
        if not hwnd:
            return

        IMAGE_ICON = 1
        LR_LOADFROMFILE = 0x00000010
        WM_SETICON = 0x0080
        ICON_SMALL = 0
        ICON_BIG = 1

        LoadImageW = ctypes.windll.user32.LoadImageW
        LoadImageW.argtypes = [
            wintypes.HINSTANCE, wintypes.LPCWSTR, wintypes.UINT,
            ctypes.c_int, ctypes.c_int, wintypes.UINT
        ]
        LoadImageW.restype = wintypes.HANDLE

        SendMessageW = ctypes.windll.user32.SendMessageW
        SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
        SendMessageW.restype = wintypes.LPARAM

        h_icon_big = LoadImageW(None, str(icon_path), IMAGE_ICON, 32, 32, LR_LOADFROMFILE)
        h_icon_small = LoadImageW(None, str(icon_path), IMAGE_ICON, 16, 16, LR_LOADFROMFILE)

        if h_icon_big:
            SendMessageW(hwnd, WM_SETICON, ICON_BIG, h_icon_big)
        if h_icon_small:
            SendMessageW(hwnd, WM_SETICON, ICON_SMALL, h_icon_small)
    except Exception:
        pass


def run_aurora_bash(repo_cls: Any = None, cli_executor: Optional[Callable[[List[str]], None]] = None) -> None:
    """Runs the interactive Aurora Bash shell."""
    if repo_cls is None or cli_executor is None:
        import main
        repo_cls = repo_cls or getattr(main, "Repository", None)
        cli_executor = cli_executor or getattr(main, "execute_cli", None)

    enable_virtual_terminal()
    if os.name == "nt":
        try:
            import ctypes
            ctypes.windll.kernel32.SetConsoleTitleW("Aurora Bash")
        except Exception:
            os.system("title Aurora Bash")
        set_window_icon()

    GREEN = "\033[92m"
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

    banner = rf"""{CYAN}{BOLD}
    _   _   _ ____   ___  ____      _      ____    _    ____  _   _ 
   / \ | | | |  _ \ / _ \|  _ \    / \    | __ )  / \  / ___|| | | |
  / _ \| | | | |_) | | | | |_) |  / _ \   |  _ \ / _ \ \___ \| |_| |
 / ___ \ |_| |  _ <| |_| |  _ <  / ___ \  | |_) / ___ \ ___) |  _  |
/_/   \_\___/|_| \_\\___/|_| \_\/_/   \_\ |____/_/   \_\____/|_| |_|
{RESET}{YELLOW}Aurora Version Control System [Aurora Bash v1.0.0]{RESET}
Type {BOLD}'help'{RESET} or run {BOLD}'init'{RESET}, {BOLD}'status'{RESET}, {BOLD}'add <file>'{RESET}, {BOLD}'commit -m "msg"'{RESET}.
Shell commands: {BOLD}ls{RESET}, {BOLD}cd <dir>{RESET}, {BOLD}pwd{RESET}, {BOLD}clear{RESET}, {BOLD}exit{RESET}.
"""
    print(banner)

    while True:
        cwd = Path.cwd()
        repo = repo_cls()
        branch_str = ""
        if repo.git_dir.exists():
            branch_str = f" {CYAN}({repo.get_current_branch()}){RESET}"

        prompt = f"{GREEN}aurora-user@local{RESET} {YELLOW}{cwd}{RESET}{branch_str}\n$ "

        try:
            line = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting Aurora Bash...")
            break

        if not line:
            continue

        try:
            parts = shlex.split(line)
        except Exception as e:
            print(f"Syntax error: {e}")
            continue

        cmd = parts[0].lower()

        if cmd in ("exit", "quit"):
            print("Exiting Aurora Bash...")
            break
        elif cmd in ("clear", "cls"):
            os.system("cls" if os.name == "nt" else "clear")
            continue
        elif cmd == "pwd":
            print(Path.cwd())
            continue
        elif cmd == "cd":
            target = parts[1] if len(parts) > 1 else str(Path.home())
            try:
                os.chdir(Path(target).expanduser().resolve())
            except Exception as e:
                print(f"cd: {e}")
            continue
        elif cmd in ("ls", "dir"):
            try:
                for item in sorted(Path.cwd().iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
                    prefix = "<DIR> " if item.is_dir() else "      "
                    print(f"{prefix} {item.name}")
            except Exception as e:
                print(f"ls: {e}")
            continue
        elif cmd == "help":
            print("\nAurora Commands:")
            print("  aurora init              - Initialize a new Aurora repository")
            print("  aurora add <files/dirs>  - Stage files or directories")
            print('  aurora commit -m "msg"   - Record staged changes')
            print("  aurora status            - Show working directory and index status")
            print("  aurora log [-n count]    - Show commit history")
            print("  aurora branch [name]     - List, create, or delete branches")
            print("  aurora checkout [-b] <br>- Switch or create branches")
            print("\nShell Commands:")
            print("  cd <path>, ls, pwd, clear, exit\n")
            continue

        # Run aurora command or fallback to system shell
        if cmd == "aurora":
            cli_args = parts[1:]
        elif cmd in ("init", "add", "commit", "checkout", "branch", "log", "status"):
            cli_args = parts
        else:
            try:
                subprocess.run(line, shell=True)
            except Exception as e:
                print(f"Error: {e}")
            continue

        if cli_args and cli_executor:
            cli_executor(cli_args)
