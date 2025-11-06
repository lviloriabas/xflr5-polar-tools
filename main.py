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


def _parse_filter_criteria(filter_list):
    """
    Parse filter criteria from command line arguments.

    Supports:
    - Standard operators: >, >=, <, <=, ==, !=
    - Between operator: "param between min,max"

    Returns:
    - criteria: dict with parsed criteria
    - display: dict for display purposes (keeps original format)
    """
    if not filter_list:
        return None, None

    criteria = {}
    display = {}
    operators = {">", ">=", "<", "<=", "==", "!="}

    for criterion in filter_list:
        parsed = False

        # Check for "between" operator
        if " between " in criterion.lower():
            parts = criterion.lower().split(" between ")
            if len(parts) == 2:
                param = parts[0].strip()
                try:
                    values = parts[1].strip().split(",")
                    if len(values) == 2:
                        min_val = float(values[0].strip())
                        max_val = float(values[1].strip())
                        criteria[param] = ("between", (min_val, max_val))
                        display[param] = ("between", (min_val, max_val))
                        parsed = True
                except ValueError:
                    pass

        # Check for standard operators
        if not parsed:
            for op in sorted(operators, key=len, reverse=True):
                if op in criterion:
                    parts = criterion.split(op, 1)
                    if len(parts) == 2:
                        param = parts[0].strip()
                        try:
                            value = float(parts[1].strip())
                            criteria[param] = (op, value)
                            display[param] = (op, value)
                            parsed = True
                            break
                        except ValueError:
                            continue

        if not parsed:
            print(f"Warning: Could not parse criterion: {criterion}")
            print("Format: 'parameter operator value' or 'parameter between min,max'")

    return criteria if criteria else None, display if display else None


def main():
    p = argparse.ArgumentParser(description="Tools for XFLR5 polar analysis")
    p.add_argument(
        "action",
        choices=["plot", "extract", "limits", "plot-clmax-cli"],
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
        help="Filter criteria (available for all actions). Format: 'parameter operator value' "
        "(e.g., 'Cl/Cd_max > 100' or 'Cd_min < 0.006' or 'cl_i between 0.3,0.8'). Can be used multiple times.",
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

        # Parse filter criteria if provided
        filter_criteria, filter_display = _parse_filter_criteria(args.filter)

        plot_polars(
            polars_dir=args.polars_dir,
            profiles=profiles,
            re_filter=args.re,
            out_path=args.out,
            filter_criteria=filter_criteria,
            filter_display=filter_display,
        )

    elif args.action == "plot-clmax-cli":
        from plot_polars import plot_clmax_vs_clideal

        # Parse filter criteria if provided
        filter_criteria, filter_display = _parse_filter_criteria(args.filter)

        plot_clmax_vs_clideal(
            polars_dir=args.polars_dir,
            profiles=profiles,
            re_filter=args.re,
            out_path=args.out,
            filter_criteria=filter_criteria,
            filter_display=filter_display,
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

        # Apply filters if provided
        if args.filter:
            filter_criteria, _ = _parse_filter_criteria(args.filter)
            if filter_criteria:
                # Apply filters
                filtered_df = filter_profiles(
                    polars_dir=args.polars_dir,
                    profiles=profiles,
                    re_filter=args.re,
                    criteria=filter_criteria,
                )
                # Keep only profiles that passed the filter
                filtered_profiles = set(filtered_df["Profile"].values)
                df_extract = df_extract[df_extract["Profile"].isin(filtered_profiles)]

                if df_extract.empty:
                    print("No profiles match the specified criteria.")
                    return
                print(
                    f"Filtered to {len(filtered_profiles)} profile(s) matching criteria"
                )

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

        # Apply filters if provided
        if args.filter:
            filter_criteria, _ = _parse_filter_criteria(args.filter)
            if filter_criteria:
                print(f"Applying filters: {filter_criteria}")
                df = filter_profiles(
                    polars_dir=args.polars_dir,
                    profiles=profiles,
                    re_filter=args.re,
                    criteria=filter_criteria,
                )

                if df.empty:
                    print("No profiles match the specified criteria.")
                    return
                print(f"Found {len(df)} matching profile(s)")

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
