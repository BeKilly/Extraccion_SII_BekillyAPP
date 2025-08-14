
from __future__ import annotations
import pandas as pd

DEFAULT_MAPPING = {
    "fecha": ["fecha", "Fecha", "date", "transaction_date"],
    "monto": ["monto", "Monto", "amount", "importe"],
    "glosa": ["glosa", "Glosa", "description", "detalle", "Descripción"],
    "referencia": ["referencia", "Ref", "doc", "Documento"],
}

def _first_existing(df: pd.DataFrame, candidates: list[str]) -> str | None:
    lower = {c.lower(): c for c in df.columns}
    for alias in candidates:
        if alias.lower() in lower:
            return lower[alias.lower()]
    return None

def normalizar_dataframe(df: pd.DataFrame, mapping: dict[str, list[str]] | None = None) -> pd.DataFrame:
    mapping = mapping or DEFAULT_MAPPING
    out = pd.DataFrame()
    for std_col, aliases in mapping.items():
        col = _first_existing(df, aliases)
        out[std_col] = df[col] if col else pd.NA
    out["fecha"] = pd.to_datetime(out["fecha"], errors="coerce")
    out["monto"] = pd.to_numeric(out["monto"], errors="coerce")
    out["glosa"] = out["glosa"].astype("string")
    out["referencia"] = out["referencia"].astype("string")
    return out
