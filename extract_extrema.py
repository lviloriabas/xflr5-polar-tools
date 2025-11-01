from polars_reader import list_polar_files, parse_polar_file
import numpy as np


def extract_extrema(
    polars_dir=None, profiles=None, re_filter=None, alphas=None
):
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
        # min/max per column
        cols = ["CL", "CD", "Cm", "Cl_Cd"]
        for c in cols:
            if c in df.columns:
                row[c] = {"min": float(df[c].min()), "max": float(df[c].max())}
        # values at requested alphas (nearest)
        if alphas:
            row["at_alpha"] = {}
            for a in alphas:
                idx = (df["alpha"] - a).abs().idxmin()
                rec = df.loc[idx].to_dict()
                # convert numpy types
                row["at_alpha"][a] = {
                    k: (float(v) if np.isscalar(v) else v)
                    for k, v in rec.items()
                }
        results[name] = row
    return results


if __name__ == "__main__":
    r = extract_extrema()
    import pprint

    pprint.pprint(r)
