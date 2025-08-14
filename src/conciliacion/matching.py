
from __future__ import annotations
import pandas as pd

def conciliar(df_banco: pd.DataFrame, df_libro: pd.DataFrame, tol_abs: float = 0.0) -> pd.DataFrame:
    b = df_banco.copy()
    l = df_libro.copy()
    b["key"] = b["fecha"].dt.date.astype("string") + "|" + b["monto"].round(2).astype("string")
    l["key"] = l["fecha"].dt.date.astype("string") + "|" + l["monto"].round(2).astype("string")
    merged = b.merge(l, on="key", how="outer", suffixes=("_banco", "_libro"), indicator=True)
    merged["match"] = merged["_merge"].eq("both")
    return merged.drop(columns=["_merge", "key"])
