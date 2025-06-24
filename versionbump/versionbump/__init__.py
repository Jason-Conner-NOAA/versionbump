import os
import pathlib
import sys
import re
import toml
from pathlib import Path

# Version loading for __version__
def _load_version():
    root = pathlib.Path(__file__).resolve().parent.parent
    version_file = root / "_version.py"
    ns = {}
    with open(version_file) as f:
        exec(f.read(), ns)
    return ns["__version__"]

__version__ = _load_version()

# --- Version bumping logic (moved from __main__.py) ---
def find_version_file():
    for path in Path(".").rglob("_version.py"):
        return path
    return None

def write_version_file(version_path, new_version):
    # Always write the version as a string, not a tuple or with parentheses
    with open(version_path, "w") as f:
        f.write(f'__version__ = "{new_version}"\n')

def read_version_from_toml(pyproject):
    data = toml.load(pyproject)
    version = data["project"]["version"]
    # If version is a list, use the last entry (assume most recent)
    if isinstance(version, list):
        version = version[-1]
    return version

def write_version_to_toml(pyproject, new_version):
    data = toml.load(pyproject)
    # Always write version as a string, not a list
    data["project"]["version"] = str(new_version)
    with open(pyproject, "w") as f:
        toml.dump(data, f)

def bump_version_logic(version, level="patch"):
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
        raise ValueError(f"Invalid format for prerelease bump: {version}")
    base, dev = match.groups()
    next_dev = int(dev) + 1 if dev is not None else 0
    return f"{base}-dev.{next_dev}"

def bump_version_cli(level=None, prerelease=False, init=None, pyproject_path="pyproject.toml", version_file_path=None):
    """
    Perform the same version bump/init logic as the CLI, but programmatically and without user interaction.
    Returns a tuple: (old_version, new_version)
    """
    pyproject = Path(pyproject_path)
    if not pyproject.exists():
        import toml
        default_toml_content = {"project": {"version": "0.1.0"}}
        with open(pyproject, "w") as f:
            toml.dump(default_toml_content, f)
        old_version = "0.1.0"
    else:
        old_version = read_version_from_toml(pyproject)

    version_file = version_file_path or find_version_file() or Path("_version.py")

    if init is not None:
        new_version = init
        if not re.match(r"^\d+\.\d+\.\d+(-dev\.\d+)?$", new_version):
            raise ValueError("Invalid version format for --init (expected X.Y.Z or X.Y.Z-dev.N)")
    elif prerelease:
        if not isinstance(old_version, str):
            old_version = str(old_version)
        if not re.match(r"^\d+\.\d+\.\d+(-dev\.\d+)?$", old_version):
            raise ValueError(f"Invalid version format in pyproject.toml: {old_version}")
        new_version = bump_prerelease(old_version)
    else:
        bump_level = level or "patch"
        if not isinstance(old_version, str):
            old_version = str(old_version)
        if not re.match(r"^\d+\.\d+\.\d+(-dev\.\d+)?$", old_version):
            raise ValueError(f"Invalid version format in pyproject.toml: {old_version}")
        new_version = bump_version_logic(old_version, bump_level)

    write_version_to_toml(pyproject, new_version)
    write_version_file(version_file, new_version)
    return old_version, new_version