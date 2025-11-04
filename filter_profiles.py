import pandas as pd

from extract_limits import extract_limits


def filter_profiles(
    polars_dir=None,
    profiles=None,
    re_filter=None,
    criteria=None,
):
    """
    Filter profiles based on performance criteria.

    Parameters:
    -----------
    polars_dir : str
        Directory containing polar files
    profiles : list
        List of profile name filters
    re_filter : str
        Reynolds number filter
    criteria : dict
        Dictionary with filtering criteria. Format:
        {
            'parameter': ('operator', value),
            ...
        }

        Available parameters:
        - Cl_alpha: Lift slope (per radian)
        - Cm_0: Moment coefficient at alpha=0
        - Cd_min: Minimum drag coefficient
        - Cl_max: Maximum lift coefficient
        - Cl/Cd_max: Maximum lift-to-drag ratio

        Available operators:
        - '>': greater than
        - '>=': greater than or equal
        - '<': less than
        - '<=': less than or equal
        - '==': equal to
        - '!=': not equal to

    Returns:
    --------
    pd.DataFrame
        Filtered profiles with their characteristics

    Examples:
    ---------
    # Find profiles with Cl/Cd_max > 100 and Cd_min < 0.006
    criteria = {
        'Cl/Cd_max': ('>', 100),
        'Cd_min': ('<', 0.006)
    }

    # Find profiles with high lift slope and low moment
    criteria = {
        'Cl_alpha': ('>', 7.0),
        'Cm_0': ('<', -0.02)
    }
    """
    # Extract all limits data
    df = extract_limits(
        polars_dir=polars_dir,
        profiles=profiles,
        re_filter=re_filter,
    )

    if df.empty:
        return df

    # Apply filtering criteria
    if criteria:
        for param, (operator, value) in criteria.items():
            if param not in df.columns:
                raise ValueError(
                    f"Parameter '{param}' not found. Available: {', '.join(df.columns)}"
                )

            if operator == ">":
                df = df[df[param] > value]
            elif operator == ">=":
                df = df[df[param] >= value]
            elif operator == "<":
                df = df[df[param] < value]
            elif operator == "<=":
                df = df[df[param] <= value]
            elif operator == "==":
                df = df[df[param] == value]
            elif operator == "!=":
                df = df[df[param] != value]
            else:
                raise ValueError(
                    f"Invalid operator '{operator}'. Use: >, >=, <, <=, ==, !="
                )

    return df.reset_index(drop=True)


if __name__ == "__main__":
    # Example usage
    criteria = {"Cl/Cd_max": (">", 100), "Cd_min": ("<", 0.006)}

    result = filter_profiles(re_filter="0.688", criteria=criteria)

    print(f"\nFound {len(result)} profiles matching criteria:")
    print(result.to_string(index=False))
