# Aurora

A lightweight, from-scratch version control system written in Python, inspired by Git internals.

Aurora implements core content-addressable storage concepts — including SHA-1 hashed blobs, trees, commits, a staging area (index), and branch management — with zero external dependencies.

---

## Features

- **Object Store**: Blob, Tree, and Commit storage compressed with `zlib` and indexed by SHA-1.
- **Staging Area**: An `index` tracking staged files and directory trees.
- **Branching & Checkout**: Create, switch, list, and delete branches.
- **Commit History**: View commit logs with parent tracking and timestamps.
- **Status & Diffs**: Inspect working tree and staging changes.

---

## Installation & Setup

### Requirements
- Python 3.8+
- No external packages or `pip install` required (uses Python standard library).

### Quick Start

Clone the repository:
```bash
git clone https://github.com/moksh033/Aurora.git
cd Aurora
```

#### Run on Linux / macOS / Git Bash:
Make the wrapper executable:
```bash
chmod +x aurora
./aurora --help
```
*(Optional)* Add Aurora to your PATH or copy to `/usr/local/bin`:
```bash
sudo cp aurora /usr/local/bin/aurora
```

#### Run on Windows:
You can invoke `aurora.cmd` directly from Command Prompt or PowerShell:
```cmd
aurora.cmd --help
```
Or run directly with Python:
```bash
python main.py --help
```

---

## Command Reference

| Command | Description | Example |
|---|---|---|
| `init` | Initialize a new Aurora repository (`.aurora/`) | `aurora init` |
| `add` | Stage files or directories | `aurora add <file_or_dir>` |
| `commit` | Record changes to the repository | `aurora commit -m "Your message"` |
| `status` | Show repository working directory and staging status | `aurora status` |
| `log` | View commit history | `aurora log` |
| `branch` | List branches, create (`-b`), or delete (`-d`) | `aurora branch feature` |
| `checkout` | Switch branches or create and switch (`-b`) | `aurora checkout -b new-branch` |

---

## License
MIT License
