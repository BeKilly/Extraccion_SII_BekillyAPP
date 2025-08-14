from __future__ import annotations
import pandas as pd
from typing import Iterable


def _to_number(s: pd.Series) -> pd.Series:
    """Convierte serie a numérico tolerando miles '.' y decimales ','."""
    if not pd.api.types.is_string_dtype(s):
        return pd.to_numeric(s, errors="coerce").fillna(0)
    s2 = (
        s.astype(str)
         .str.replace(r"\.", "", regex=True)  # quita miles
         .str.replace(",", ".", regex=False)  # decimales
    )
    return pd.to_numeric(s2, errors="coerce").fillna(0)


def calcular_efecto_neto(
    df: pd.DataFrame,
    *,
    col_monto_exento: str = "Monto Exento",
    col_monto_neto: str = "Monto Neto",
    col_tipo_doc: str = "Tipo Doc",
    notas_credito: Iterable[str] = ("61",),   # Tipos que invierten signo
) -> pd.DataFrame:
    """
    Calcula columnas:
      - Total Neto = Monto Exento + Monto Neto
      - Signo Doc  = -1 si Tipo Doc ∈ notas_credito, si no 1
      - Efecto Neto = Total Neto * Signo Doc
    """
    faltantes = [c for c in (col_monto_exento, col_monto_neto, col_tipo_doc) if c not in df.columns]
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas: {', '.join(faltantes)}")

    out = df.copy()

    # Normaliza numéricos
    out[col_monto_exento] = _to_number(out[col_monto_exento])
    out[col_monto_neto]   = _to_number(out[col_monto_neto])

    # Total Neto
    out["Total Neto"] = out[col_monto_exento] + out[col_monto_neto]

    # Signo por tipo de documento (p.ej. 61 = Nota de Crédito)
    tipo = out[col_tipo_doc].astype(str).str.strip()
    mask_nc = tipo.isin(set(str(x).strip() for x in notas_credito))
    out["Signo Doc"] = 1
    out.loc[mask_nc, "Signo Doc"] = -1

    # Efecto Neto (con signo)
    out["Efecto Neto"] = out["Total Neto"] * out["Signo Doc"]

    return out
