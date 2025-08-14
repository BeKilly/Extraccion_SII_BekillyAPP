from __future__ import annotations
from pathlib import Path, PureWindowsPath
from typing import Any, Dict, List, Optional, Tuple
import yaml

# Importes relativos a la carpeta "extraccion"
from .extraccion.extract_venta import run_venta
from .extraccion.extract_compra import run_compra


# ---------------- helpers de tipos / rango ----------------
def _normalize_tipos(items: Optional[List[str]]) -> List[str]:
    if not items:
        return ["VENTA", "COMPRA"]
    out, seen = [], set()
    for raw in items:
        k = str(raw).strip().lower()
        v = "VENTA" if k.startswith("vent") else "COMPRA"
        if v not in seen:
            seen.add(v); out.append(v)
    return out

def _validate_and_fix_range(anho_ini: int, mes_ini: int, anho_fin: int, mes_fin: int) -> Tuple[int,int,int,int]:
    if not (1 <= mes_ini <= 12 and 1 <= mes_fin <= 12):
        raise ValueError("Mes fuera de rango (1..12)")
    if (anho_ini, mes_ini) > (anho_fin, mes_fin):
        anho_ini, mes_ini, anho_fin, mes_fin = anho_fin, mes_fin, anho_ini, mes_ini
    return anho_ini, mes_ini, anho_fin, mes_fin

def _select_clientes(cfg: Dict[str, Any], rut_filtro: Optional[str]) -> List[Dict[str, str]]:
    if cfg.get("clientes"):
        base = [{"rut": str(c["rut"]).strip(), "clave": str(c["clave"]).strip()} for c in cfg["clientes"]]
    else:
        cred = cfg.get("credenciales", {}) or {}
        base = [{"rut": str(cred.get("rut", "")).strip(), "clave": str(cred.get("clave", "")).strip()}]
    if rut_filtro:
        clean = rut_filtro.replace(".", "").replace("-", "")
        base = [c for c in base if c["rut"].replace(".", "").replace("-", "") == clean]
    return [c for c in base if c["rut"] and c["clave"]]


# ---------------- helpers de rutas (Windows -> WSL) ----------------
def _is_windows_path(p: str) -> bool:
    return len(p) >= 2 and p[1] == ':' and p[0].isalpha()

def _to_wsl_path(p: str) -> Path:
    if _is_windows_path(p):
        win = PureWindowsPath(p)
        drive = win.drive[0].lower()
        tail = Path(*win.parts[1:])
        return Path("/mnt") / drive / tail
    return Path(p)

def _norm_path(p: Optional[str], default: Optional[str] = None) -> Path:
    if not p and default is not None:
        p = default
    if not p:
        return Path(".").resolve()
    return _to_wsl_path(p).resolve()


# ---------------- API principal ----------------
def run(
    *,
    config: Dict[str, Any],
    headless: bool,
    rut_filtro: Optional[str] = None,
    tipos_filtro: Optional[List[str]] = None,
) -> None:
    """
    Orquesta las extracciones según el config ya cargado (dict).
    Compatible con main.py que llama orquestador.run(...)
    """
    rutas = config.get("rutas", {}) or {}
    carpeta_base = _to_wsl_path(rutas.get("carpeta_base", "./data")).resolve()
    chromedriver_raw = rutas.get("chromedriver")
    chrome_binary_raw = rutas.get("chrome_binary")

    chromedriver = str(_to_wsl_path(chromedriver_raw)) if chromedriver_raw else None
    chrome_binary = str(_to_wsl_path(chrome_binary_raw)) if chrome_binary_raw else None

    d = config.get("descarga", {}) or {}
    anho_ini = int(d["anho_inicio"]); mes_ini = int(d["mes_inicio"])
    anho_fin = int(d["anho_fin"]);    mes_fin = int(d["mes_fin"])
    anho_ini, mes_ini, anho_fin, mes_fin = _validate_and_fix_range(anho_ini, mes_ini, anho_fin, mes_fin)

    tipos_cfg = _normalize_tipos(d.get("tipos_libro", ["venta", "compra"]))
    if tipos_filtro:
        tipos_cfg = _normalize_tipos(tipos_filtro)

    clientes = _select_clientes(config, rut_filtro)
    if not clientes:
        raise ValueError("No hay clientes/credenciales válidas (o el filtro --rut no coincide).")

    print(f"[SETUP] Base: {carpeta_base} | Rango {anho_ini}-{mes_ini:02d} → {anho_fin}-{mes_fin:02d} | Tipos: {', '.join(tipos_cfg)} | headless={headless}")

    for c in clientes:
        rut, clave = c["rut"], c["clave"]
        print("\n" + "="*60)
        print(f"Cliente: {rut}")
        print("="*60)
        for tipo in tipos_cfg:
            try:
                print(f"[Extracción] {tipo.title()}…")
                if tipo == "VENTA":
                    run_venta(
                        rut=rut, clave=clave,
                        anho_ini=anho_ini, mes_ini=mes_ini, anho_fin=anho_fin, mes_fin=mes_fin,
                        carpeta_base=carpeta_base, headless=headless,
                        chrome_binary=chrome_binary, chromedriver_path=chromedriver
                    )
                else:
                    run_compra(
                        rut=rut, clave=clave,
                        anho_ini=anho_ini, mes_ini=mes_ini, anho_fin=anho_fin, mes_fin=mes_fin,
                        carpeta_base=carpeta_base, headless=headless,
                        chrome_binary=chrome_binary, chromedriver_path=chromedriver
                    )
                print(f"[OK] {tipo.title()} completado.")
            except Exception as e:
                print(f"[WARN] Falló {tipo} para {rut}: {e}")


# ---------------- modo CLI opcional ----------------
def _load_yaml(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def main() -> int:
    import argparse
    p = argparse.ArgumentParser(description="Orquestador extracción RCV (SII)")
    p.add_argument("--config", required=True, help="Ruta a sample_config.yaml")
    p.add_argument("--no-headless", action="store_true", help="Mostrar navegador")
    p.add_argument("--rut", help="Procesar solo este RUT")
    p.add_argument("--tipos", help="Forzar tipos: 'venta', 'compra' o 'venta,compra'")
    args = p.parse_args()

    cfg = _load_yaml(Path(args.config))
    tipos = [t.strip() for t in args.tipos.split(",")] if args.tipos else None
    run(config=cfg, headless=not args.no_headless, rut_filtro=args.rut, tipos_filtro=tipos)
    print("\n[OK] Extracción finalizada.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
