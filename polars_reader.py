import re
from pathlib import Path
import pandas as pd
import numpy as np

POLARS_DIR = Path(__file__).parent / "polars"

_re_re = re.compile(r"Re\s*=\s*([0-9.+-eE]+)\s*e\s*([0-9]+)")
_re_re_simple = re.compile(r"Re([0-9.]+)")
_re_name = re.compile(r"Calculated polar for:\s*(.*)")


def list_polar_files(polars_dir=None):
    d = Path(polars_dir) if polars_dir else POLARS_DIR
    return sorted([p for p in d.glob("*.txt")])


def parse_re_from_header(text):
    m = _re_re.search(text)
    if m:
        mant = float(m.group(1))
        exp = int(m.group(2))
        return mant * (10**exp)
    # fallback: try find ReNNN in filename style
    m2 = _re_re_simple.search(text)
    if m2:
        return (
            float(m2.group(1)) * 1e6
            if float(m2.group(1)) < 1000
            else float(m2.group(1))
        )
    return None


def parse_name_from_header(text):
    m = _re_name.search(text)
    return m.group(1).strip() if m else None


def parse_polar_file(path):
    path = Path(path)
    text = path.read_text(encoding="utf-8", errors="ignore")
    name = parse_name_from_header(text) or path.stem
    # try to get Re from header string
    re_val = parse_re_from_header(text)

    lines = text.splitlines()
    # find header line that contains 'alpha' (case-insensitive) and 'CL'
    header_idx = None
    for i, ln in enumerate(lines):
        low = ln.lower()
        if "alpha" in low and "cl" in low:
            header_idx = i
            break
    data = []
    colnames = None
    if header_idx is not None:
        # header columns
        header_line = lines[header_idx].strip()
        # split header into tokens
        colnames = re.split(r"\s+", header_line)
        # data starts two lines after header (often a dash line)
        for ln in lines[header_idx + 2 :]:
            if not ln.strip():
                break
            toks = re.split(r"\s+", ln.strip())
            # select numeric tokens
            numtoks = []
            for t in toks:
                try:
                    numtoks.append(float(t))
                except:
                    pass
            if len(numtoks) >= 5:
                # alpha, CL, CD, CDp, Cm
                row = {
                    "alpha": numtoks[0],
                    "CL": numtoks[1],
                    "CD": numtoks[2],
                    "CDp": numtoks[3] if len(numtoks) > 3 else np.nan,
                    "Cm": numtoks[4] if len(numtoks) > 4 else np.nan,
                }
                data.append(row)
    # fallback: try pandas read_table by whitespace
    if not data:
        try:
            df = pd.read_csv(
                path,
                delim_whitespace=True,
                comment="%",
                header=None,
                engine="python",
            )
            # try to find first row with alphabetic 'alpha' in it
            # not robust but a fallback
            # find rows with at least 5 numeric columns
            good = df.dropna(how="all")
            if good.shape[1] >= 5:
                # take first N numeric columns
                arr = good.values
                for r in arr:
                    try:
                        a = float(r[0])
                        cl = float(r[1])
                        cd = float(r[2])
                        cm = float(r[4])
                        data.append(
                            {
                                "alpha": a,
                                "CL": cl,
                                "CD": cd,
                                "CDp": float(r[3]) if len(r) > 3 else np.nan,
                                "Cm": cm,
                            }
                        )
                    except:
                        continue
        except Exception:
            pass

    df = pd.DataFrame(data)
    if not df.empty:
        df = df.sort_values("alpha").reset_index(drop=True)
        df["Cl_Cd"] = df["CL"] / df["CD"].replace(0, np.nan)

    return {"path": path, "name": name, "re": re_val, "df": df}


def list_available_re(polars_dir=None):
    files = list_polar_files(polars_dir)
    vals = set()
    for f in files:
        s = str(f)
        m = _re_re_simple.search(s)
        if m:
            vals.add(m.group(1))
        else:
            # parse header
            p = parse_polar_file(f)
            if p["re"] is not None:
                vals.add(str(p["re"]))
    return sorted(vals)
