import numpy as np
import pandas as pd

from polars_reader import list_polar_files, parse_polar_file


def extract_values(polars_dir=None, profiles=None, re_filter=None, alphas=None):
    """Extract coefficient values at specific angles of attack."""
    files = list_polar_files(polars_dir)
    if profiles:
        procs = []
        for p in profiles:
            for f in files:
                if p in f.name:
                    procs.append(f)
        files = sorted(set(procs), key=lambda p: p.name)
    if re_filter:
        files = [f for f in files if re_filter in f.name]
    if not files:
        raise RuntimeError("No polar files matched selection")

    results = {}
    for f in files:
        p = parse_polar_file(f)
        df = p["df"]
        name = p["name"]
        if df is None or df.empty:
            print(f"WARNING: Skipping '{name}' - no polar data available (empty file)")
            continue
        row = {}
        # values at requested alphas (nearest)
        if alphas:
            for a in alphas:
                idx = (df["alpha"] - a).abs().idxmin()
                rec = df.loc[idx].to_dict()
                # convert numpy types
                row[f"alpha_{a}"] = {
                    k: (float(v) if np.isscalar(v) else v) for k, v in rec.items()
                }
        results[name] = row
    return results


def extract_limits(polars_dir=None, profiles=None, re_filter=None):
    """Extract limit values (min/max) and the angles where they occur."""
    files = list_polar_files(polars_dir)
    if profiles:
        procs = []
        for p in profiles:
            for f in files:
                if p in f.name:
                    procs.append(f)
        files = sorted(set(procs), key=lambda p: p.name)
    if re_filter:
        files = [f for f in files if re_filter in f.name]
    if not files:
        raise RuntimeError("No polar files matched selection")

    table_data = []
    for f in files:
        p = parse_polar_file(f)
        df = p["df"]
        name = p["name"]
        if df is None or df.empty:
            print(f"WARNING: Skipping '{name}' - no polar data available (empty file)")
            continue

        # Find CD min
        cd_min_idx = df["CD"].idxmin()
        cd_min = float(df.loc[cd_min_idx, "CD"])
        alpha_cd_min = float(df.loc[cd_min_idx, "alpha"])
        cl_ideal = float(df.loc[cd_min_idx, "CL"])  # Cl at Cd_min (ideal Cl)

        # Calculate Cl/Cd at Cl_ideal (Cl_i)
        cl_cd_at_cli = cl_ideal / cd_min if cd_min != 0 else np.nan

        # Find CL max
        cl_max_idx = df["CL"].idxmax()
        cl_max = float(df.loc[cl_max_idx, "CL"])
        alpha_cl_max = float(df.loc[cl_max_idx, "alpha"])
        cd_at_cl_max = float(df.loc[cl_max_idx, "CD"])

        # Find Cl/Cd max
        clcd_max_idx = df["Cl_Cd"].idxmax()
        clcd_max = float(df.loc[clcd_max_idx, "Cl_Cd"])
        alpha_clcd_max = float(df.loc[clcd_max_idx, "alpha"])

        # Calculate lift slope (Cl_alpha) in the linear region
        # Find data near alpha = 0 (between -2 and 5 degrees for better linear fit)
        linear_region = df[(df["alpha"] >= -2) & (df["alpha"] <= 5)]
        if len(linear_region) >= 2:
            # Linear regression: Cl = Cl_alpha * alpha + Cl_0
            alphas = linear_region["alpha"].values
            cls = linear_region["CL"].values

            # Calculate in degrees (alpha in degrees)
            coeffs_deg = np.polyfit(alphas, cls, 1)
            cl_alpha_deg = float(coeffs_deg[0])  # per degree

            # Calculate in radians (alpha converted to radians)
            alphas_rad = np.deg2rad(alphas)
            coeffs_rad = np.polyfit(alphas_rad, cls, 1)
            cl_alpha_rad = float(coeffs_rad[0])  # per radian
        else:
            cl_alpha_deg = np.nan
            cl_alpha_rad = np.nan

        # Find Cm at alpha = 0 degrees (nearest value)
        idx_0 = (df["alpha"] - 0.0).abs().idxmin()
        cm_0 = float(df.loc[idx_0, "Cm"])

        table_data.append(
            {
                "Profile": name,
                "Cl_alpha (deg⁻¹)": cl_alpha_deg,
                "Cl_alpha (rad⁻¹)": cl_alpha_rad,
                "Cm_0": cm_0,
                "Cd_min": cd_min,
                "α @ Cd_min (deg)": alpha_cd_min,
                "Cl_i": cl_ideal,  # Simplified name for Cl_ideal
                "Cl/Cd @ Cl_i": cl_cd_at_cli,  # Cl/Cd evaluated at Cl_ideal
                "Cl_max": cl_max,
                "α @ Cl_max (deg)": alpha_cl_max,
                "Cd @ Cl_max": cd_at_cl_max,
                "Cl/Cd_max": clcd_max,
                "α @ Cl/Cd_max (deg)": alpha_clcd_max,
            }
        )

    return pd.DataFrame(table_data)


if __name__ == "__main__":
    # Test limits
    df = extract_limits()
    print(df.to_string())
