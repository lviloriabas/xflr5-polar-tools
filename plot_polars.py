import matplotlib.pyplot as plt
from polars_reader import list_polar_files, parse_polar_file


def _match_re(filename, target_re):
    if target_re is None:
        return True
    # target_re provided as string like '0.100' or '0.100e6' or '100000'
    s = str(filename)
    return target_re in s


def plot_polars(
    polars_dir=None,
    profiles=None,
    re_filter=None,
    out_path=None,
    figsize=(16, 12),
):
    files = list_polar_files(polars_dir)
    # filter by profiles list if provided (list of names or substrings)
    if profiles:
        procs = []
        for p in profiles:
            for f in files:
                if p in f.name:
                    procs.append(f)
        files = sorted(set(procs), key=lambda p: p.name)
    # filter by re
    re_value = None
    re_display = None
    if re_filter:
        files = [f for f in files if re_filter in f.name]
        # Extract Re value for title and convert to actual Reynolds number
        re_value = re_filter
        try:
            # Convert string like "0.688" to actual Re number (688000)
            re_float = float(re_value)
            re_actual = int(re_float * 1e6)
            re_display = f"{re_actual:,}".replace(",", " ")
        except ValueError:
            re_display = re_value
    if not files:
        raise RuntimeError("No polar files matched selection")

    fig, axs = plt.subplots(2, 2, figsize=figsize)
    ax1, ax2, ax3, ax4 = axs.flatten()

    # Use only solid lines for better readability
    linestyle = "-"

    # Organized to maximize visual distinction between adjacent colors
    colors = [
        "#1f77b4",
        "#ff7f0e",
        "#2ca02c",
        "#d62728",
        "#9467bd",
        "#8c564b",
        "#e377c2",
        "#bcbd22",
        "#17becf",
        "#aec7e8",
        "#0000ff",
        "#ff0000",
        "#00ff00",
        "#ff00ff",
        "#00ffff",
        "#800000",
        "#008000",
        "#000080",
        "#800080",
        "#008080",
        "#c71585",
        "#ff4500",
        "#32cd32",
        "#4169e1",
        "#ff1493",
        "#00ced1",
        "#ff8c00",
        "#9400d3",
        "#00fa9a",
        "#dc143c",
        "#1e90ff",
        "#ffd700",
        "#adff2f",
        "#ff69b4",
        "#00bfff",
        "#ff6347",
        "#7b68ee",
        "#00ff7f",
        "#ff00bf",
        "#20b2aa",
        "#b22222",
        "#228b22",
        "#4682b4",
        "#d2691e",
        "#6a5acd",
        "#db7093",
        "#ff8c69",
        "#7fff00",
        "#6495ed",
        "#dc1485",
        "#3cb371",
        "#8b008b",
        "#cd5c5c",
        "#4b0082",
        "#f08080",
        "#2e8b57",
        "#ba55d3",
        "#cd853f",
        "#bc8f8f",
        "#4169e1",
        "#da70d6",
        "#b8860b",
        "#ee82ee",
        "#d2b48c",
        "#9370db",
        "#f4a460",
        "#dda0dd",
        "#bdb76b",
        "#8a2be2",
        "#ff7f50",
        "#9932cc",
        "#ffa07a",
        "#8b4513",
        "#fa8072",
        "#a0522d",
        "#ff6eb4",
        "#556b2f",
        "#ff1c8d",
        "#6b8e23",
        "#c0c0c0",
        "#e9967a",
        "#8fbc8f",
        "#f5deb3",
        "#48d1cc",
        "#c0d9af",
    ]

    for i, f in enumerate(files):
        parsed = parse_polar_file(f)
        df = parsed["df"]
        # Only use profile name in legend, no Reynolds
        label = parsed["name"]
        if df is None or df.empty:
            continue

        # Cycle through colors only (solid lines for all)
        color = colors[i % len(colors)]

        # Plot with solid lines, no markers
        ax1.plot(
            df["alpha"],
            df["CL"],
            label=label,
            color=color,
            linestyle=linestyle,
            linewidth=2.5,
        )
        ax2.plot(
            df["alpha"],
            df["Cm"],
            label=label,
            color=color,
            linestyle=linestyle,
            linewidth=2.5,
        )
        ax3.plot(
            df["CL"],
            df["CD"],
            label=label,
            color=color,
            linestyle=linestyle,
            linewidth=2.5,
        )
        ax4.plot(
            df["alpha"],
            df["Cl_Cd"],
            label=label,
            color=color,
            linestyle=linestyle,
            linewidth=2.5,
        )

    # Use Greek alpha symbol and subscripts for coefficients
    ax1.set_xlabel(r"$\alpha$ (deg)", fontsize=18)
    ax1.set_ylabel(r"$C_l$", fontsize=18)
    ax1.tick_params(axis="both", labelsize=16)
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=0, color="gray", linewidth=1.0, alpha=0.6, zorder=1)
    ax1.axvline(x=0, color="gray", linewidth=1.0, alpha=0.6, zorder=1)

    ax2.set_xlabel(r"$\alpha$ (deg)", fontsize=18)
    ax2.set_ylabel(r"$C_m$", fontsize=18)
    ax2.tick_params(axis="both", labelsize=16)
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=0, color="gray", linewidth=1.0, alpha=0.6, zorder=1)
    ax2.axvline(x=0, color="gray", linewidth=1.0, alpha=0.6, zorder=1)

    ax3.set_xlabel(r"$C_l$", fontsize=18)
    ax3.set_ylabel(r"$C_d$", fontsize=18)
    ax3.tick_params(axis="both", labelsize=16)
    ax3.grid(True, alpha=0.3)
    ax3.axhline(y=0, color="gray", linewidth=1.0, alpha=0.6, zorder=1)
    ax3.axvline(x=0, color="gray", linewidth=1.0, alpha=0.6, zorder=1)

    ax4.set_xlabel(r"$\alpha$ (deg)", fontsize=18)
    ax4.set_ylabel(r"$C_l/C_d$", fontsize=18)
    ax4.tick_params(axis="both", labelsize=16)
    ax4.grid(True, alpha=0.3)
    ax4.axhline(y=0, color="gray", linewidth=1.0, alpha=0.6, zorder=1)
    ax4.axvline(x=0, color="gray", linewidth=1.0, alpha=0.6, zorder=1)

    # Add overall title with Reynolds number if available
    if re_display:
        fig.suptitle(
            f"Simulaciones de perfiles a Re = {re_display}",
            fontsize=20,
            y=0.99,
        )

    # Add legend outside the plot area on the right
    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="center left",
        bbox_to_anchor=(0.91, 0.5),
        fontsize=13,
    )

    # Adjust layout to maximize plot area while keeping space for legend
    fig.tight_layout(rect=[0, 0, 0.90, 0.97])
    if out_path:
        fig.savefig(out_path, dpi=300, bbox_inches="tight")
        print("Saved figure to", out_path)
    else:
        plt.show()


if __name__ == "__main__":
    # quick manual demo when running module directly
    plot_polars()
