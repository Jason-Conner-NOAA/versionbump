import os
import pathlib

def _load_version():
    root = pathlib.Path(__file__).resolve().parent.parent
    version_file = root / "_version.py"
    ns = {}
    with open(version_file) as f:
        exec(f.read(), ns)
    return ns["__version__"]

__version__ = _load_version()