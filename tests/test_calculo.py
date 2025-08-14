
import pandas as pd
from conciliacion.sii.calculo import calcular_efecto_neto

def test_calculo_basico():
    df = pd.DataFrame({
        "Monto Exento": [0, 0],
        "Monto Neto": [1000, 1000],
        "Tipo Doc": ["33", "61"],
    })
    out = calcular_efecto_neto(df)
    assert list(out["Total Neto"]) == [1000, 1000]
    assert list(out["Efecto Neto"]) == [1000, -1000]
