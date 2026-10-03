"""
Execute a shakemap-urls notebook end-to-end and scan its outputs for problems.
This mirrors the manual checks used repeatedly while building the skill:
error cells, and any "Warning"/"WARNING" text in stream output — both
dissolve_multipolygon (MultiPolygon leftover) and to_osh_url (URL over
MAX_URL_LENGTH) print a WARNING on failure, so a clean scan of stream text
covers both failure modes without needing separate length-parsing logic.

Usage: python3 verify_notebook.py <path/to/notebook.ipynb>
Exits 0 and prints "CLEAN" if nothing was found, else prints each problem and
exits 1.
"""
import json
import subprocess
import sys


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 verify_notebook.py <path/to/notebook.ipynb>")
        sys.exit(2)

    path = sys.argv[1]
    result = subprocess.run(
        ["jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace", path],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print("EXECUTION FAILED:")
        print(result.stderr[-4000:])
        sys.exit(1)

    with open(path) as f:
        nb = json.load(f)

    problems = []
    for i, cell in enumerate(nb["cells"]):
        if cell.get("cell_type") != "code":
            continue
        for out in cell.get("outputs", []):
            if out.get("output_type") == "error":
                problems.append(f"cell {i}: ERROR {out.get('ename')}: {out.get('evalue')}")
            elif out.get("output_type") == "stream":
                text = "".join(out.get("text", []))
                if "warning" in text.lower():
                    snippet = next((line for line in text.splitlines() if "warning" in line.lower()), text[:200])
                    problems.append(f"cell {i}: {snippet}")

    if problems:
        print("NOT CLEAN:")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)

    print("CLEAN")
    sys.exit(0)


if __name__ == "__main__":
    main()
