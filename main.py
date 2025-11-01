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
    p = argparse.ArgumentParser(
        description="Herramientas para análisis de polares XFLR5"
    )
    p.add_argument(
        "action",
        choices=["plot", "extract", "limits"],
        help="Funcionalidad a ejecutar",
    )
    p.add_argument(
        "--profiles",
        "-p",
        help="Perfiles a incluir (coma-separados, substring del nombre). Default: todos",
    )
    p.add_argument(
        "--re",
        help="Filtro de Reynolds (ej: 0.100 ó Re0.100). Si no se especifica usa todos",
    )
    p.add_argument(
        "--polars-dir",
        default=str(Path(__file__).parent / "polars"),
        help="Directorio de polars",
    )
    p.add_argument("--out", "-o", help="Ruta de salida para figuras (plot)")
    p.add_argument(
        "--alphas",
        help="Lista de alpha para extracción en 'extract' (comma-separated)",
    )
    p.add_argument(
        "--sort",
        help="Ordenar tabla de limits por columna (ej: Cd_min, Cl_max, Cl/Cd_max). Use '-' para descendente (ej: -Cl/Cd_max)",
    )
    p.add_argument(
        "--list-re",
        action="store_true",
        help="Listar valores de Re disponibles en polars",
    )
    args = p.parse_args()

    if args.list_re:
        vals = list_available_re(args.polars_dir)
        print("Reynolds disponibles (aparecen en nombres de archivo):")
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
            print("Error: debe especificar --alphas para extract")
            return
        from extract_limites import extract_values

        res = extract_values(
            polars_dir=args.polars_dir,
            profiles=profiles,
            re_filter=args.re,
            alphas=alphas,
        )
        import json

        print(json.dumps(res, indent=2, ensure_ascii=False))

    elif args.action == "limits":
        from extract_limites import extract_limits

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

        print(df.to_string(index=False))


if __name__ == "__main__":
    main()
