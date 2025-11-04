# Summary

Collection of scripts for XFLR5 polar analysis.

Main files

- `polars_reader.py`: reading and parsing files in `polars/`.
- `plot_polars.py`: generates a figure with 4 subplots (Cl vs alpha, Cm vs alpha, Cd vs Cl, Cl/Cd vs alpha).
- `extract_limits.py`: extracts minimum and maximum limits per column and values near requested alphas.
- `main.py`: CLI that allows executing the functionalities.

## Installation

Create an environment and install dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Basic Usage

### List available Reynolds numbers

```powershell
python main.py --list-re
```

### Plot polars

**Example 1**: Plot all profiles at Re = 0.100

```powershell
python main.py plot --re 0.100 --out polars_plot.png
```

**Example 2**: Plot only specific profiles (NACA and CLARK YS) at Re = 0.100

```powershell
python main.py plot --re 0.100 --profiles "NACA,CLARK YS" --out selected_polars.png
```

**Example 3**: Plot only MH profiles at Re = 0.500

```powershell
python main.py plot --re 0.500 --profiles "MH" --out mh_polars.png
```

**Note on profile selection**: The `--profiles` parameter accepts a comma-separated list of names or substrings. The script will search for all files containing any of those strings in their name. For example:

- `--profiles "NACA"` will include all NACA profiles (NACA 0015, NACA 4408, etc.)
- `--profiles "MH 16,MH 17"` will include only MH 16 and MH 17
- Without specifying `--profiles`, all available profiles are plotted

### Extract limits (minimum and maximum)

**Example 1**: Extract limits from all profiles at Re = 0.688 and display in console

```powershell
python main.py limits --re 0.688
```

**Example 2**: Extract limits and export to CSV for Excel

```powershell
python main.py limits --re 0.688 --csv limits_Re0688.csv
```

**Example 3**: Extract limits sorted by Cl/Cd_max (descending) and export

```powershell
python main.py limits --re 0.688 --sort="-Cl/Cd_max" --csv sorted_limits.csv
```

**Example 4**: Extract limits sorted by lift slope (Cl_alpha) descending

```powershell
python main.py limits --re 0.688 --sort="-Cl_alpha"
```

The limits table includes:

- `Cl_alpha`: Lift slope (dCl/dα) in the linear region, calculated from -2° to 5° (per radian)
- `Cm_0`: Pitching moment coefficient at α = 0° (important for longitudinal stability)
- `Cd_min` and `α @ Cd_min` (angle where it occurs)
- `Cl_max` and `α @ Cl_max` (angle where it occurs)
- `Cl/Cd_max` and `α @ Cl/Cd_max` (angle where it occurs)

### Extract values at specific angles

**Example 1**: Extract all coefficient values at α = 0°, 5° and 10° for CLARK profiles

```powershell
python main.py extract --re 0.688 --alphas="0,5,10" --profiles "CLARK"
```

**Example 2**: Extract and export to CSV

```powershell
python main.py extract --re 0.688 --alphas="0,5,10" --profiles "CLARK" --csv clark_values.csv
```

## Notes

- The parser attempts to extract `alpha`, `CL`, `CD`, `Cm` columns from XFLR5 files.
- If any file cannot be parsed correctly, it will be ignored with a warning.
- Re filters work by searching for the provided string in the file name (e.g., `0.100` matches files containing `Re0.100`).
