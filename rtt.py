#!/usr/bin/env python3
"""
rtt - Repo to Text CLI

Convert repository code into AI-friendly text format.

Usage:
    rtt <path>                          # All supported files
    rtt <path> .py .swift               # Only specific extensions
    rtt <path> .py .swift -o out.txt    # Export to file
    rtt <path> --tree                   # Show file tree only
"""

import os
import sys
import argparse


SKIP_DIRS = {'.git', '.svn', '.hg', 'node_modules', '__pycache__', '.tox',
             '.eggs', '.mypy_cache', '.pytest_cache', 'venv', '.venv', 'env',
             '.idea', '.vscode', '.DS_Store', 'dist', 'build', '.next'}


def collect_files(root_dir, extensions=None):
    """Walk directory and collect matching files."""
    matched = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith('.')]
        dirnames.sort()

        for f in sorted(filenames):
            if f.startswith('.'):
                continue
            if extensions:
                if not any(f.lower().endswith(ext) for ext in extensions):
                    continue
            matched.append(os.path.join(dirpath, f))
    return matched


def build_tree(root_dir, extensions=None):
    """Build a directory tree string for matched files."""
    lines = [os.path.basename(root_dir) + "/"]
    matched_files = collect_files(root_dir, extensions)
    matched_set = set(matched_files)

    # Collect all directories that contain matched files
    relevant_dirs = set()
    for fp in matched_files:
        parent = os.path.dirname(fp)
        while parent != root_dir and parent.startswith(root_dir):
            relevant_dirs.add(parent)
            parent = os.path.dirname(parent)

    def _walk(current_dir, prefix=""):
        entries = []
        try:
            for name in sorted(os.listdir(current_dir)):
                full = os.path.join(current_dir, name)
                if os.path.isdir(full):
                    if name in SKIP_DIRS or name.startswith('.'):
                        continue
                    if full in relevant_dirs:
                        entries.append((name, full, True))
                elif full in matched_set:
                    entries.append((name, full, False))
        except PermissionError:
            return

        for i, (name, full, is_dir) in enumerate(entries):
            is_last = i == len(entries) - 1
            connector = "└── " if is_last else "├── "
            if is_dir:
                lines.append(f"{prefix}{connector}{name}/")
                extension = "    " if is_last else "│   "
                _walk(full, prefix + extension)
            else:
                lines.append(f"{prefix}{connector}{name}")

    _walk(root_dir)
    return "\n".join(lines)


def merge_files(root_dir, files):
    """Merge file contents into AI-friendly text format."""
    parts = []
    for file_path in files:
        rel_path = os.path.relpath(file_path, root_dir)
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception as e:
            content = f"Error reading file: {e}"

        parts.append(f"// {rel_path}\n\n{content}")

    return ("\n\n" + "-" * 40 + "\n\n").join(parts) + "\n"


def parse_extensions(ext_args):
    """Normalize extension arguments to dotted lowercase form."""
    exts = []
    for e in ext_args:
        e = e.strip().lower()
        if not e.startswith('.'):
            e = '.' + e
        exts.append(e)
    return exts


def main():
    parser = argparse.ArgumentParser(
        prog="rtt",
        description="Repo to Text — convert repository code to AI-friendly text.",
    )
    parser.add_argument("path", help="Path to the project directory")
    parser.add_argument("extensions", nargs="*",
                        help="File extensions to include (e.g. .py .swift .js). All files if omitted.")
    parser.add_argument("-o", "--output", metavar="FILE",
                        help="Write output to a file instead of stdout")
    parser.add_argument("--tree", action="store_true",
                        help="Print the file tree only, without content")
    parser.add_argument("--copy", "-c", action="store_true",
                        help="Copy output to clipboard (macOS/Linux)")

    args = parser.parse_args()

    root_dir = os.path.abspath(args.path)
    if not os.path.isdir(root_dir):
        print(f"rtt: error: '{args.path}' is not a directory", file=sys.stderr)
        sys.exit(1)

    extensions = parse_extensions(args.extensions) if args.extensions else None

    # Tree-only mode
    if args.tree:
        tree = build_tree(root_dir, extensions)
        print(tree)
        return

    files = collect_files(root_dir, extensions)
    if not files:
        print("rtt: no files found matching criteria.", file=sys.stderr)
        sys.exit(1)

    # Build output: tree + merged content
    tree = build_tree(root_dir, extensions)
    merged = merge_files(root_dir, files)
    output = f"{tree}\n\n{'=' * 40}\n\n{merged}"

    # Output destination
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"rtt: written to {args.output} ({len(files)} files)")
    elif args.copy:
        try:
            import subprocess
            proc = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
            proc.communicate(output.encode("utf-8"))
            print(f"rtt: copied to clipboard ({len(files)} files)")
        except FileNotFoundError:
            try:
                proc = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE)
                proc.communicate(output.encode("utf-8"))
                print(f"rtt: copied to clipboard ({len(files)} files)")
            except FileNotFoundError:
                print("rtt: clipboard not available, printing to stdout", file=sys.stderr)
                print(output)
    else:
        print(output)


if __name__ == "__main__":
    main()
