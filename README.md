# Aurora

A lightweight, from-scratch version control system written in Python, inspired by the architecture and internals of Git.

Aurora was built to explore how Git really works under the hood — content-addressable storage, SHA-1 hashed blobs, trees, commits, an isolated staging area, and branch pointers — completely from scratch with **zero external dependencies**.

---

## ⚡ Quick Start: Download Aurora Bash (Windows Standalone)

You don't need Python or any dev environment installed to start using Aurora.

We provide a pre-built standalone executable with an interactive shell called **Aurora Bash**:

1. Head over to the **[Latest GitHub Releases](https://github.com/moksh033/Aurora/releases/latest)**.
2. Download `aurora.exe` (or `aurora-windows-x64-v1.0.zip`).
3. Double-click `aurora.exe` to launch **Aurora Bash** directly in its own dedicated terminal interface with custom branding.
4. *(Optional)* Add `aurora.exe` to your Windows `PATH` if you'd like to invoke `aurora <command>` from PowerShell, CMD, or any external terminal.

---

## What Aurora Can Do

- **Object Storage (`.aurora/objects`)**: Compresses and stores file contents (Blobs), directories (Trees), and history checkpoints (Commits) indexed by SHA-1 hashes using `zlib`.
- **Staging Index (`.aurora/index`)**: A working staging area to prepare commits file-by-file or directory-wide.
- **Commit History & Graphs**: Track parent commit hashes, author timestamps, and formatted commit logs.
- **Branching & HEAD Pointers**: Seamlessly create, switch, and delete branches.
- **Working Tree Inspection**: Real-time status detection for untracked, modified, staged, and deleted files.
- **Dual Mode Interface**:
  - Run as a traditional CLI utility (`aurora init`, `aurora commit -m "..."`).
  - Or launch straight into the interactive **Aurora Bash** shell.

---

## Running from Source

If you prefer to run or modify the code directly:

### Requirements
- Python 3.8+
- Pure Python standard library (no `pip install` required).

### Setup

```bash
git clone https://github.com/moksh033/Aurora.git
cd Aurora
```

#### Linux / macOS:
```bash
chmod +x aurora
./aurora --help
```
*(Optional: move to system PATH)*:
```bash
sudo cp aurora /usr/local/bin/aurora
```

#### Windows:
Invoke the included batch runner or Python script:
```cmd
aurora.cmd --help
```
or
```bash
python main.py
```
*(Running without arguments starts Aurora Bash)*

---

## Command Reference

| Command | Description | Example |
|---|---|---|
| `init` | Initialize a new repository (`.aurora/`) | `aurora init` |
| `add` | Stage files or entire folders | `aurora add <path>` |
| `commit` | Save staged snapshot with message | `aurora commit -m "Initial commit"` |
| `status` | Check modified, staged, or untracked changes | `aurora status` |
| `log` | Browse commit logs | `aurora log` |
| `branch` | List branches, create new, or delete (`-d`) | `aurora branch feature-branch` |
| `checkout` | Switch branches or create and checkout (`-b`) | `aurora checkout -b feature-branch` |

---

## Interactive Aurora Bash Commands

When you launch `aurora.exe` directly or run `python main.py` with no arguments, Aurora opens an interactive prompt:

```text
aurora-user@local C:\Your\Project
$ init
$ add .
$ commit -m "My first commit"
```

Common built-in shell commands like `ls`, `cd <dir>`, `pwd`, `clear`, and `exit` are also built right in.

---

## License

This project is licensed under the MIT License.
