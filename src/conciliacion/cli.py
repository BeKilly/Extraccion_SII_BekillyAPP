
from __future__ import annotations
import argparse
import os
import sys
from pathlib import Path

import pandas as pd
import yaml

from conciliacion.sii import extraer_rcv_tipo, consolidar_libros_por_rut, calcular_efecto_neto


def _resolve_path(value: str | None, fallback_env: str | None = None) -> Path | None:
    if value is None:
        if fallback_env and os.getenv(fallback_env):
            return Path(os.getenv(fallback_env))
        return None
    # Expande variables de entorno y ~
    return Path(os.path.expandvars(os.path.expanduser(value)))


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="conciliacion",
        description="Pipeline SII: extracción -> consolidación -> cálculo",
    )
    ap.add_argument("--config", required=True, help="Ruta a YAML de configuración")
    ap.add_argument(
        "--headless",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Forzar modo headless (usa --headless para activar, --no-headless para desactivar). Por defecto toma el YAML.",
    )
    ap.add_argument(
        "--chrome-binary",
        default=None,
        help="Ruta al binario de Google Chrome/Chromium. Si no se indica, usa el del sistema/imagen.",
    )
    ap.add_argument(
        "--chromedriver",
        default=None,
        help="Ruta a chromedriver. Si no se indica, se asume en PATH.",
    )
    return ap


def main(argv=None) -> int:
    ap = build_parser()
    args = ap.parse_args(argv)

    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))

    # Rutas base desde YAML con fallback a variables de entorno si existen
    base_dir = _resolve_path(cfg.get("base_dir"), "BEKILLY_BASE_DIR")
    if base_dir is None:
        # último fallback: workspace actual
        base_dir = Path.cwd()

    encabezados = _resolve_path(cfg.get("encabezados_xlsx"), "BEKILLY_CONFIG_DIR")
    if encabezados and encabezados.is_dir():
        # si apuntaron a carpeta, asume nombre por defecto
        encabezados = encabezados / "Encabezados.xlsx"

    # Chrome/Driver
    chrome_binary = args.chrome_binary or cfg.get("chrome_binary")
    chromedriver = args.chromedriver or cfg.get("chromedriver_path") or "chromedriver"

    # Headless: CLI tiene prioridad; si no se pasa, usa YAML; si no, True por defecto
    headless_cfg = cfg.get("headless")
    headless = args.headless if args.headless is not None else (True if headless_cfg is None else bool(headless_cfg))

    period = cfg["periodo"]
    clientes = cfg["clientes"]  # lista de objetos con rut, clave, anho_inicio, etc.

    ejecutar_extraccion = bool(cfg.get("ejecutar_extraccion", True))

    for c in clientes:
        rut = str(c["rut"]).strip()
        print(f"\n=== Cliente: {rut} ===")

        try:
            # Extracción
            if ejecutar_extraccion:
                for tipo in ("venta", "compra"):
                    print(f"[Extracción] {tipo} (headless={headless})...")
                    extraer_rcv_tipo(
                        rut=rut,
                        clave=c["clave"],
                        anho_ini=period["anho_inicio"],
                        mes_ini=period["mes_inicio"],
                        anho_fin=period["anho_fin"],
                        mes_fin=period["mes_fin"],
                        tipo=tipo,
                        chromedriver_path=str(chromedriver) if chromedriver else None,
                        carpeta_base=str(base_dir),
                        headless=headless,              # <- NUEVO: se espera que el driver use --headless=new
                        chrome_binary=chrome_binary,    # <- opcional: ruta a chrome
                    )

            # Consolidación
            for tipo in ("venta", "compra"):
                out_name = f"Consolidado_{'Venta' if tipo=='venta' else 'Compra'} - {rut}.xlsx"
                salida = base_dir / f"SII_{rut}" / out_name
                print(f"[Consolidación] {tipo} -> {salida.name}")
                consolidar_libros_por_rut(str(base_dir), rut, tipo, str(encabezados), str(salida))

                # Cálculo
                if salida.exists():
                    print(f"[Cálculo] {tipo}...")
                    df = pd.read_excel(salida)
                    df_calc = calcular_efecto_neto(df)
                    salida_calc = salida.with_name(salida.stem.replace("Consolidado", "Calculado") + salida.suffix)
                    df_calc.to_excel(salida_calc, index=False)
                    print(f"[OK] {salida_calc.name}")
                else:
                    print(f"[Aviso] No existe {salida.name}; se omite cálculo de {tipo}")

        except KeyboardInterrupt:
            print("Interrumpido por el usuario.")
            return 130
        except Exception as e:
            print(f"[Error] Cliente {rut}: {e}")
            # continúa con el siguiente cliente
            continue

    return 0


if __name__ == "__main__":
    sys.exit(main())
