
import pandas as pd
from conciliacion.normalizacion import normalizar_dataframe

def test_normalizar_mapea():
    df = pd.DataFrame({"Fecha": ["2025-08-01"], "Monto": [1000], "Glosa": ["abono"]})
    out = normalizar_dataframe(df)
    assert str(out.loc[0,"fecha"])[:10] == "2025-08-01"
    assert out.loc[0,"monto"] == 1000
