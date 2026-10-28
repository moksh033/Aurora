from __future__ import annotations
from typing import Optional
from re import sub
from os import path
import hashlib
import argparse
from pathlib import Path
import sys
import json
import zlib
import time
from typing import Dict
from typing import List
from typing import Tuple

# make sure to keep future import on top


# main git object thtll act as the parent
class GitObject:
    def __init__(self, obj_type: str, content: bytes):
        self.type = obj_type
        self.content = content

    def hash(self) -> str:
        header = f"{self.type} {len(self.content)}\0".encode()
        return hashlib.sha1(header + self.content).hexdigest()

    def serialize(self) -> bytes:
        header = f"{self.type} {len(self.content)}\0".encode()
        return zlib.compress(header + self.content)

    @classmethod
    def deserialize(cls, data: bytes) -> GitObject:
        decompressed = zlib.decompress(data)
        null_idx = decompressed.find(b"\0")
        header = decompressed[:null_idx].decode()
        content = decompressed[null_idx + 1 :]

        obj_type = header.split(" ")[0]
        return cls(obj_type, content)


# blob object class


class Blob(GitObject):
    def __init__(self, content: bytes):
        super().__init__("blob", content)

    def get_content(self) -> bytes:
        return self.content


# tree object class
class Tree(GitObject):
    def __init__(self, entries: list[Tuple[str, str, str]] = None):
        self.entries = entries or []
        content = self._serialize_entries()
        super().__init__("tree", content)

    def _serialize_entries(self) -> bytes:
        content = b""

        for mode, name, obj_hash in sorted(self.entries):
            content += f"{mode} {name}\0".encode()
            content += bytes.fromhex(obj_hash)

        return content

    def add_entry(self, mode: str, name: str, obj_hash: str):
        self.entries.append((mode, name, obj_hash))
        self.content = self._serialize_entries()

    @classmethod
    def from_content(cls, content: bytes):
        tree = cls()
        i = 0

        while i < len(content):
            null_idx = content.find(b"\0", i)
            if null_idx == -1:
                break

            mode_name = content[i:null_idx].decode()
            mode, name = mode_name.split(" ", 1)

            obj_hash = content[null_idx + 1 : null_idx + 21].hex()
            tree.entries.append((mode, name, obj_hash))

            i = null_idx + 21

        return tree


# commit object class
class Commit(GitObject):
    def __init__(
        self,
        tree_hash: str,
        parent_hashes: List[str],
        author: str,
        committer: str,
        message: str,
        timestamp: int = None,
    ):
        self.tree_hash = tree_hash
        self.parent_hashes = parent_hashes
        self.author = author
        self.committer = committer
        self.message = message
        self.timestamp = timestamp or int(time.time())

        content = self.serialize_commit()
        super().__init__("commit", content)

    def serialize_commit(self):
        lines = [f"tree {self.tree_hash}"]

        for parent in self.parent_hashes:
            lines.append(f"parent {parent}")

        lines.append(f"author {self.author} {self.timestamp} +0000")
        lines.append(f"committer {self.committer} {self.timestamp} +0000")
        lines.append("")
        lines.append(self.message)

        return "\n".join(lines).encode()

    @classmethod
    def from_content(cls, content: bytes) -> Commit:
        lines = content.decode().split("\n")

        tree_hash = None
        parent_hashes = []
        author = None
        committer = None
        message_start = 0

        for i, line in enumerate(lines):
            if line.startswith("tree "):
                tree_hash = line[5:]
            elif line.startswith("parent "):
                parent_hashes.append(line[7:])
            elif line.startswith("author "):
                author_parts = line[7:].rsplit(" ", 2)
                author = author_parts[0]
                timestamp = (
                    int(author_parts[1])
                    if author_parts[1].isdigit()
                    else int(time.time())
                )
            elif line.startswith("committer "):
                committer_parts = line[10:].rsplit(" ", 2)
                committer = committer_parts[0]
            elif line == "":
                message_start = i + 1
                break

        message = "\n".join(lines[message_start:])

        commit = cls(tree_hash, parent_hashes, author, committer, message, timestamp)

        return commit


# repo class
class Repository:
    def __init__(self, path="."):
        self.path = Path(path).resolve()
        self.git_dir = self.path / ".aurora"

        # aurora objects
        self.objects_dir = self.git_dir / "objects"
        # aurora refs
        self.refs_dir = self.git_dir / "refs"
        self.heads_dir = self.refs_dir / "heads"
        #  aurora HEAD file
        self.head_file = self.git_dir / "HEAD"
        # aurora index
        self.index_file = self.git_dir / "index"

    def init(self) -> bool:
        # Check if already made
        if self.git_dir.exists():
            return False

        # making folders
        self.git_dir.mkdir()
        self.objects_dir.mkdir()
        self.refs_dir.mkdir()
        self.heads_dir.mkdir()

        # making initial HEAD pointing to a branch
        self.head_file.write_text("ref: refs/heads/master\n")

        self.save_index({})

        self.index_file.write_text(json.dumps({}, indent=2))

        print(f"Initialized empty aurora repository in {self.git_dir}")
        return True

    def store_object(self, obj: GitObject):
        obj_hash = obj.hash()
        obj_dir = self.objects_dir / obj_hash[:2]
        obj_file = obj_dir / obj_hash[2:]
        if not obj_file.exists():
            obj_dir.mkdir(exist_ok=True)
            obj_file.write_bytes(obj.serialize())
        return obj_hash

    def load_index(self) -> Dict[str, str]:
        if not self.index_file.exists():
            return {}
        try:
            return json.loads(self.index_file.read_text())
        except:
            return {}

    def save_index(self, index: Dict[str, str]):
        self.index_file.write_text(json.dumps(index, indent=2))

    def add_file(self, path: str):
        full_path = self.path / path
        if not full_path.exists():
            raise FileNotFoundError(f"Path {path} not found")
        if any(part.lower() in [".aurora", ".git"] for part in full_path.parts):
            return
        # Reading the file content
        content = full_path.read_bytes()
        # Making a BLOB object
        blob = Blob(content)
        # storing blob object in .aurora/objects
        blob_hash = self.store_object(blob)
        # updating index to add the file
        index = self.load_index()
        rel_path = str(full_path.relative_to(self.path)).replace("\\", "/")
        index[rel_path] = blob_hash
        self.save_index(index)

        print(f"Added {rel_path}")

    def add_directory(self, path: str):
        full_path = self.path / path

        if not full_path.exists():
            raise FileNotFoundError(f"Directory {path} not found")

        if not full_path.is_dir():
            raise ValueError(f"{path} is not a directory")
        index = self.load_index()
        added_count = 0

        # goes over all files in dir using rglob
        for file_path in full_path.rglob("*"):
            if file_path.is_file():
                if any(part.lower() in [".aurora", ".git"] for part in file_path.parts):
                    continue
                # creating blob obj
                content = file_path.read_bytes()
                blob = Blob(content)
                blob_hash = self.store_object(blob)
                # updating index
                rel_path = str(file_path.relative_to(self.path)).replace("\\", "/")
                index[rel_path] = blob_hash
                added_count += 1
                print(f"Added {rel_path}")
        self.save_index(index)
        if added_count > 0:
            print(f"Added {added_count} files from directory {path}")
        else:
            print(f"Directory {path} already up to date")

    def add_path(self, path: str) -> None:
        full_path = self.path / path

        if not full_path.exists():
            raise FileNotFoundError(f"Path {path} not found")

        if full_path.is_file():
            self.add_file(path)
        elif full_path.is_dir():
            self.add_directory(path)
        else:
            raise ValueError(f"{path} is neither a file nor a directory")

    def load_object(self, obj_hash: str) -> GitObject:
        obj_dir = self.objects_dir / obj_hash[:2]
        obj_file = obj_dir / obj_hash[2:]
        if not obj_file.exists():
            raise FileNotFoundError(f"Object {obj_hash} not found")
        return GitObject.deserialize(obj_file.read_bytes())

    def create_tree_from_index(self):
        index = self.load_index()
        if not index:
            tree = Tree()
            return self.store_object(tree)
        dirs = {}
        files = {}

        for file_path, blob_hash in index.items():
            parts = Path(file_path).parts

            if len(parts) == 1:
                files[parts[0]] = blob_hash
            else:
                dir_name = parts[0]
                if dir_name not in dirs:
                    dirs[dir_name] = {}

                current = dirs[dir_name]
                for part in parts[1:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = blob_hash

        def create_tree_recursive(entries_dict: Dict):
            tree = Tree()
            for name, blob_hash in entries_dict.items():
                if isinstance(blob_hash, str):
                    tree.add_entry("100644", name, blob_hash)
                if isinstance(blob_hash, dict):
                    subtree_hash = create_tree_recursive(blob_hash)
                    tree.add_entry("40000", name, subtree_hash)
            return self.store_object(tree)

        root_entries = {**files}
        for dir_name, dir_contents in dirs.items():
            root_entries[dir_name] = dir_contents

        return create_tree_recursive(root_entries)

    def get_current_branch(self) -> str:
        if not self.head_file.exists():
            return "master"
        head_content = self.head_file.read_text().strip()
        if head_content.startswith("ref: refs/heads/"):
            return head_content[16:]
        return "HEAD"

    def get_branch_commit(self, current_branch: str):
        branch_file = self.heads_dir / current_branch

        if branch_file.exists():
            return branch_file.read_text().strip()
        return None

    def set_branch_commit(self, current_branch: str, commit_hash: str):
        branch_file = self.heads_dir / current_branch
        branch_file.write_text(commit_hash + "\n")

    def commit(self, message: str, author: str = "Aurora User <user@aurora.com>"):
        tree_hash = self.create_tree_from_index()

        current_branch = self.get_current_branch()
        parent_commit = self.get_branch_commit(current_branch)
        parent_hashes = [parent_commit] if parent_commit else []

        index = self.load_index()
        if not index:
            print("Nothing to commit, working tree is clean")
            return None
        if parent_commit:
            parent_git_commit_obj = self.load_object(parent_commit)
            parent_commit_data = Commit.from_content(parent_git_commit_obj.content)
            if tree_hash == parent_commit_data.tree_hash:
                print("nothing to commit, working tree clean")
                return None

        commit = Commit(
            tree_hash=tree_hash,
            parent_hashes=parent_hashes,
            author=author,
            committer=author,
            message=message,
        )
        commit_hash = self.store_object(commit)
        self.set_branch_commit(current_branch, commit_hash)
        self.save_index({})
        print(f"Created commit {commit_hash} on branch {current_branch}")
        return commit_hash

    def get_files_from_tree_recursive(
        self,
        tree_hash: str,
        prefix: str = "",
    ):
        files = set()
        try:
            tree_obj = self.load_object(tree_hash)
            tree = Tree.from_content(tree_obj.content)

            for mode, name, obj_hash in tree.entries:
                full_name = f"{prefix}{name}"
                if mode.startswith("100"):
                    files.add(full_name)
                elif mode.startswith("400"):
                    subtree_files = self.get_files_from_tree_recursive(
                        obj_hash, f"{full_name}/"
                    )
                    files.update(subtree_files)

        except Exception as e:
            print(f"Warning: Could not read tree {tree_hash}: {e}")

        return files

    # logic for checkout command
    def checkout(self, branch: str, create_branch: bool):
        previous_branch = self.get_current_branch()
        previous_commit_hash = self.get_branch_commit(previous_branch)

        branch_file = self.heads_dir / branch

        if not branch_file.exists():
            if not create_branch:
                print(f"Branch '{branch}' not found")
                print(
                    f"Use 'python3 main.py checkout -b {branch}' "
                    "to create and switch to a new branch"
                )
                return

            branch_file.parent.mkdir(parents=True, exist_ok=True)
            branch_file.write_text(
                (previous_commit_hash + "\n") if previous_commit_hash else ""
            )
            print(f"Created a new branch {branch}")

        elif create_branch:
            print(f"Branch '{branch}' already exists")
            return

        self.head_file.write_text(f"ref: refs/heads/{branch}\n")
        print(f"Switched to branch '{branch}'")

        target_commit_hash = self.get_branch_commit(branch)

        if previous_commit_hash == target_commit_hash:
            return

        old_files = set()
        if previous_commit_hash:
            try:
                prev_commit_object = self.load_object(previous_commit_hash)
                prev_commit = Commit.from_content(prev_commit_object.content)
                if prev_commit.tree_hash:
                    old_files = self.get_files_from_tree_recursive(
                        prev_commit.tree_hash
                    )
            except Exception as e:
                print(f"Warning: Could not read previous commit: {e}")

        new_files = set()
        if target_commit_hash:
            try:
                target_commit_object = self.load_object(target_commit_hash)
                target_commit = Commit.from_content(target_commit_object.content)
                if target_commit.tree_hash:
                    new_files = self.get_files_from_tree_recursive(
                        target_commit.tree_hash
                    )
            except Exception as e:
                print(f"Warning: Could not read target commit: {e}")

        files_to_clear = old_files - new_files
        files_to_clear = {
            f
            for f in files_to_clear
            if not any(part.lower() in [".aurora", ".git"] for part in Path(f).parts)
        }

        self.restore_working_directory(branch, files_to_clear)

    def restore_tree(self, tree_hash: str, base_path: Path):
        try:
            tree_obj = self.load_object(tree_hash)
        except FileNotFoundError:
            print(f"Warning: Tree object {tree_hash} not found")
            return

        tree = Tree.from_content(tree_obj.content)

        for mode, name, obj_hash in tree.entries:
            if any(part.lower() in [".aurora", ".git"] for part in Path(name).parts):
                continue

            file_path = base_path / name

            if mode.startswith("100"):
                try:
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    blob_obj = self.load_object(obj_hash)
                    file_path.write_bytes(blob_obj.content)
                except FileNotFoundError:
                    print(f"Warning: Blob object {obj_hash} for {name} not found")
            elif mode.startswith("400"):
                file_path.mkdir(parents=True, exist_ok=True)
                self.restore_tree(obj_hash, file_path)

    def restore_working_directory(
        self,
        branch: str,
        files_to_clear: set[str],
    ):
        target_commit_hash = self.get_branch_commit(branch)

        for rel_path in sorted(files_to_clear):
            if any(
                part.lower() in [".aurora", ".git"] for part in Path(rel_path).parts
            ):
                continue
            file_path = self.path / rel_path
            try:
                if file_path.is_file():
                    file_path.unlink()
            except OSError:
                pass

        if not target_commit_hash:
            self.save_index({})
            return

        try:
            target_commit_obj = self.load_object(target_commit_hash)
        except FileNotFoundError:
            print("Branch commit object not found")
            return

        target_commit = Commit.from_content(target_commit_obj.content)

        if target_commit.tree_hash:
            self.restore_tree(target_commit.tree_hash, self.path)

        self.save_index({})

    def branch(self, branch_name: str, delete: bool = False):
        if delete and branch_name:
            branch_file = self.heads_dir / branch_name
            if branch_file.exists():
                branch_file.unlink()
                print(f"Deleted branch {branch_name}")
            else:
                print(f"Branch {branch_name} not found")
            return
        current_branch = self.get_current_branch()
        if branch_name:
            current_commit = self.get_branch_commit(current_branch)
            if current_commit:
                self.set_branch_commit(branch_name, current_commit)
                print(f"Created branch {branch_name}")
            else:
                print("No commits yet, cannot create a new branch")
        else:
            branches = []
            for branch_file in self.heads_dir.iterdir():
                if branch_file.is_file() and not branch_file.name.startswith("."):
                    branches.append(branch_file.name)

            print("Branches:")
            for branch in sorted(branches):
                current__marker = "* " if branch == current_branch else "  "
                print(f"{current__marker}{branch}")

    def log(self, max_count: int = 10):
        current_branch = self.get_current_branch()
        commit_hash = self.get_branch_commit(current_branch)

        if not commit_hash:
            print("No commits yet!")
            return

        count = 0
        while commit_hash and count < max_count:
            commit_obj = self.load_object(commit_hash)
            commit = Commit.from_content(commit_obj.content)

            print(f"commit {commit_hash}")
            print(f"author:{commit.author}")
            print(f"Date: {time.ctime(commit.timestamp)}")
            print(f"\n    {commit.message}\n")

            commit_hash = commit.parent_hashes[0] if commit.parent_hashes else None
            count += 1

    def build_index_from_tree(self, tree_hash: str, prefix: str = ""):
        index = {}
        try:
            tree_obj = self.load_object(tree_hash)
            tree = Tree.from_content(tree_obj.content)

            for mode, name, obj_hash in tree.entries:
                full_name = f"{prefix}{name}"
                if mode.startswith("100"):
                    index[full_name] = obj_hash
                elif mode.startswith("400"):
                    subindex = self.build_index_from_tree(obj_hash, f"{full_name}/")
                    index.update(subindex)

        except Exception as e:
            print(f"Warning: Could not read tree {tree_hash}: {e}")

        return index

    def get_all_files(self) -> List[Path]:
        files = []

        for item in self.path.rglob("*"):
            if any(part.lower() in [".aurora", ".git"] for part in item.parts):
                continue
            if item.is_file():
                files.append(item)
        return files

    def status(self):
        # current branch
        current_branch = self.get_current_branch()
        print(f"On branch {current_branch}")
        index = self.load_index()
        # latest commit
        current_commit_hash = self.get_branch_commit(current_branch)
        last_index_files = {}
        if current_commit_hash:
            try:
                commit_obj = self.load_object(current_commit_hash)
                commit = Commit.from_content(commit_obj.content)
                if commit.tree_hash:
                    last_index_files = self.build_index_from_tree(commit.tree_hash)
            except:
                last_index_files = {}

        working_files = {}

        for item in self.get_all_files():
            rel_path = str(item.relative_to(self.path)).replace("\\", "/")

            try:
                content = item.read_bytes()
                blob = Blob(content)
                working_files[rel_path] = blob.hash()
            except:
                continue

        staged_files = []
        unstaged_files = []
        untracked_files = []
        deleted_files = []

        # what files are staged forcommit
        for file_path in set(index.keys()) | set(last_index_files.keys()):
            index_hash = index.get(file_path)
            last_index_hash = last_index_files.get(file_path)

            if index_hash and not last_index_hash:
                staged_files.append(("new file", file_path))
            elif index_hash and last_index_hash and index_hash != last_index_hash:
                staged_files.append(("modified", file_path))
        if staged_files:
            print("\nChanges to be commited:")
            for stage_status, file_path in sorted(staged_files):
                print(f"   {stage_status}: {file_path}")

        # file modified but havent been staged
        for file_path in working_files:
            if file_path in index:
                if working_files[file_path] != index[file_path]:
                    unstaged_files.append(file_path)
        if unstaged_files:
            print("Changes not staged for commit: ")
            for file_path in sorted(unstaged_files):
                print(f"   modified: {file_path}")
        # untracked files
        for file_path in working_files:
            if file_path not in index and file_path not in last_index_files:
                untracked_files.append(file_path)

        if untracked_files:
            print("Untracked files:")
            for file_path in sorted(untracked_files):
                print(f"   {file_path}")
        # deleted files
        for file_path in index:
            if file_path not in working_files:
                deleted_files.append(file_path)

        if deleted_files:
            print("Deleted files:")
            for file_path in sorted(deleted_files):
                print(f"   deleted: {file_path}")
        if (
            not staged_files
            and not unstaged_files
            and not untracked_files
            and not deleted_files
        ):
            print("\nnothing to commit, working tree is clean")


def main():
    parser = argparse.ArgumentParser(
        description="Aurora - Version Control System by Moksh!"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init cmd
    init_parser = subparsers.add_parser("init", help="Initialize a new repository")
    # add command
    add_parser = subparsers.add_parser(
        "add", help="Add files and directories to the staging area"
    )
    add_parser.add_argument("paths", nargs="+", help="Files and directories to add")
    # commit command
    commit_parser = subparsers.add_parser("commit", help=" Create a new commit")
    commit_parser.add_argument("-m", "--message", help="Commit message", required=True)
    commit_parser.add_argument("--author", help="Author name and email")
    # checkout command
    checkout_parser = subparsers.add_parser("checkout", help="Move/Create a new branch")
    checkout_parser.add_argument("branch", help="Branch to switch to")
    checkout_parser.add_argument(
        "-b",
        "--create-branch",
        action="store_true",
        help="Create and switch to a new branch",
    )
    # branch command
    branch_parser = subparsers.add_parser("branch", help="List or manage branches")
    branch_parser.add_argument("name", nargs="?")
    branch_parser.add_argument(
        "-b",
        "--create-branch",
        action="store_true",
        help="Create a new branch",
    )
    branch_parser.add_argument(
        "-d",
        "--delete",
        action="store_true",
        help="Delete a branch",
    )
    # log command
    log_parser = subparsers.add_parser("log", help="Show Commit History")
    log_parser.add_argument(
        "-n",
        "--max-count",
        type=int,
        default=10,
        help="limits commit shown",
    )

    # status command
    status_parser = subparsers.add_parser("status", help="Show repository status")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return
    repo = Repository()
    try:
        if args.command == "init":
            if not repo.init():
                print("Repository already exists")
        elif args.command == "add":
            if not repo.git_dir.exists():
                print("Not an aurora repository")
                return
            for path in args.paths:
                repo.add_path(path)
        elif args.command == "commit":
            if not repo.git_dir.exists():
                print("Not an aurora repository")
                return
            author = args.author or "AuroraUser <user@aurora.com>"
            repo.commit(args.message, author)
        elif args.command == "checkout":
            if not repo.git_dir.exists():
                print("Not an aurora repository")
                return
            repo.checkout(args.branch, args.create_branch)
        elif args.command == "branch":
            if not repo.git_dir.exists():
                print("Not an aurora repository")
                return

            repo.branch(args.name, args.delete)
        elif args.command == "log":
            if not repo.git_dir.exists():
                print("Not an aurora repository")
                return
            repo.log(args.max_count)
        elif args.command == "status":
            if not repo.git_dir.exists():
                print("Not an aurora repository")
                return

            repo.status()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


# calling the helper.py file containing all the other stuff ( aurura bash logo and all)
if __name__ == "__main__":
    if len(sys.argv) == 1:
        import helper

        helper.run_aurora_bash()
    else:
        main()
