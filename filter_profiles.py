import pandas as pd

from extract_limits import extract_limits

# Column aliases for easier filtering (without special characters, all lowercase)
COLUMN_ALIASES = {
    # Lift slope aliases
    "cl_alpha_deg": "Cl_alpha (deg⁻¹)",
    "cl_alpha_rad": "Cl_alpha (rad⁻¹)",
    "cl_alpha": "Cl_alpha (rad⁻¹)",  # Default to radians
    # Moment coefficient
    "cm_0": "Cm_0",
    # Drag
    "cd_min": "Cd_min",
    "cd_at_cl_max": "Cd @ Cl_max",
    # Lift
    "cl_max": "Cl_max",
    "cl_i": "Cl_i",  # Simplified name for Cl_ideal (Cl @ Cd_min)
    "cl_ideal": "Cl_i",  # Alias for Cl_ideal
    # Efficiency
    "cl_cd_max": "Cl/Cd_max",
    "cl_cd_at_cli": "Cl/Cd @ Cl_i",  # Cl/Cd evaluated at Cl_ideal
    "cl_cd_cli": "Cl/Cd @ Cl_i",  # Short alias
    # Angles (all in degrees)
    "alpha_cd_min": "α @ Cd_min (deg)",
    "alpha_cl_max": "α @ Cl_max (deg)",
    "alpha_cl_cd_max": "α @ Cl/Cd_max (deg)",
}


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
            # Try to resolve alias to actual column name (case-insensitive)
            # First try exact match, then try lowercase match
            actual_param = COLUMN_ALIASES.get(param)
            if actual_param is None:
                # Try case-insensitive match
                param_lower = param.lower()
                actual_param = COLUMN_ALIASES.get(param_lower, param)

            if actual_param not in df.columns:
                # Show available aliases and columns
                available_aliases = list(COLUMN_ALIASES.keys())
                raise ValueError(
                    f"Parameter '{param}' (resolved to '{actual_param}') not found.\n"
                    f"Available short names: {', '.join(available_aliases)}\n"
                    f"Available full names: {', '.join(df.columns)}"
                )

            if operator == ">":
                df = df[df[actual_param] > value]
            elif operator == ">=":
                df = df[df[actual_param] >= value]
            elif operator == "<":
                df = df[df[actual_param] < value]
            elif operator == "<=":
                df = df[df[actual_param] <= value]
            elif operator == "==":
                df = df[df[actual_param] == value]
            elif operator == "!=":
                df = df[df[actual_param] != value]
            elif operator == "between":
                # value is a tuple (min_val, max_val)
                min_val, max_val = value
                df = df[(df[actual_param] >= min_val) & (df[actual_param] <= max_val)]
            else:
                raise ValueError(
                    f"Invalid operator '{operator}'. Use: >, >=, <, <=, ==, !=, between"
                )

    return df.reset_index(drop=True)


if __name__ == "__main__":
    # Example usage
    criteria = {"Cl/Cd_max": (">", 100), "Cd_min": ("<", 0.006)}

    result = filter_profiles(re_filter="0.688", criteria=criteria)

    print(f"\nFound {len(result)} profiles matching criteria:")
    print(result.to_string(index=False))
