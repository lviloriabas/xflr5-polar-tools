# Resumen

Colección de scripts para análisis de polares XFLR5.

Archivos principales

- `polars_reader.py` : lectura y parsing de archivos en `polars/`.
- `plot_polars.py` : genera una figura con 4 subplots (Cl vs alpha, Cm vs alpha, Cd vs Cl, Cl/Cd vs alpha).
- `extract_extrema.py` : extrae mínimos y máximos por columna y valores cercanos a alfas pedidos.
- `main.py` : CLI que permite ejecutar las funcionalidades.

## Instalación

Crear un entorno e instalar dependencias:

```powershell
python -m pip install -r requirements.txt
```

## Uso básico

### Listar los Reynolds disponibles:

```powershell
python main.py plot --list-re
```

### Graficar polares

**Ejemplo 1**: Graficar todos los perfiles a Re = 0.100

```powershell
python main.py plot --re 0.100 --out polars_plot.png
```

**Ejemplo 2**: Graficar solo perfiles específicos (NACA y CLARK YS) a Re = 0.100

```powershell
python main.py plot --re 0.100 --profiles "NACA,CLARK YS" --out polares_seleccionados.png
```

**Ejemplo 3**: Graficar solo perfiles MH a Re = 0.500

```powershell
python main.py plot --re 0.500 --profiles "MH" --out polares_mh.png
```

**Nota sobre selección de perfiles**: El parámetro `--profiles` acepta una lista separada por comas de nombres o subcadenas. El script buscará todos los archivos que contengan alguna de esas cadenas en su nombre. Por ejemplo:

- `--profiles "NACA"` incluirá todos los perfiles NACA (NACA 0015, NACA 4408, etc.)
- `--profiles "MH 16,MH 17"` incluirá solo MH 16 y MH 17
- Sin especificar `--profiles` se grafican todos los perfiles disponibles

### Extraer datos extremos

Ejemplo: extraer mínimos/máximos y valores en alpha específicos

```powershell
python main.py extract --re 0.100 --alphas 0,5,10
```

## Notas

- El parser intenta extraer las columnas `alpha`, `CL`, `CD`, `Cm` de los archivos de XFLR5.
- Si algún archivo no se puede parsear correctamente será ignorado con un aviso.
- Los filtros de Re funcionan buscando la cadena provista en el nombre del archivo (por ejemplo `0.100` coincide con archivos que contienen `Re0.100`).
