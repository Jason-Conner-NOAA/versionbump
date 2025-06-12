#!/usr/bin/env python3

import argparse
import os
import re
import sys

VERSION_FILE = "_version.py"
DEFAULT_VERSION = "0.1.0"

def parse_version(ver):
    parts = ver.strip().split(".")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        raise ValueError("Version must be in format X.Y.Z with integers.")
    return list(map(int, parts))

def format_version(parts):
    return ".".join(map(str, parts))

def bump_version(current, part):
    parts = parse_version(current)
    if part == "major":
        parts[0] += 1
        parts[1:] = [0, 0]
    elif part == "minor":
        parts[1] += 1
        parts[2] = 0
    elif part == "patch":
        parts[2] += 1
    return format_version(parts)

def get_current_version(path):
    if not os.path.isfile(path):
        return None
    with open(path, "r") as f:
        content = f.read()
    match = re.search(r'__version__\s*=\s*[\'"]([^\'"]+)[\'"]', content)
    return match.group(1) if match else None

def write_version(path, ver):
    with open(path, "w") as f:
        f.write(f'__version__ = "{ver}"\n')

def main():
    parser = argparse.ArgumentParser(description="Create or bump _version.py in current directory.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--major", action="store_true", help="Bump major version (e.g., 1.0.0)")
    group.add_argument("--minor", action="store_true", help="Bump minor version (e.g., 0.2.0)")
    group.add_argument("--patch", action="store_true", help="Bump patch version (e.g., 0.1.1) [default]")
    parser.add_argument("--init", metavar="VERSION", help="Initial version to use if creating (e.g., 0.2.5)")
    parser.add_argument("--yes", "-y", action="store_true", help="Auto-confirm without prompting")
    parser.add_argument("--path", default=VERSION_FILE, help="Path to _version.py (default: ./_version.py)")
    args = parser.parse_args()

    # Determine bump part
    if args.major:
        part = "major"
    elif args.minor:
        part = "minor"
    else:
        part = "patch"

    # Determine path and version
    path = args.path
    current = get_current_version(path)

    if not current:
        version_to_write = args.init or DEFAULT_VERSION
        try:
            # Validate custom version if provided
            parse_version(version_to_write)
        except ValueError as e:
            print(f"Invalid --init version: {e}")
            sys.exit(1)

        print(f"{path} not found. Will create with version {version_to_write}")
        if args.yes or input(f"Create {path} with version {version_to_write}? [y/N]: ").strip().lower() == "y":
            write_version(path, version_to_write)
            print(f"Created: {path} with version {version_to_write}")
        else:
            print("Aborted.")
        return

    # Bump existing version
    new = bump_version(current, part)
    print(f"Current version: {current}")
    print(f"New version:     {new}")
    if args.yes or input("Apply this change? [y/N]: ").strip().lower() == "y":
        write_version(path, new)
        print(f"Updated {path} to version {new}")
    else:
        print("Aborted.")

if __name__ == "__main__":
    main()
