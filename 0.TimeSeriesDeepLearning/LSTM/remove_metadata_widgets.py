import json
import shutil
import sys
from pathlib import Path
import nbformat

def remove_widgets_recursive(obj):
    # work on plain dict-like NotebookNode as well
    if isinstance(obj, dict):
        # pop any direct 'widgets' key safely
        if "widgets" in obj:
            obj.pop("widgets", None)
        # iterate over a static list of keys to avoid mutation-during-iteration issues
        for k in list(obj.keys()):
            remove_widgets_recursive(obj[k])
    elif isinstance(obj, list):
        for item in obj:
            remove_widgets_recursive(item)

def main(nb_path):
    nb_path = Path(nb_path)
    if not nb_path.exists():
        print(f"Not found: {nb_path}")
        return
    backup = nb_path.with_suffix(nb_path.suffix + ".bak")
    shutil.copy2(nb_path, backup)
    nb = nbformat.read(str(nb_path), as_version=nbformat.NO_CONVERT)
    # remove top-level metadata.widgets if present
    if "metadata" in nb and isinstance(nb["metadata"], dict) and "widgets" in nb["metadata"]:
        nb["metadata"].pop("widgets", None)
    # traverse entire notebook structure
    remove_widgets_recursive(nb)
    nbformat.write(nb, str(nb_path))
    print(f"Done. Backup: {backup}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 remove_metadata_widgets.py <notebook.ipynb>")
        sys.exit(1)
    main(sys.argv[1])