"""Diagnostic script to identify which polar files are not being processed"""

from pathlib import Path

from polars_reader import parse_polar_file

polars_dir = Path(__file__).parent / "polars"
files = sorted([f for f in polars_dir.glob("*Re0.688*.txt")])

print(f"Total files found: {len(files)}")
print()

empty_or_none = []
errors = []

for f in files:
    try:
        p = parse_polar_file(f)
        df = p["df"]
        name = p["name"]

        if df is None or df.empty:
            empty_or_none.append(f.name)
            print(f"❌ {f.name}")
            print(f"   Name: {name}")
            print(f"   DataFrame: {df is None and 'None' or 'Empty'}")
            print()
    except Exception as e:
        errors.append((f.name, str(e)))
        print(f"💥 ERROR in {f.name}: {e}")
        print()

print("\n" + "=" * 80)
print(f"Successfully parsed: {len(files) - len(empty_or_none) - len(errors)}")
print(f"Empty or None DataFrames: {len(empty_or_none)}")
print(f"Errors: {len(errors)}")

if empty_or_none:
    print("\nFiles with empty/None DataFrames:")
    for fname in empty_or_none:
        print(f"  - {fname}")

if errors:
    print("\nFiles with errors:")
    for fname, err in errors:
        print(f"  - {fname}: {err}")
