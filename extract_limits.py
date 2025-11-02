from polars_reader import list_polar_files, parse_polar_file
import numpy as np
import pandas as pd


def extract_values(
    polars_dir=None, profiles=None, re_filter=None, alphas=None
):
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
            continue
        row = {}
        # values at requested alphas (nearest)
        if alphas:
            for a in alphas:
                idx = (df["alpha"] - a).abs().idxmin()
                rec = df.loc[idx].to_dict()
                # convert numpy types
                row[f"alpha_{a}"] = {
                    k: (float(v) if np.isscalar(v) else v)
                    for k, v in rec.items()
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
            continue

        # Find CD min
        cd_min_idx = df["CD"].idxmin()
        cd_min = float(df.loc[cd_min_idx, "CD"])
        alpha_cd_min = float(df.loc[cd_min_idx, "alpha"])

        # Find CL max
        cl_max_idx = df["CL"].idxmax()
        cl_max = float(df.loc[cl_max_idx, "CL"])
        alpha_cl_max = float(df.loc[cl_max_idx, "alpha"])

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
            # Convert alpha from degrees to radians for the slope
            alphas_rad = np.deg2rad(alphas)
            # Fit: Cl = a * alpha_rad + b
            coeffs = np.polyfit(alphas_rad, cls, 1)
            cl_alpha = float(coeffs[0])  # per radian
        else:
            cl_alpha = np.nan

        table_data.append(
            {
                "Profile": name,
                "Cl_alpha": cl_alpha,
                "Cd_min": cd_min,
                "α @ Cd_min": alpha_cd_min,
                "Cl_max": cl_max,
                "α @ Cl_max": alpha_cl_max,
                "Cl/Cd_max": clcd_max,
                "α @ Cl/Cd_max": alpha_clcd_max,
            }
        )

    return pd.DataFrame(table_data)


if __name__ == "__main__":
    # Test limits
    df = extract_limits()
    print(df.to_string())
