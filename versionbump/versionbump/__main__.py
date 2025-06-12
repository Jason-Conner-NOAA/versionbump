#!/usr/bin/env python3
import sys
import re
import toml
from pathlib import Path

def find_version_file():
    for path in Path(".").rglob("_version.py"):
        return path
    return None

def write_version_file(version_path, new_version):
    with open(version_path, "w") as f:
        f.write(f'__version__ = "{new_version}"\n')

def read_version_from_toml(pyproject):
    data = toml.load(pyproject)
    return data["project"]["version"]

def write_version_to_toml(pyproject, new_version):
    data = toml.load(pyproject)
    data["project"]["version"] = new_version
    with open(pyproject, "w") as f:
        toml.dump(data, f)

def bump_version(version, level="patch"):
    base = version.split("-")[0]
    major, minor, patch = map(int, base.split("."))
    if level == "major":
        major += 1
        minor = 0
        patch = 0
    elif level == "minor":
        minor += 1
        patch = 0
    else:
        patch += 1
    return f"{major}.{minor}.{patch}"

def bump_prerelease(version):
    match = re.match(r"^(\d+\.\d+\.\d+)(?:-dev\.(\d+))?$", version)
    if not match:
        print(f"❌ Invalid format for prerelease bump: {version}")
        sys.exit(1)
    base, dev = match.groups()
    next_dev = int(dev) + 1 if dev is not None else 0
    return f"{base}-dev.{next_dev}"

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Bump or initialize project version")
    parser.add_argument("level", nargs="?", choices=["patch", "minor", "major"],
                        help="Bump level (default: patch)")
    parser.add_argument("--prerelease", action="store_true",
                        help="Increment prerelease tag (e.g., -dev.0 → -dev.1)")
    parser.add_argument("--init", metavar="X.Y.Z", help="Initialize versioning to provided version")

    args = parser.parse_args()

    conflicting_args = [arg for arg, value in [("level", args.level), ("prerelease", args.prerelease), ("init", args.init)] if value]
    if len(conflicting_args) > 1:
        print(f"❌ Conflicting arguments: {', '.join(conflicting_args)}. Choose only one of: bump level, --prerelease, or --init")
        sys.exit(1)

    pyproject = Path("pyproject.toml")
    if not pyproject.exists():
        print("ℹ️ pyproject.toml not found. Creating a default pyproject.toml...")
        default_toml_content = {
            "project": {
                "version": "0.1.0"
            }
        }
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
    else:
        old_version = read_version_from_toml(pyproject)
        if args.prerelease:
            if not re.match(r"^\d+\.\d+\.\d+(-dev\.\d+)?$", old_version):
                print(f"❌ Invalid version format in pyproject.toml: {old_version}")
                sys.exit(1)
            new_version = bump_prerelease(old_version)
        else:
            level = args.level or "patch"
            new_version = bump_version(old_version, level)

        print(f"Current version: {old_version}")
        print(f"New version:     {new_version}")
        confirm = input("Apply version bump? [y/N]: ").strip().lower()
        if confirm != "y":
            print("Aborted.")
            return

    try:
        write_version_to_toml(pyproject, new_version)
        write_version_file(version_file, new_version)
        print(f"✅ Version set to {new_version}. Updated files: {pyproject}, {version_file}")
    except Exception as e:
        print(f"❌ Failed to update version: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
