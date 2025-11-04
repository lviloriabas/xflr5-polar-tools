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

    # Count profiles for title
    num_profiles = len(files)

    # Use only solid lines for better readability
    linestyle = "-"

    # Generate colors dynamically using matplotlib colormaps
    # Use tab20 + Dark2 + Set1 for distinct, saturated colors
    # Avoids light colors like yellow that don't show well
    import matplotlib.cm as cm

    # Get qualitative colormaps with saturated colors
    tab20_cmap = cm.get_cmap("tab20")
    dark2_cmap = cm.get_cmap("Dark2")
    set1_cmap = cm.get_cmap("Set1")

    # Sample colors from each colormap
    tab20_colors = [tab20_cmap(i) for i in range(20)]
    dark2_colors = [dark2_cmap(i / 8) for i in range(8)]
    set1_colors = [set1_cmap(i / 9) for i in range(9)]

    # Combine all colors - total 37 distinct colors
    all_colors = tab20_colors + dark2_colors + set1_colors
    colors = [all_colors[i % len(all_colors)] for i in range(num_profiles)]

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

    # Add overall title with Reynolds number and profile count
    if re_display:
        fig.suptitle(
            f"Simulaciones de {num_profiles} perfiles a Re = {re_display}",
            fontsize=20,
            y=0.99,
        )
    else:
        fig.suptitle(
            f"Simulaciones de {num_profiles} perfiles",
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
    plot_polars()
