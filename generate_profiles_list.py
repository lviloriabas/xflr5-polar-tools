"""Generate a text file listing all available profiles and Reynolds numbers in the polars directory."""

import re
from collections import defaultdict
from pathlib import Path

# Get polars directory
polars_dir = Path(__file__).parent / "polars"

# Regular expression to extract Reynolds number from filename
re_pattern = re.compile(r"Re([0-9.]+)")

# Dictionary to store profiles by Reynolds number
profiles_by_re = defaultdict(list)
all_profiles = set()

# Process all .txt files in polars directory
txt_files = sorted(polars_dir.glob("*.txt"))

for file in txt_files:
    # Extract Reynolds number from filename
    match = re_pattern.search(file.name)
    if match:
        re_value = match.group(1)
        # Extract profile name (everything before _T1_Re)
        profile_name = file.name.split("_T1_Re")[0]

        profiles_by_re[re_value].append(profile_name)
        all_profiles.add(profile_name)

# Sort Reynolds numbers
sorted_reynolds = sorted(profiles_by_re.keys(), key=lambda x: float(x))

# Generate output text
output_lines = []
output_lines.append("=" * 80)
output_lines.append("AVAILABLE PROFILES AND REYNOLDS NUMBERS")
output_lines.append("xflr5-polar-tools")
output_lines.append("=" * 80)
output_lines.append("")
output_lines.append(
    "This file lists all airfoil profiles and Reynolds numbers available in the"
)
output_lines.append(
    "'polars' directory. These are polar data files (.txt) calculated by xflr5."
)
output_lines.append("")
output_lines.append(
    "NOTE: Airfoil geometry files (.dat) are NOT included in this package."
)
output_lines.append("      Only pre-calculated polar data is provided.")
output_lines.append("")
output_lines.append("=" * 80)
output_lines.append("")

# Summary
output_lines.append(f"SUMMARY")
output_lines.append("-" * 80)
output_lines.append(f"Total unique profiles: {len(all_profiles)}")
output_lines.append(f"Reynolds numbers available: {len(sorted_reynolds)}")
output_lines.append(f"Total polar files: {len(txt_files)}")
output_lines.append("")
output_lines.append("=" * 80)
output_lines.append("")

# List Reynolds numbers available
output_lines.append("REYNOLDS NUMBERS AVAILABLE")
output_lines.append("-" * 80)
output_lines.append("")
for re_val in sorted_reynolds:
    re_float = float(re_val)
    re_sci = f"{re_float:.3f}e6" if re_float < 1 else f"{re_float / 1e6:.3f}e6"
    num_profiles = len(profiles_by_re[re_val])
    output_lines.append(
        f"  Re {re_val:>5s}  ({re_sci:>10s})  -  {num_profiles:3d} profiles"
    )
output_lines.append("")
output_lines.append("=" * 80)
output_lines.append("")

# List all unique profiles
output_lines.append("ALL AVAILABLE PROFILES (alphabetically)")
output_lines.append("-" * 80)
output_lines.append("")
for i, profile in enumerate(sorted(all_profiles), 1):
    output_lines.append(f"{i:3d}. {profile}")
output_lines.append("")
output_lines.append("=" * 80)
output_lines.append("")

# List profiles by Reynolds number
output_lines.append("PROFILES BY REYNOLDS NUMBER")
output_lines.append("-" * 80)
output_lines.append("")

for re_val in sorted_reynolds:
    re_float = float(re_val)
    re_sci = f"{re_float:.3f}e6" if re_float < 1 else f"{re_float / 1e6:.3f}e6"
    output_lines.append("")
    output_lines.append(f"Reynolds Number: {re_val} ({re_sci})")
    output_lines.append(f"Number of profiles: {len(profiles_by_re[re_val])}")
    output_lines.append("-" * 40)

    for i, profile in enumerate(sorted(profiles_by_re[re_val]), 1):
        output_lines.append(f"  {i:3d}. {profile}")

    output_lines.append("")

output_lines.append("=" * 80)
output_lines.append("END OF FILE")
output_lines.append("=" * 80)

# Write to file
output_file = Path(__file__).parent / "AVAILABLE_PROFILES.txt"
with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))

print(f"✓ Profile list generated successfully!")
print(f"  Output file: {output_file}")
print(f"  Total profiles: {len(all_profiles)}")
print(f"  Reynolds numbers: {len(sorted_reynolds)}")
print(f"  Total files: {len(txt_files)}")
