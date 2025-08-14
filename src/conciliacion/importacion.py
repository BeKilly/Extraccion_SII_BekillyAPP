
from __future__ import annotations
from pathlib import Path
import pandas as pd

def cargar(path: str | Path) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"No existe archivo: {p}")
    if p.suffix.lower() == ".csv":
        return pd.read_csv(p)
    if p.suffix.lower() in {".xls", ".xlsx"}:
        return pd.read_excel(p)
    raise ValueError(f"Formato no soportado: {p.suffix}")
