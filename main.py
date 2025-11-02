import argparse
from pathlib import Path
from polars_reader import list_available_re


def _parse_csv_list(s):
    if not s:
        return None
    return [p.strip() for p in s.split(",") if p.strip()]


def _parse_alphas(s):
    if not s:
        return None
    parts = [p.strip() for p in s.split(",") if p.strip()]
    return [float(p) for p in parts]


def main():
    p = argparse.ArgumentParser(description="Tools for XFLR5 polar analysis")
    p.add_argument(
        "action",
        choices=["plot", "extract", "limits"],
        help="Functionality to execute",
    )
    p.add_argument(
        "--profiles",
        "-p",
        help="Profiles to include (comma-separated, substring of name). Default: all",
    )
    p.add_argument(
        "--re",
        help="Reynolds filter (e.g.: 0.100 or Re0.100). If not specified, uses all",
    )
    p.add_argument(
        "--polars-dir",
        default=str(Path(__file__).parent / "polars"),
        help="Polars directory",
    )
    p.add_argument("--out", "-o", help="Output path for figures (plot)")
    p.add_argument(
        "--alphas",
        help="List of alpha for extraction in 'extract' (comma-separated)",
    )
    p.add_argument(
        "--sort",
        help="Sort limits table by column (e.g.: Cd_min, Cl_max, Cl/Cd_max). Use '-' for descending (e.g.: -Cl/Cd_max)",
    )
    p.add_argument(
        "--csv",
        help="CSV file path to export results (extract or limits)",
    )
    p.add_argument(
        "--list-re",
        action="store_true",
        help="List available Re values in polars",
    )
    args = p.parse_args()

    if args.list_re:
        vals = list_available_re(args.polars_dir)
        print("Available Reynolds (appearing in file names):")
        for v in vals:
            print(" -", v)
        return

    profiles = _parse_csv_list(args.profiles)
    alphas = _parse_alphas(args.alphas)

    if args.action == "plot":
        from plot_polars import plot_polars

        plot_polars(
            polars_dir=args.polars_dir,
            profiles=profiles,
            re_filter=args.re,
            out_path=args.out,
        )

    elif args.action == "extract":
        if not alphas:
            print("Error: must specify --alphas for extract")
            return
        from extract_limits import extract_values
        import pandas as pd

        res = extract_values(
            polars_dir=args.polars_dir,
            profiles=profiles,
            re_filter=args.re,
            alphas=alphas,
        )

        # Convert to DataFrame for easier CSV export
        rows = []
        for profile_name, data in res.items():
            for alpha_key, values in data.items():
                row = {
                    "Profile": profile_name,
                    "Alpha_target": alpha_key.replace("alpha_", ""),
                }
                row.update(values)
                rows.append(row)

        df_extract = pd.DataFrame(rows)

        if args.csv:
            df_extract.to_csv(args.csv, index=False, encoding="utf-8-sig")
            print(f"Data exported to {args.csv}")
        else:
            import json

            print(json.dumps(res, indent=2, ensure_ascii=False))

    elif args.action == "limits":
        from extract_limits import extract_limits

        df = extract_limits(
            polars_dir=args.polars_dir,
            profiles=profiles,
            re_filter=args.re,
        )

        # Apply sorting if requested
        if args.sort:
            sort_col = args.sort
            ascending = True
            if sort_col.startswith("-"):
                ascending = False
                sort_col = sort_col[1:]

            if sort_col in df.columns:
                df = df.sort_values(by=sort_col, ascending=ascending)
            else:
                print(
                    f"Warning: Column '{sort_col}' not found. Available columns: {', '.join(df.columns)}"
                )

        if args.csv:
            df.to_csv(args.csv, index=False, encoding="utf-8-sig")
            print(f"Data exported to {args.csv}")
        else:
            print(df.to_string(index=False))


if __name__ == "__main__":
    main()
