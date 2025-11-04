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

### Plot Cl_max vs Cl_ideal comparison

This plot shows the relationship between maximum lift coefficient (Cl_max) and ideal lift coefficient (Cl_ideal or Cl @ Cd_min). Cl_ideal is the lift coefficient at minimum drag (Cd_min), representing the optimal operating point for cruise efficiency.

**Example 1**: Plot Cl_max vs Cl_ideal for all profiles at Re = 0.688

```powershell
python main.py plot-clmax-cli --re 0.688 --out clmax_vs_clideal.png
```

**Example 2**: Compare specific profile families

```powershell
python main.py plot-clmax-cli --re 0.688 --profiles "MH,NACA" --out clmax_comparison.png
```

**Example 3**: Analyze at different Reynolds numbers

```powershell
python main.py plot-clmax-cli --re 0.100 --out clmax_low_re.png
python main.py plot-clmax-cli --re 1.000 --out clmax_high_re.png
```

**Interpretation**:

- Profiles above the diagonal line (Cl_max = Cl_ideal) have higher maximum lift than their cruise optimum
- Profiles close to the diagonal have similar Cl_max and Cl_ideal, indicating narrow operating range
- Larger vertical distance from diagonal suggests better high-lift capability beyond cruise conditions

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
- `Cd_min` and `α @ Cd_min` (angle at minimum drag, where Cl_ideal occurs)
- `Cl @ Cd_min`: Lift coefficient at minimum drag (also known as Cl_ideal, the optimal cruise Cl)
- `Cl_max`, `α @ Cl_max` (angle where it occurs), and `Cd @ Cl_max` (drag coefficient at maximum lift)
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

### Filter profiles by performance criteria

The `filter` action is a powerful tool that allows you to select airfoil profiles based on specific aerodynamic performance thresholds. This is particularly useful for aircraft design when you need to identify profiles that meet certain requirements.

#### Filter Syntax

```powershell
python main.py filter --re <reynolds> --filter "parameter operator value" [options]
```

**Basic structure:**

- `--filter` or `-f`: Specifies a filtering criterion (can be used multiple times)
- Format: `"parameter operator value"` (always use quotes)
- Multiple filters are combined with **AND logic** (all criteria must be met)

#### Available Parameters

You can filter by any column from the limits table:

| Parameter       | Description                            | Typical Range | Use Case                                 |
| --------------- | -------------------------------------- | ------------- | ---------------------------------------- |
| `Cl_alpha`      | Lift slope (dCl/dα) in per radian      | 5.0 - 8.0     | High sensitivity to angle changes        |
| `Cm_0`          | Pitching moment at α=0°                | -0.3 to 0.1   | Longitudinal stability (near 0 = stable) |
| `Cd_min`        | Minimum drag coefficient               | 0.004 - 0.015 | Low-drag profiles for cruise             |
| `α @ Cd_min`    | Angle at minimum drag (where Cl_ideal) | -2° to 5°     | Optimal cruise angle                     |
| `Cl @ Cd_min`   | Cl at minimum drag (Cl_ideal)          | 0.2 - 1.5     | Optimal cruise lift coefficient          |
| `Cl_max`        | Maximum lift coefficient               | 0.8 - 2.5     | High-lift capability for takeoff/landing |
| `Cd @ Cl_max`   | Drag at maximum lift                   | 0.01 - 0.35   | Drag penalty at high angles of attack    |
| `Cl/Cd_max`     | Maximum lift-to-drag ratio             | 50 - 200      | Overall aerodynamic efficiency           |
| `α @ Cl_max`    | Angle at maximum lift                  | 8° to 25°     | Stall angle                              |
| `α @ Cl/Cd_max` | Angle at best efficiency               | 2° to 8°      | Optimal operating angle                  |

#### Available Operators

| Operator | Meaning               | Example             |
| -------- | --------------------- | ------------------- |
| `>`      | Greater than          | `"Cl/Cd_max > 100"` |
| `>=`     | Greater than or equal | `"Cl_alpha >= 6.5"` |
| `<`      | Less than             | `"Cd_min < 0.006"`  |
| `<=`     | Less than or equal    | `"Cm_0 <= -0.05"`   |
| `==`     | Equal to              | `"Cl_max == 1.5"`   |
| `!=`     | Not equal to          | `"Cd_min != 0.01"`  |

#### Detailed Examples

**Example 1**: Find high-efficiency profiles for cruise

Find profiles with excellent lift-to-drag ratio at typical cruise Reynolds number:

```powershell
python main.py filter --re 0.688 --filter "Cl/Cd_max > 100"
```

**Example 2**: Low-drag profiles with good lift capability

Find profiles combining low minimum drag with adequate maximum lift:

```powershell
python main.py filter --re 0.688 --filter "Cd_min < 0.006" --filter "Cl_max > 1.5"
```

**Example 3**: Profiles optimized for low-speed flight

Find profiles with high lift slope and stable pitching moment for low-speed operations:

```powershell
python main.py filter --re 0.100 --filter "Cl_alpha > 6.0" --filter "Cm_0 > -0.05" --csv low_speed_profiles.csv
```

**Example 4**: Moment-stable profiles sorted by efficiency

Find profiles with stable pitching moment characteristics (near zero Cm_0) and rank by efficiency:

```powershell
python main.py filter --re 0.500 --filter "Cm_0 >= -0.10" --filter "Cm_0 <= 0.10" --sort="-Cl/Cd_max"
```

**Example 5**: Ultra-efficient profiles with low drag at Cl_max

Find profiles that maintain low drag even at maximum lift angle:

```powershell
python main.py filter --re 0.688 --filter "Cl/Cd_max > 150" --filter "Cd @ Cl_max < 0.05"
```

**Example 6**: Search within specific profile families

Limit search to MH-series profiles and apply performance criteria:

```powershell
python main.py filter --re 0.688 --profiles "MH" --filter "Cl/Cd_max > 120" --filter "Cd_min < 0.0055"
```

**Example 7**: Complex multi-criteria selection

Find profiles with a specific combination of characteristics:

```powershell
python main.py filter --re 0.688 --filter "Cl_alpha > 7.0" --filter "Cd_min < 0.006" --filter "Cl/Cd_max > 100" --filter "Cm_0 > -0.05" --sort="-Cl/Cd_max" --csv selected_profiles.csv
```

**Example 8**: Profiles with specific angle characteristics

Find profiles that reach maximum efficiency at low angles:

```powershell
python main.py filter --re 0.688 --filter "Cl/Cd_max > 120" --filter "α @ Cl/Cd_max < 4.0"
```

**Example 8b**: Profiles optimized for specific cruise angle

Find profiles with Cl_ideal (optimal cruise Cl) at low angles of attack:

```powershell
python main.py filter --re 0.688 --filter "Cl @ Cd_min > 0.4" --filter "α @ Cd_min < 2.0" --filter "Cl/Cd_max > 100"
```

**Example 9**: High-lift profiles with controlled stall

Find profiles with high Cl_max but reasonable stall angle:

```powershell
python main.py filter --re 0.500 --filter "Cl_max > 1.8" --filter "α @ Cl_max < 15.0"
```

**Example 10**: Compare different Reynolds numbers

Export filtered results at different Re for comparison:

```powershell
python main.py filter --re 0.100 --filter "Cl/Cd_max > 100" --csv re_100_efficient.csv
python main.py filter --re 0.688 --filter "Cl/Cd_max > 100" --csv re_688_efficient.csv
```

#### Practical Use Cases

**1. Sailplane/Glider Design**

```powershell
# Very high efficiency, low drag, stable moment
python main.py filter --re 0.500 --filter "Cl/Cd_max > 150" --filter "Cd_min < 0.005" --filter "Cm_0 >= -0.08" --filter "Cm_0 <= 0.08"
```

**2. Motor Glider / Efficient Cruiser**

```powershell
# Good efficiency, moderate lift, stable
python main.py filter --re 0.688 --filter "Cl/Cd_max > 100" --filter "Cl_max > 1.3" --filter "Cd @ Cl_max < 0.04"
```

**3. Slow-Speed Trainer / STOL Aircraft**

```powershell
# High lift slope, high Cl_max, low-speed Re
python main.py filter --re 0.200 --filter "Cl_alpha > 6.5" --filter "Cl_max > 1.5" --filter "α @ Cl_max < 16.0"
```

**4. Aerobatic Aircraft**

```powershell
# Symmetric-like characteristics (low moment), good efficiency range
python main.py filter --re 0.625 --filter "Cm_0 >= -0.05" --filter "Cm_0 <= 0.05" --filter "Cl/Cd_max > 80"
```

**5. High-Speed Cruise**

```powershell
# Very low drag, efficiency at low angles
python main.py filter --re 1.000 --filter "Cd_min < 0.0055" --filter "α @ Cd_min < 2.0" --filter "Cl/Cd_max > 120"
```

#### Tips and Best Practices

**Combining Filters:**

- Filters use AND logic: all criteria must be satisfied
- Start with broad criteria, then refine with additional filters
- Use `--sort` to rank results by your priority parameter

**Performance Considerations:**

- **Efficiency**: Prioritize `Cl/Cd_max` and `Cd_min`
- **Stability**: Monitor `Cm_0` (closer to zero = more stable)
- **Operating Range**: Consider `α @ Cl/Cd_max` for typical flight angles
- **Stall Behavior**: Check `α @ Cl_max` and `Cd @ Cl_max`

**Workflow Recommendations:**

1. First, use `limits` to see all available profiles and their characteristics
2. Identify target values for your design requirements
3. Use `filter` with broad criteria to get a shortlist
4. Refine with additional criteria
5. Export to CSV for detailed analysis in Excel
6. Use `plot` to visualize the final candidates

**Command Options:**

- `--profiles "name1,name2"`: Pre-filter by profile family before applying criteria
- `--sort="parameter"`: Sort ascending by parameter
- `--sort="-parameter"`: Sort descending (use `-` prefix)
- `--csv filename.csv`: Export results for further analysis
- `--re value`: Always specify Reynolds number for consistent comparison

**Note on Quotes:**
Always use quotes around filter criteria to prevent the shell from interpreting operators:

- ✅ Correct: `--filter "Cl/Cd_max > 100"`
- ❌ Wrong: `--filter Cl/Cd_max > 100` (shell interprets `>` as redirection)

## Notes

- The parser attempts to extract `alpha`, `CL`, `CD`, `Cm` columns from XFLR5 files.
- If any file cannot be parsed correctly, it will be ignored with a warning.
- Re filters work by searching for the provided string in the file name (e.g., `0.100` matches files containing `Re0.100`).
