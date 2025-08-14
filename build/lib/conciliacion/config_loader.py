from pathlib import Path
import yaml

def cargar_config(path_config: str | Path) -> dict:
    """Carga la configuración YAML y devuelve un diccionario."""
    path_config = Path(path_config)
    if not path_config.exists():
        raise FileNotFoundError(f"No se encontró el archivo de configuración: {path_config}")
    with open(path_config, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config
