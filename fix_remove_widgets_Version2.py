#!/usr/bin/env python3
"""
fix_remove_widgets.py

Usage:
  python fix_remove_widgets.py path/to/notebook1.ipynb [path/to/notebook2.ipynb ...]

This script:
- Creates a .bak backup for each notebook (same folder, filename + ".bak").
- Removes any 'widgets' key anywhere in the notebook JSON (cell metadata, top-level metadata, nested places).
- Preserves all other notebook content (cells, outputs, execution counts, other metadata).
"""
import sys
from pathlib import Path
import shutil
import nbformat
import json
from typing import Any

def remove_widgets_recursive(obj: Any) -> bool:
    """
    Recursively remove keys named 'widgets' from dict-like objects anywhere
    in the structure. Returns True if any removal happened.
    """
    changed = False
    if isinstance(obj, dict):
        # iterate over a list of keys to allow mutation
        for key in list(obj.keys()):
            if key == "widgets":
                del obj[key]
                changed = True
                continue
            val = obj.get(key)
            if isinstance(val, (dict, list)):
                if remove_widgets_recursive(val):
                    changed = True
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, (dict, list)):
                if remove_widgets_recursive(item):
                    changed = True
    return changed

def remove_widgets_from_notebook(path: Path) -> bool:
    if not path.exists():
        print(f"[SKIP] Not found: {path}")
        return False

    # Backup
    bak = path.with_suffix(path.suffix + ".bak")
    shutil.copy2(path, bak)
    print(f"[BACKUP] {path} -> {bak}")

    changed = False
    nb = None

    # Try reading with nbformat first (preserves NotebookNode structure)
    try:
        nb = nbformat.read(str(path), as_version=nbformat.NO_CONVERT)
        # operate on NotebookNode (dict-like)
        if remove_widgets_recursive(nb):
            changed = True
    except Exception as e:
        # Fallback: load raw JSON to handle severely invalid notebooks
        print(f"[WARN] nbformat.read failed ({e}), falling back to raw JSON processing")
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            if remove_widgets_recursive(raw):
                changed = True
            nb = raw
        except Exception as e2:
            print(f"[ERROR] Failed to load notebook JSON: {e2}")
            return False

    if changed:
        # Try writing with nbformat first to preserve format; fallback to json.dump if it errors
        try:
            nbformat.write(nb, str(path))
            print(f"[PATCHED] {path} (removed 'widgets' keys)")
        except Exception as e:
            print(f"[WARN] nbformat.write failed ({e}), writing raw JSON as fallback")
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(nb, f, ensure_ascii=False, indent=1)
                print(f"[PATCHED] {path} (written raw JSON)")
            except Exception as e2:
                print(f"[ERROR] Failed to write patched notebook: {e2}")
                return False
    else:
        print(f"[NO CHANGE] {path} (no 'widgets' keys found)")

    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_remove_widgets.py notebook1.ipynb [notebook2.ipynb ...]")
        sys.exit(1)
    for p in sys.argv[1:]:
        remove_widgets_from_notebook(Path(p))

if __name__ == '__main__':
    main()