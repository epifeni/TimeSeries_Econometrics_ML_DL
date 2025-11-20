import json
import shutil
import sys
from pathlib import Path

def remove_widgets_in_metadata(obj):
    if isinstance(obj, dict):
        # remove widgets under any metadata dict
        if "metadata" in obj and isinstance(obj["metadata"], dict) and "widgets" in obj["metadata"]:
            del obj["metadata"]["widgets"]
        # also remove any direct "widgets" keys just in case
        if "widgets" in obj:
            del obj["widgets"]
        for v in obj.values():
            remove_widgets_in_metadata(v)
    elif isinstance(obj, list):
        for item in obj:
            remove_widgets_in_metadata(item)

def main(nb_path):
    nb_path = Path(nb_path)
    if not nb_path.exists():
        print(f"Not found: {nb_path}")
        return
    backup = nb_path.with_suffix(nb_path.suffix + ".bak")
    shutil.copy2(nb_path, backup)
    with nb_path.open("r", encoding="utf-8") as f:
        nb = json.load(f)
    remove_widgets_in_metadata(nb)
    with nb_path.open("w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    print(f"Done. Backup saved to: {backup}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 remove_metadata_widgets.py <notebook.ipynb>")
        sys.exit(1)
    main(sys.argv[1])