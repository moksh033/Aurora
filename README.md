# Aurora 

Lightweight, from scratch Python clone of [Git](https://git-scm.com/)'s architecture and internals.

Aurora is primarily a proof of concept program built from scratch to learn how Git works at it's most core (content addressed storage, SHA-1 hashed blobs, trees, commits, completely isolated Staging Index and HEAD branch pointers) without ANY outside dependencies whatsoever.


--- 

Download Aurora Bash (Windows Standalone) 

There's no need to download Python or any sort of development software or environment to run Aurora.

We've provided a standalone build with interactive shell **Aurora Bash**:

1. Open [Latest GitHub Releases](https://github.com/moksh033/Aurora/releases/latest) 
2. Download `aurora.exe` or `aurora-windows-x64-v1.0.zip`. 
3. Double click on `aurora.exe` to launch Aurora Bash into it's own custom terminal window with special branding.
4. *(Optional)* Add `aurora.exe` to your Windows PATH if you want to use aurora <command> globally from PowerShell, CMD or any other terminal program.

--- 

## What Aurora Does 

- Store objects (.aurora/objects) compressed files (blobs), directories (trees) and checkpoints (commits) using zlib and indexed by SHA-1 hash.
- Has own standalone staging index (`.aurora/index`) to modify your next commit file-by-file or recursively entire folders at once.
- Persistent commit history & graphs using parent commit hashes and human readable timestamps & messages.
- Maintains pointers to branches (`master`) and head (WHAT YOU'RE WORKING ON) for easy branch management.
- Inspect your working tree for real time status of modified, staged, deleted or untracked files.
- **Interactive Mode:** 
- Operate Aurora as a traditional command line tool. ie. `aurora init` or `aurora commit -m "Something new..."`.
- _Or Enter the interactive Aurora Bash prompt_ 

--- 

## Running Aurora From Source 

Want to run Aurora yourself or make your own modifications?

### Requirements 
- Python 3.8+ 
- No special libraries outside of the **Python Standard Library**

### Installation 

```bash 
git clone https://github.com/moksh033/Aurora.git 
cd Aurora 
``` 

#### Linux / macOS: 
```bash 
chmod +x aurora 
./aurora --help 
``` 
*Make Aurora globally executable (Optional):* 
```bash 
sudo cp aurora /usr/local/bin/aurora 
``` 

#### Windows: 
Run either the bundled batch file or the Python script directly:

```cmd 
aurora. cmd --help 
``` 
```bash 
python main.py 
``` 
*Runs Aurora Bash if no arguments are provided. * 

--- 

## Command Help 

| Command | Description | Example | 
| ------- | ------------------ | ---------------------- | 
| `init` | Create a new repo | `aurora init` | 
| `add` | Stage files/folder | `aurora add <file.ext>`| 
| `commit`| Commit your changes| `aurora commit -m "Message"` |
| `status`| View file status | `aurora status` | 
| `log` | View git logs | `aurora log` | 
| `branch`| Manage branches | `aurora branch <name>` | 
| `checkout` | Switch Branches | `aurora checkout <branch>` | 

--- 

## Aurora Bash Commands 

Launch `aurora.exe` or run `python main.py` with NO arguments to enter Aurora Bash.

```text 
aurora-user@local C:\Your\Project 
$ 
$ init # Initialize a new Repository (.aurora/) 
$ add . # Add files to staging index (.aurora/index) 
$ commit -m "message" # Create a commit (.aurora/objects/*) 
$ 
``` 
Change directory (cd), copy (cp), print working directory (pwd) and other basic built-in shell commands are supported as well.

--- 

## License 

[MIT License](LICENSE) 
