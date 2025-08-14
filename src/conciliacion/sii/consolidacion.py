from __future__ import annotations
from pathlib import Path
import pandas as pd
from typing import Iterable

# --- Utilidades internas -----------------------------------------------------

def _cargar_encabezados(path_encabezados: str, tipo: str) -> list[str]:
    hoja = "Libro de Compra" if tipo.lower() == "compra" else "Libro Venta"
    cols = pd.read_excel(path_encabezados, sheet_name=hoja).columns.tolist()
    return [str(c).strip() for c in cols]

def _limpiar_duplicado_encabezado(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    primera_fila = df.iloc[0].astype(str).str.strip().tolist()
    cols = [str(c).strip() for c in df.columns]
    if primera_fila == cols:
        df = df.iloc[1:].reset_index(drop=True)
    return df

def _corregir_desplazamiento(df: pd.DataFrame) -> pd.DataFrame:
    if df.shape[1] < 2 or df.shape[0] < 3:
        return df
    first, second = df.columns[:2]
    body = df.iloc[1:]
    try:
        desplazadas = body[first].isna() & body[second].notna()
        if desplazadas.mean() > 0.8:
            df.iloc[1:] = body.shift(-1, axis=1)
    except Exception:
        pass
    return df

def _convertir_numericos(df: pd.DataFrame, columnas: Iterable[str]) -> pd.DataFrame:
    # Convierte solo columnas que vienen en encabezados y existen en df
    for col in columnas:
        if col not in df.columns:
            continue
        s = df[col]
        if s.dtype == object:
            s2 = (
                s.astype(str)
                 .str.replace(r"\.", "", regex=True)
                 .str.replace(",", ".", regex=False)
            )
            df[col] = pd.to_numeric(s2, errors="ignore")
    return df

def _leer_csv_inteligente(path: Path) -> pd.DataFrame:
    # Intenta detectar separador y encoding común en archivos SII
    seps = [";", ","]
    encs = ["latin-1", "utf-8-sig", "cp1252"]
    for enc in encs:
        for sep in seps:
            try:
                df = pd.read_csv(path, sep=sep, encoding=enc, dtype=str)
                if df.shape[1] >= 2:
                    return df
            except Exception:
                continue
    # último intento con el motor de Python autodetectando
    try:
        return pd.read_csv(path, sep=None, engine="python", dtype=str)
    except Exception as e:
        raise RuntimeError(f"no se pudo leer {path.name}: {e}")

# --- Función pública ---------------------------------------------------------

def consolidar_libros_por_rut(base_dir: str, rut: str, tipo: str, path_encabezados: str, salida_xlsx: str) -> None:
    carpeta = Path(base_dir) / f"SII_{rut}" / ("RCV_Venta" if tipo.lower() == "venta" else "RCV_Compra")
    if not carpeta.exists():
        print(f"⚠️ Carpeta no encontrada: {carpeta}")
        return

    try:
        encabezados = _cargar_encabezados(path_encabezados, tipo)
    except Exception as e:
        print(f"❌ Error cargando encabezados desde {path_encabezados}: {e}")
        return

    frames: list[pd.DataFrame] = []
    archivos = sorted(carpeta.glob("*.csv"))
    if not archivos:
        print(f"⚠️ Sin CSV en {carpeta}")
        return

    for f in archivos:
        try:
            df = _leer_csv_inteligente(f)
            df.columns = [str(c).strip() for c in df.columns]
            df = _limpiar_duplicado_encabezado(df)
            df = _corregir_desplazamiento(df)

            # Mantén solo columnas esperadas (en el orden del encabezado)
            cols_presentes = [c for c in encabezados if c in df.columns]
            if not cols_presentes:
                print(f"⚠️ {f.name}: ninguna columna esperada coincide; se omite")
                continue

            df = df[cols_presentes].copy()
            df = _convertir_numericos(df, cols_presentes)

            df["Archivo.Origen"] = f.name
            frames.append(df.reset_index(drop=True))
        except Exception as e:
            print(f"❌ Error en {f.name}: {e}")

    if frames:
        out = pd.concat(frames, ignore_index=True)
        out_path = Path(salida_xlsx)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out.to_excel(out_path, index=False)
        print(f"✅ Consolidado: {out_path.name} ({len(out):,} filas)")
    else:
        print(f"⚠️ Sin archivos válidos en {carpeta}")
