# Summary

Collection of scripts for XFLR5 polar analysis.

Main files

- `polars_reader.py`: reading and parsing files in `polars/`.
- `plot_polars.py`: generates a figure with 4 subplots (Cl vs alpha, Cm vs alpha, Cd vs Cl, Cl/Cd vs alpha).
- `extract_limits.py`: extracts minimum and maximum limits per column and values near requested alphas.
- `main.py`: CLI that allows executing the functionalities.

## Available Data

The `polars/` directory contains pre-calculated polar data for **80 airfoil profiles** at **13 different Reynolds numbers** (0.100e6 to 1.000e6), totaling **1040 polar files**.

**NOTE**: This package includes only polar data files (`.txt`). Airfoil geometry files (`.dat`) are **NOT included**.

For a complete list of available profiles and Reynolds numbers, see the file:

- **`AVAILABLE_PROFILES.txt`** - Lists all 80 profiles and their availability across Reynolds numbers

To regenerate this list, run:

```powershell
python generate_profiles_list.py
```

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

#### Plot with filters

You can apply performance filters directly when plotting polars. The filter criteria will be displayed as an annotation below the title with proper mathematical notation (LaTeX symbols with subscripts and operators).

**Example 4**: Plot only profiles with high maximum lift (Cl_max >= 1.26)

```powershell
python main.py plot --re 0.688 --filter "cl_max >= 1.26" --out high_lift_polars.png
```

**Example 5**: Plot profiles with low drag and high efficiency

```powershell
python main.py plot --re 0.688 --filter "cd_min < 0.006" --filter "cl_cd_max > 100" --out efficient_polars.png
```

**Example 6**: Find profiles suitable for specific design requirements

```powershell
# High lift with reasonable drag
python main.py plot --re 0.688 --filter "cl_max >= 1.4" --filter "cd_min < 0.007" --out design_candidates.png
```

**Filter Display**: The filters are shown in a separate annotation box below the title using proper aerodynamic notation:

- Parameters are converted to LaTeX format (e.g., `cl_max` → $C_{l_{max}}$, `cl_cd_max` → $(C_l/C_d)_{max}$)
- Operators use mathematical symbols (e.g., `>=` → ≥, `<=` → ≤)
- Multiple filters are separated by `|` for clarity

**Note**: Filters use the same syntax and aliases as the `filter` action (see Filter Profiles section below). Multiple `--filter` arguments are combined with AND logic.

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

#### Plot Cl_max vs Cl_ideal with filters

You can also apply performance filters to this plot. The filter criteria will be displayed as an annotation with proper mathematical notation.

**Example 4**: Plot only high-lift profiles

```powershell
python main.py plot-clmax-cli --re 0.688 --filter "cl_max >= 1.4" --out clmax_high_lift.png
```

**Example 5**: Combine multiple criteria for design selection

```powershell
python main.py plot-clmax-cli --re 0.688 --filter "cl_max >= 1.4" --filter "cl_cd_max > 100" --filter "cd_min < 0.007" --out clmax_design_candidates.png
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
python main.py limits --re 0.688 --sort="-Cl_alpha (rad⁻¹)"
```

The limits table includes:

- `Cl_alpha (deg⁻¹)`: Lift slope (dCl/dα) per degree in the linear region, calculated from -2° to 5°
- `Cl_alpha (rad⁻¹)`: Lift slope (dCl/dα) per radian in the linear region, calculated from -2° to 5°
- `Cm_0`: Pitching moment coefficient at α = 0° (important for longitudinal stability)
- `Cd_min` and `α @ Cd_min (deg)`: Minimum drag coefficient and angle where it occurs
- `Cl_i`: Lift coefficient at minimum drag (simplified notation for Cl_ideal, the optimal cruise Cl)
- `Cl/Cd @ Cl_i`: Lift-to-drag ratio evaluated at Cl_ideal (cruise efficiency at the optimal operating point)
- `Cl_max`, `α @ Cl_max (deg)` and `Cd @ Cl_max`: Maximum lift coefficient, angle where it occurs, and drag at maximum lift
- `Cl/Cd_max` and `α @ Cl/Cd_max (deg)`: Maximum lift-to-drag ratio and angle where it occurs

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

The `--filter` parameter is a powerful tool that allows you to select airfoil profiles based on specific aerodynamic performance thresholds. **Filters work with all actions** (limits, extract, plot, plot-clmax-cli), not as a separate action.

#### Filter Syntax

```powershell
python main.py <action> --re <reynolds> --filter "parameter operator value" [options]
```

**Basic structure:**

- `--filter` or `-f`: Specifies a filtering criterion (can be used multiple times with any action)
- Format: `"parameter operator value"` (always use quotes)
- Multiple filters are combined with **AND logic** (all criteria must be met)

**Filter behavior by action:**

- **`limits`**: Shows only profiles matching criteria in the limits table
- **`extract`**: Extracts alpha data only for profiles matching criteria
- **`plot`**: Plots polar curves only for profiles matching criteria
- **`plot-clmax-cli`**: Shows only matching profiles in the Clmax vs Cli scatter plot

#### Available Parameters

You can filter by any column from the limits table using either **full names** or **short aliases** (recommended for easier typing):

| Short Alias       | Full Name             | Description                                 | Typical Range |
| ----------------- | --------------------- | ------------------------------------------- | ------------- |
| `cl_alpha_deg`    | `Cl_alpha (deg⁻¹)`    | Lift slope per degree                       | 0.09 - 0.14   |
| `cl_alpha_rad`    | `Cl_alpha (rad⁻¹)`    | Lift slope per radian                       | 5.0 - 8.0     |
| `cl_alpha`        | `Cl_alpha (rad⁻¹)`    | Lift slope (defaults to rad⁻¹)              | 5.0 - 8.0     |
| `cm_0`            | `Cm_0`                | Pitching moment at α=0°                     | -0.3 to 0.1   |
| `cd_min`          | `Cd_min`              | Minimum drag coefficient                    | 0.004 - 0.015 |
| `cd_at_cl_max`    | `Cd @ Cl_max`         | Drag at maximum lift                        | 0.01 - 0.35   |
| `cl_max`          | `Cl_max`              | Maximum lift coefficient                    | 0.8 - 2.5     |
| `cl_i`            | `Cl_i`                | Cl at minimum drag (Cl_ideal)               | 0.2 - 1.5     |
| `cl_ideal`        | `Cl_i`                | Alias for Cl_i (optimal cruise Cl)          | 0.2 - 1.5     |
| `cl_cd_max`       | `Cl/Cd_max`           | Maximum lift-to-drag ratio                  | 50 - 200      |
| `cl_cd_at_cli`    | `Cl/Cd @ Cl_i`        | Cl/Cd evaluated at Cl_i (cruise efficiency) | 40 - 190      |
| `cl_cd_cli`       | `Cl/Cd @ Cl_i`        | Short alias for cl_cd_at_cli                | 40 - 190      |
| `alpha_cd_min`    | `α @ Cd_min (deg)`    | Angle at minimum drag                       | -2° to 5°     |
| `alpha_cl_max`    | `α @ Cl_max (deg)`    | Angle at maximum lift (stall angle)         | 8° to 25°     |
| `alpha_cl_cd_max` | `α @ Cl/Cd_max (deg)` | Angle at best efficiency                    | 2° to 8°      |

**Note**: You can use either the short alias (e.g., `cl_alpha`) or the full name (e.g., `Cl_alpha (rad⁻¹)`) in filters. Short aliases are recommended as they are all lowercase and don't contain special characters. The alias system is case-insensitive: `Cl_alpha`, `cl_alpha`, and `CL_ALPHA` all work.

**Important**: The simplified notation `Cl_i` (instead of `Cl @ Cd_min` or `Cl_ideal`) is used throughout to represent the ideal lift coefficient for cruise - the Cl value at minimum drag (Cd_min). Similarly, `Cl/Cd @ Cl_i` represents the lift-to-drag ratio evaluated at this optimal cruise point, providing a measure of cruise efficiency.

#### Available Operators

| Operator  | Meaning               | Example (short alias)    | Example (full name)          |
| --------- | --------------------- | ------------------------ | ---------------------------- |
| `>`       | Greater than          | `"cl_cd_max > 100"`      | `"Cl/Cd_max > 100"`          |
| `>=`      | Greater than or equal | `"cl_alpha >= 6.5"`      | `"Cl_alpha (rad⁻¹) >= 6.5"`  |
| `<`       | Less than             | `"cd_min < 0.006"`       | `"Cd_min < 0.006"`           |
| `<=`      | Less than or equal    | `"cm_0 <= -0.05"`        | `"Cm_0 <= -0.05"`            |
| `==`      | Equal to              | `"cl_max == 1.5"`        | `"Cl_max == 1.5"`            |
| `!=`      | Not equal to          | `"alpha_cl_max != 10.0"` | `"α @ Cl_max (deg) != 10.0"` |
| `between` | Range (inclusive)     | `"cl_i between 0.3,0.8"` | `"Cl_i between 0.3,0.8"`     |

**Note**: The `between` operator allows filtering within a range using the syntax `"parameter between min,max"`. Both minimum and maximum values are inclusive (min ≤ parameter ≤ max).

#### Detailed Examples

**Example 1**: List high-efficiency profiles for cruise (limits action)

Find profiles with excellent lift-to-drag ratio at typical cruise Reynolds number:

```powershell
python main.py limits --re 0.688 --filter "cl_cd_max > 100"
```

**Example 2**: Plot only low-drag profiles (plot action)

Plot profiles combining low minimum drag with adequate maximum lift:

```powershell
python main.py plot --re 0.688 --filter "cd_min < 0.006" --filter "cl_max > 1.5" --out selected_polars.png
```

**Example 3**: Extract data for low-speed profiles (extract action)

Extract specific alpha data for profiles optimized for low-speed operations:

```powershell
python main.py extract --re 0.100 --alphas="0,5,10" --filter "cl_alpha > 6.0" --filter "cm_0 > -0.05" --csv low_speed_profiles.csv
```

**Example 4**: Moment-stable profiles sorted by efficiency (limits action)

Find profiles with stable pitching moment characteristics (near zero cm_0) and rank by efficiency:

```powershell
python main.py limits --re 0.500 --filter "cm_0 >= -0.10" --filter "cm_0 <= 0.10" --sort="-Cl/Cd_max"
```

Alternatively, using the `between` operator for more concise syntax:

```powershell
python main.py limits --re 0.500 --filter "cm_0 between -0.10,0.10" --sort="-Cl/Cd_max"
```

**Example 5**: Plot Clmax vs Cli for ultra-efficient profiles (plot-clmax-cli action)

Generate a scatter plot showing only profiles that maintain low drag even at maximum lift:

```powershell
python main.py plot-clmax-cli --re 0.688 --filter "Cl/Cd_max > 150" --filter "Cd @ Cl_max < 0.05" --out efficient_profiles.png
```

**Example 6**: Search within specific profile families (limits action)

Limit search to MH-series profiles and apply performance criteria:

```powershell
python main.py limits --re 0.688 --profiles "MH" --filter "Cl/Cd_max > 120" --filter "cd_min < 0.0055"
```

**Example 7**: Complex multi-criteria selection with CSV export (limits action)

Find profiles with a specific combination of characteristics and export to CSV:

```powershell
python main.py limits --re 0.688 --filter "cl_alpha > 7.0" --filter "cd_min < 0.006" --filter "cl_cd_max > 100" --filter "cm_0 > -0.05" --sort="-Cl/Cd_max" --csv selected_profiles.csv
```

**Example 8**: Plot profiles with specific angle characteristics (plot action)

Plot only profiles that reach maximum efficiency at low angles:

```powershell
python main.py plot --re 0.688 --filter "cl_cd_max > 120" --filter "alpha_cl_cd_max < 4.0" --out low_angle_efficient.png
```

**Example 9**: Extract data for cruise-optimized profiles (extract action)

Extract alpha values for profiles optimized for specific cruise conditions:

```powershell
python main.py extract --re 0.688 --alphas="2,4,6,8" --filter "cl_ideal > 0.4" --filter "alpha_cd_min < 2.0" --filter "cl_cd_max > 100" --csv cruise_profiles.csv
```

**Example 9**: High-lift profiles with controlled stall

Find profiles with high cl_max but reasonable stall angle:

```powershell
python main.py filter --re 0.500 --filter "cl_max > 1.8" --filter "alpha_cl_max < 15.0"
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
python main.py filter --re 0.500 --filter "Cl/Cd_max > 150" --filter "cd_min < 0.005" --filter "cm_0 >= -0.08" --filter "cm_0 <= 0.08"
```

**2. Motor Glider / Efficient Cruiser**

```powershell
# Good efficiency, moderate lift, stable
python main.py filter --re 0.688 --filter "Cl/Cd_max > 100" --filter "cl_max > 1.3" --filter "Cd @ Cl_max < 0.04"
```

**3. Slow-Speed Trainer / STOL Aircraft**

```powershell
# High lift slope, high cl_max, low-speed Re
python main.py filter --re 0.200 --filter "cl_alpha > 6.5" --filter "cl_max > 1.5" --filter "alpha_cl_max < 16.0"
```

**4. Aerobatic Aircraft**

```powershell
# Symmetric-like characteristics (low moment), good efficiency range
python main.py filter --re 0.625 --filter "cm_0 >= -0.05" --filter "cm_0 <= 0.05" --filter "cl_cd_max > 80"
```

**5. High-Speed Cruise**

```powershell
# Very low drag, efficiency at low angles
python main.py filter --re 1.000 --filter "cd_min < 0.0055" --filter "alpha_cd_min < 2.0" --filter "cl_cd_max > 120"
```

#### Tips and Best Practices

**Combining Filters:**

- Filters use AND logic: all criteria must be satisfied
- Start with broad criteria, then refine with additional filters
- Use `--sort` to rank results by your priority parameter

**Performance Considerations:**

- **Efficiency**: Prioritize `cl_cd_max` and `cd_min`
- **Stability**: Monitor `cm_0` (closer to zero = more stable)
- **Operating Range**: Consider `alpha_cl_cd_max` for typical flight angles
- **Stall Behavior**: Check `alpha_cl_max` and `cd_at_cl_max`

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
