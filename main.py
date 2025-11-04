import argparse
from pathlib import Path

from filter_profiles import filter_profiles
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
        choices=["plot", "extract", "limits", "filter", "plot-clmax-cli"],
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
        "--filter",
        "-f",
        action="append",
        help="Filter criteria for 'filter' action. Format: 'parameter operator value' "
        "(e.g., 'Cl/Cd_max > 100' or 'Cd_min < 0.006'). Can be used multiple times.",
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

    elif args.action == "plot-clmax-cli":
        from plot_polars import plot_clmax_vs_clideal

        plot_clmax_vs_clideal(
            polars_dir=args.polars_dir,
            profiles=profiles,
            re_filter=args.re,
            out_path=args.out,
        )

    elif args.action == "extract":
        if not alphas:
            print("Error: must specify --alphas for extract")
            return
        import pandas as pd

        from extract_limits import extract_values

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

    elif args.action == "filter":
        if not args.filter:
            print("Error: --filter criteria required for 'filter' action.")
            print("Example: --filter 'Cl/Cd_max > 100' --filter 'Cd_min < 0.006'")
            return

        # Parse filter criteria
        criteria = {}
        operators = {">", ">=", "<", "<=", "==", "!="}
        for criterion in args.filter:
            # Try to parse: "parameter operator value"
            parsed = False
            for op in sorted(operators, key=len, reverse=True):  # Check >= before >
                if op in criterion:
                    parts = criterion.split(op, 1)
                    if len(parts) == 2:
                        param = parts[0].strip()
                        try:
                            value = float(parts[1].strip())
                            criteria[param] = (op, value)
                            parsed = True
                            break
                        except ValueError:
                            continue
            if not parsed:
                print(f"Warning: Could not parse criterion: {criterion}")
                print(
                    "Format should be: 'parameter operator value' (e.g., 'Cl/Cd_max > 100')"
                )

        if not criteria:
            print("Error: No valid filter criteria parsed.")
            return

        print(f"Filtering with criteria: {criteria}")
        filtered_df = filter_profiles(args.polars_dir, profiles, args.re, criteria)

        if filtered_df.empty:
            print("No profiles match the specified criteria.")
            return

        print(f"\nFound {len(filtered_df)} matching profile(s):")

        # Apply sorting if requested
        if args.sort:
            sort_col = args.sort
            ascending = True
            if sort_col.startswith("-"):
                ascending = False
                sort_col = sort_col[1:]

            if sort_col in filtered_df.columns:
                filtered_df = filtered_df.sort_values(by=sort_col, ascending=ascending)
            else:
                print(
                    f"Warning: Column '{sort_col}' not found. Available columns: {', '.join(filtered_df.columns)}"
                )

        if args.csv:
            filtered_df.to_csv(args.csv, index=False, encoding="utf-8-sig")
            print(f"Results exported to: {args.csv}")
        else:
            print(filtered_df.to_string(index=False))


if __name__ == "__main__":
    main()
