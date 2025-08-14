
from __future__ import annotations
from pathlib import Path
import pandas as pd

def generar_reporte(conciliado: pd.DataFrame, salida: str | Path) -> None:
    p = Path(salida)
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.suffix.lower() == ".xlsx":
        conciliado.to_excel(p, index=False)
    elif p.suffix.lower() == ".csv":
        conciliado.to_csv(p, index=False)
    else:
        raise ValueError("Extensión no soportada. Usa .xlsx o .csv")
