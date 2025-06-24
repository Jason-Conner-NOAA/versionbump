#!/usr/bin/env python3
import sys
import argparse
from . import (
    find_version_file,
    write_version_file,
    read_version_from_toml,
    write_version_to_toml,
    bump_version_logic,
    bump_prerelease,
)
from pathlib import Path
import re

def main():
    parser = argparse.ArgumentParser(description="Bump or initialize project version")
    parser.add_argument("level", nargs="?", choices=["patch", "minor", "major"],
                        help="Bump level (default: patch)")
    parser.add_argument("--prerelease", action="store_true",
                        help="Increment prerelease tag (e.g., -dev.0 → -dev.1)")
    parser.add_argument("--init", metavar="X.Y.Z", help="Initialize versioning to provided version")

    args = parser.parse_args()

    # Argument conflict logic: only one of the three options can be set
    set_args = [bool(args.level), args.prerelease, bool(args.init)]
    if sum(set_args) > 1:
        print("❌ Conflicting arguments: choose only one of bump level, --prerelease, or --init")
        sys.exit(1)

    pyproject = Path("pyproject.toml")
    if not pyproject.exists():
        import toml
        default_toml_content = {"project": {"version": "0.1.0"}}
        with open(pyproject, "w") as f:
            toml.dump(default_toml_content, f)
        print("✅ Default pyproject.toml created with version 0.1.0.")

    version_file = find_version_file()
    if not version_file:
        version_file = Path("_version.py")
        print(f"ℹ️ Creating version file at {version_file}")

    if args.init:
        new_version = args.init
        if not re.match(r"^\d+\.\d+\.\d+(-dev\.\d+)?$", new_version):
            print("❌ Invalid version format for --init (expected X.Y.Z or X.Y.Z-dev.N)")
            sys.exit(1)
        print(f"Initializing version: {new_version}")
        old_version = None
    else:
        old_version = read_version_from_toml(pyproject)
        if args.prerelease:
            if not re.match(r"^\d+\.\d+\.\d+(-dev\.\d+)?$", old_version):
                print(f"❌ Invalid version format in pyproject.toml: {old_version}")
                sys.exit(1)
            try:
                new_version = bump_prerelease(old_version)
            except ValueError as e:
                print(f"❌ {e}")
                sys.exit(1)
        else:
            level = args.level or "patch"
            new_version = bump_version_logic(old_version, level)

        print(f"Current version: {old_version}")
        print(f"New version:     {new_version}")
        confirm = input("Apply version bump? [y/N]: ").strip().lower()
        if confirm != "y":
            print("Aborted.")
            sys.exit(0)

    try:
        write_version_to_toml(pyproject, new_version)
        write_version_file(version_file, new_version)
        print(f"✅ Version set to {new_version}. Updated files: {pyproject}, {version_file}")
    except Exception as e:
        print(f"❌ Failed to update version: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
