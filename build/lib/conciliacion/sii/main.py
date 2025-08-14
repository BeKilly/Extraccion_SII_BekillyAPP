#!/usr/bin/env python3
import argparse
import sys
import yaml
from pathlib import Path
from conciliacion.sii import orquestador


def main() -> int:
    parser = argparse.ArgumentParser(description="Extracción RCV SII BekillyAPP")
    parser.add_argument(
        "--config",
        default="config/sample_config.yaml",  # Valor por defecto
        help="Ruta al archivo de configuración YAML (por defecto: config/sample_config.yaml)"
    )
    parser.add_argument("--no-headless", action="store_true", help="Desactivar modo headless en Chrome")
    parser.add_argument("--rut", help="RUT específico a procesar (opcional)")
    parser.add_argument("--tipos", nargs="+", choices=["COMPRA", "VENTA"], help="Tipos a procesar (opcional)")

    args = parser.parse_args()

    # Cargar configuración desde YAML
    config_path = Path(args.config).expanduser().resolve()
    if not config_path.exists():
        print(f"[ERROR] No se encuentra el archivo de configuración: {config_path}")
        return 1

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Ejecutar orquestador con argumentos
    orquestador.run(
        config=config,
        headless=not args.no_headless,
        rut_filtro=args.rut,
        tipos_filtro=args.tipos,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
def cli_entry():
    import sys
    sys.exit(main())