from __future__ import annotations
from pathlib import Path
from typing import Optional
from .common_rcv import extract_for_tipo

def run_venta(*, rut: str, clave: str,
              anho_ini: int, mes_ini: int, anho_fin: int, mes_fin: int,
              carpeta_base: Path, headless: bool,
              chrome_binary: Optional[str], chromedriver_path: Optional[str]) -> None:
    extract_for_tipo(
        rut=rut, clave=clave,
        anho_ini=anho_ini, mes_ini=mes_ini, anho_fin=anho_fin, mes_fin=mes_fin,
        tipo_up="VENTA",
        carpeta_base=carpeta_base, headless=headless,
        chrome_binary=chrome_binary, chromedriver_path=chromedriver_path
    )
