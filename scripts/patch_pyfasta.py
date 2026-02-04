import io
import os
import sys
from pathlib import Path


def patch_pyfasta():
    try:
        import pyfasta
    except Exception as exc:
        print(f"pyfasta import failed: {exc}")
        return 1

    records_path = Path(pyfasta.__file__).resolve().parent / "records.py"
    if not records_path.exists():
        print(f"records.py not found: {records_path}")
        return 1

    text = records_path.read_text()
    original = text

    if "sys.maxint" in text:
        text = text.replace("sys.maxint", "sys.maxsize")

    if "long" in text and "long = int" not in text:
        lines = text.splitlines()
        insert_at = 0
        for i, line in enumerate(lines):
            if line.startswith("import ") or line.startswith("from "):
                insert_at = i + 1
        lines.insert(insert_at, "long = int")
        text = "\n".join(lines) + ("\n" if text.endswith("\n") else "")

    if text != original:
        records_path.write_text(text)
        print(f"patched: {records_path}")
    else:
        print(f"no changes: {records_path}")

    return 0


if __name__ == "__main__":
    sys.exit(patch_pyfasta())
