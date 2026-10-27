# Aurora

A light weight, from scratch VCS (version control system) in Python, modelled on the architecture and internals of Git.

Aurora was built to explore just how Git works at the most fundamental level (content addressed storage, SHA-1 hashed blobs, trees, commits, a completely isolated staging area and branch pointers) from the ground up with absolutely zero external dependencies.

---

Download Aurora Bash (Windows Standalone)

You don't need Python or any development environment installed in order to get started with Aurora.

We provide a pre-built standalone executable with an interactive shell called **Aurora Bash**:

1. Go to the [Latest GitHub Releases](https://github.com/moksh033/Aurora/releases/latest)
2. Download `aurora.exe` or `aurora-windows-x64-v1.0.zip`.
3. Double click aurora.exe to launch Aurora Bash straight into its own dedicated terminal interface with the appropriate branding.
4. (Optional) Add aurora.exe to your Windows PATH if you'd like to invoke aurora <command> from PowerShell, CMD or any other external terminal.

---

## What Aurora Can Do

- Object storage (in .aurora/objects) compresses and stores the file contents (blobs), directories (trees) and history checkpoints (commits) all indexed by their SHA-1 hash using zlib.
- Staging Index (`.aurora/index`): A working staging area in which you can prepare your commits file by file or directory wide.
- Commit history & graphs: parent commit hashes, author timestamps and formatted commit log.
- Branching & HEAD pointers: create, switch and delete branches as required.
- Working tree inspection: real time status of untracked, modified, staged and deleted files.
- **Dual Mode Interface**:
  Run it as a regular command line tool. For example, use `aurora init` or `aurora commit -m "..."`.
  - Or just go straight into the interactive Aurora Bash shell.

---

## Running from Source

If you prefer to run or modify the code directly:

### Requirements
- Python 3.8+
- Pure Python standard library (no pip install required).

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
| `init` | Start a new repository (`.aurora/`) | `aurora init` |
| `add` | Stage files or entire folders | `aurora add <path>` |
| `commit` | Save staged snapshot with message | `aurora commit -m "Initial commit"` |
| `status` | Check modified, staged, or untracked changes | `aurora status` |
| `log` | Browse commit logs | `aurora log` |
| `branch` | List branches, create new, or delete (`-d`) | `aurora branch feature-branch` |
| `checkout` | Switch branches or create and checkout (`-b`) | `aurora checkout -b feature-branch` |

---

## Interactive Aurora Bash Commands

If you just launch aurora.exe or run python main.py with no arguments at all then Aurora will open an interactive prompt:

```text
aurora-user@local C:\Your\Project
$ init
$ add .
$ commit -m "My first commit"
```

The common built-in shell commands (ls, cd <dir>, pwd, clear and exit) are all built in as well.

---

## License

This project is licensed under the MIT License.
