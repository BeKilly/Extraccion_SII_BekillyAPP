# src/conciliacion/sii/extraccion/common_rcv.py
from __future__ import annotations

import os
import time
import shutil
import tempfile
from pathlib import Path
from typing import Optional, Tuple

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
    NoSuchElementException,
)

SII_URL = "https://www4.sii.cl/consdcvinternetui/"

# =========================
# Utilidades ambiente
# =========================
def _free_port() -> int:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]

def _autodetect_chrome_binary(explicit: Optional[str]) -> Optional[str]:
    if explicit and os.path.exists(explicit):
        return explicit
    for p in (
        os.environ.get("CHROME_BIN"),
        shutil.which("google-chrome"),
        "/usr/bin/google-chrome",
        shutil.which("chromium-browser"),
        "/usr/bin/chromium-browser",
        shutil.which("chromium"),
        "/snap/bin/chromium",
    ):
        if p and os.path.exists(p):
            return p
    return None

def build_driver(
    *,
    download_dir: Path,
    headless: bool,
    chrome_binary: Optional[str] = None,
    chromedriver_path: Optional[str] = None,
) -> Tuple[webdriver.Chrome, WebDriverWait, str]:
    """Crea un Chrome listo para descargar en download_dir (WSL-friendly)."""
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    for a in (
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--disable-extensions",
        "--window-size=1920,1080",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-sync",
    ):
        opts.add_argument(a)

    tmp_profile = tempfile.mkdtemp(prefix="bekilly_chrome_")
    opts.add_argument(f"--user-data-dir={tmp_profile}")
    opts.add_argument(f"--remote-debugging-port={_free_port()}")

    bin_loc = _autodetect_chrome_binary(chrome_binary)
    if bin_loc:
        opts.binary_location = bin_loc

    download_dir.mkdir(parents=True, exist_ok=True)
    prefs = {
        "download.default_directory": str(download_dir),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "plugins.always_open_pdf_externally": True,
    }
    opts.add_experimental_option("prefs", prefs)

    if chromedriver_path:
        service = Service(chromedriver_path)
    else:
        which_cd = shutil.which("chromedriver")
        service = Service(which_cd) if which_cd else Service()

    driver = webdriver.Chrome(service=service, options=opts)
    wait = WebDriverWait(driver, 14)
    return driver, wait, tmp_profile

# =========================
# Sesión / navegación SII
# =========================
def _esta_en_login(driver) -> bool:
    try:
        url = driver.current_url
        if any(k in url for k in ("IngresoRutClave", "AUT2000", "AUTENTICACION")):
            return True
    except Exception:
        pass
    for by, sel in (
        (By.ID, "rutcntr"),
        (By.NAME, "rut"),
        (By.ID, "clave"),
        (By.NAME, "clave"),
        (By.ID, "bt_ingresar"),
    ):
        try:
            if driver.find_element(by, sel):
                return True
        except Exception:
            continue
    return False

def _cerrar_alertas(driver, wait: WebDriverWait) -> None:
    xps = (
        "//div[contains(@class,'modal') and contains(@class,'show')]//button[normalize-space()='Aceptar']",
        "//div[contains(@class,'modal') and contains(@class,'show')]//button[normalize-space()='OK']",
        "//div[contains(@class,'modal') and contains(@class,'show')]//button[contains(.,'Cerrar')]",
        "//button[normalize-space()='Aceptar']",
        "//button[normalize-space()='OK']",
        "//button[contains(.,'Cerrar')]",
    )
    for xp in xps:
        for el in driver.find_elements(By.XPATH, xp):
            try:
                if el.is_displayed() and el.is_enabled():
                    driver.execute_script("arguments[0].click();", el)
                    time.sleep(0.2)
            except Exception:
                pass

def _asegurar_sesion(driver, wait: WebDriverWait, rut: str, clave: str) -> None:
    if not _esta_en_login(driver):
        return
    # Variante común
    try:
        rut_el = wait.until(EC.presence_of_element_located((By.ID, "rutcntr")))
        rut_el.clear(); rut_el.send_keys(rut)
        clave_el = driver.find_element(By.ID, "clave")
        clave_el.clear(); clave_el.send_keys(clave)
        btn = driver.find_element(By.ID, "bt_ingresar")
        driver.execute_script("arguments[0].click();", btn)
        time.sleep(0.2)
        return
    except Exception:
        pass
    # Variante alternativa
    try:
        rut_el = wait.until(EC.presence_of_element_located((By.NAME, "rut")))
        rut_el.clear(); rut_el.send_keys(rut)
        clave_el = driver.find_element(By.NAME, "clave")
        clave_el.clear(); clave_el.send_keys(clave)
        for xp in ("//button[@id='bt_ingresar']", "//button[contains(.,'Ingresar')]", "//input[@type='submit']"):
            try:
                b = driver.find_element(By.XPATH, xp)
                driver.execute_script("arguments[0].click();", b)
                time.sleep(0.2)
                return
            except Exception:
                continue
    except Exception:
        pass

def goto_rcv(driver, wait: WebDriverWait, rut: str, clave: str) -> None:
    driver.get(SII_URL)
    try:
        wait.until(
            EC.any_of(
                EC.presence_of_element_located((By.ID, "periodoMes")),
                EC.presence_of_element_located((By.XPATH, "//select[@ng-model='periodoAnho']")),
                EC.presence_of_element_located((By.ID, "rutcntr")),
            )
        )
    except TimeoutException:
        pass
    _asegurar_sesion(driver, wait, rut, clave)
    try:
        wait.until(
            EC.any_of(
                EC.presence_of_element_located((By.ID, "periodoMes")),
                EC.presence_of_element_located((By.XPATH, "//select[@ng-model='periodoAnho']")),
            )
        )
    except TimeoutException:
        time.sleep(0.2)

# =========================
# UI helpers
# =========================
def _click_resiliente(driver, locator, timeout=14) -> bool:
    el = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(locator))
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
    try:
        el.click()
        return True
    except ElementClickInterceptedException:
        pass
    try:
        driver.execute_script("arguments[0].click();", el)
        return True
    except Exception:
        pass
    try:
        el.send_keys(Keys.ENTER)
        return True
    except Exception:
        return False

def select_period_and_consult(driver, wait: WebDriverWait, *, anho: int, mes: int) -> None:
    # 1) Mes y Año (IDs/atributos reales del sitio)
    mes_el = wait.until(EC.presence_of_element_located((By.ID, "periodoMes")))
    Select(mes_el).select_by_value(f"{mes:02d}")
    anho_el = wait.until(EC.presence_of_element_located((By.XPATH, "//select[@ng-model='periodoAnho']")))
    Select(anho_el).select_by_value(str(anho))

    # 2) Consultar (XPath absoluto + fallbacks)
    locs = [
        (By.XPATH, "/html/body/div[1]/div[2]/div[1]/div[1]/div/div[1]/div/div[3]/div/form/div[3]/button"),
        (By.XPATH, "//button[@type='submit' and normalize-space()='Consultar']"),
        (By.CSS_SELECTOR, "form button.btn.btn-default.btn-xs-block.btn-block[type='submit']"),
    ]
    for loc in locs:
        try:
            if _click_resiliente(driver, loc):
                break
        except TimeoutException:
            continue
    else:
        raise RuntimeError("No fue posible hacer click en 'Consultar'.")

    # 3) Espera inicial post-consulta
    try:
        wait.until(
            EC.any_of(
                EC.presence_of_element_located((By.XPATH, "//*[@role='tablist']")),
                EC.presence_of_element_located((By.XPATH, "//*[contains(@class,'nav-tabs')]")),
                EC.presence_of_element_located((By.XPATH, "//strong[normalize-space()='COMPRA']")),
                EC.presence_of_element_located((By.XPATH, "//strong[normalize-space()='VENTA']")),
                EC.invisibility_of_element_located((By.CSS_SELECTOR, ".loading, .spinner, .block-ui-message-container")),
            )
        )
    except TimeoutException:
        pass

def _panel_visible(driver, tipo_up: str) -> bool:
    """Confirma que la pestaña correcta está activa (texto, li.active y hash #venta/#compra)."""
    base = tipo_up.lower()
    try:
        strong = driver.find_element(By.XPATH, f"//ul//li//strong[normalize-space()='{tipo_up}']")
        if strong.is_displayed():
            li = strong.find_element(By.XPATH, "../../..")
            if "active" in (li.get_attribute("class") or ""):
                return True
    except Exception:
        pass
    try:
        hashval = driver.execute_script("return window.location.hash || ''") or ""
        if f"#{base}/" in hashval:
            return True
    except Exception:
        pass
    for css in (f"#{base}.active", f"#pane-{base}.active", f"[role='tabpanel'].active[id*='{base}']"):
        try:
            if driver.find_element(By.CSS_SELECTOR, css):
                return True
        except Exception:
            continue
    return False

def activate_tab(driver, wait: WebDriverWait, *, tipo_up: str) -> None:
    """Activa COMPRA/VENTA priorizando ui-sref/href; incluye reintentos y fallback JS."""
    if _panel_visible(driver, tipo_up):
        return

    base = tipo_up.lower()

    # Preferidos: ui-sref / href
    preferidos = [
        (By.CSS_SELECTOR, f"a[ui-sref='{base}']"),
        (By.CSS_SELECTOR, f"a[href='#{base}/']"),
        (By.XPATH, f"//ul/li/a[@ui-sref='{base}']"),
        (By.XPATH, f"//ul/li/a[@href='#{base}/']"),
    ]
    for by, sel in preferidos:
        try:
            a = WebDriverWait(driver, 6).until(EC.element_to_be_clickable((by, sel)))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", a)
            driver.execute_script("arguments[0].click();", a)
            for _ in range(12):
                if _panel_visible(driver, tipo_up):
                    return
                time.sleep(0.1)
        except Exception:
            continue

    # Respaldo: XPaths absolutos de <strong>
    absolutos = {
        "COMPRA": "/html/body/div[1]/div[2]/div[1]/div[1]/div/div[2]/ul/li[1]/a/strong",
        "VENTA":  "/html/body/div[1]/div[2]/div[1]/div[1]/div/div[2]/ul/li[2]/a/strong",
    }
    xp = absolutos.get(tipo_up)
    if xp:
        try:
            st = WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.XPATH, xp)))
            a = st.find_element(By.XPATH, "./parent::*")
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", a)
            driver.execute_script("arguments[0].click();", a)
            for _ in range(12):
                if _panel_visible(driver, tipo_up):
                    return
                time.sleep(0.1)
        except Exception:
            pass

    # Fallback JS
    js = """
      var base = arguments[0];
      var a = document.querySelector("a[ui-sref='"+base+"']") || document.querySelector("a[href='#"+base+"/']");
      if(a){ a.click(); return true; }
      return false;
    """
    try:
        ok = driver.execute_script(js, base)
        if ok:
            for _ in range(12):
                if _panel_visible(driver, tipo_up):
                    return
                time.sleep(0.1)
    except Exception:
        pass

    raise NoSuchElementException(f"No fue posible activar la pestaña {tipo_up}")

def download_resumen_y_detalle(driver, wait: WebDriverWait) -> None:
    """Click en 'Descargar Resumenes' y luego 'Descargar Detalles' si existen."""
    try:
        wait.until(
            EC.any_of(
                EC.presence_of_element_located((By.XPATH, "//button[contains(.,'Descargar Resumenes')]")),
                EC.presence_of_element_located((By.XPATH, "//button[contains(.,'Descargar Detalles')]")),
                EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div[1]/div[2]/div/div/div/div/div[4]")),
            )
        )
    except TimeoutException:
        pass

    # Resumenes
    for loc in (
        (By.XPATH, "/html/body/div[1]/div[2]/div[1]/div[2]/div/div/div/div/div[4]/div[1]/div[1]/button"),
        (By.XPATH, "//button[normalize-space()='Descargar Resumenes']"),
        (By.XPATH, "//button[contains(.,'Descargar Resumenes')]"),
    ):
        try:
            if _click_resiliente(driver, loc):
                time.sleep(1.0)
                break
        except Exception:
            pass

    # Detalles
    for loc in (
        (By.XPATH, "/html/body/div[1]/div[2]/div[1]/div[2]/div/div/div/div/div[4]/div[1]/div[2]/button"),
        (By.XPATH, "//button[normalize-space()='Descargar Detalles']"),
        (By.XPATH, "//button[contains(.,'Descargar Detalles')]"),
    ):
        try:
            if _click_resiliente(driver, loc):
                time.sleep(2.0)
                break
        except Exception:
            pass

# =========================
# Core reutilizable por tipo
# =========================
def extract_for_tipo(
    *,
    rut: str,
    clave: str,
    anho_ini: int,
    mes_ini: int,
    anho_fin: int,
    mes_fin: int,
    tipo_up: str,  # "COMPRA" | "VENTA"
    carpeta_base: Path,
    headless: bool,
    chrome_binary: Optional[str],
    chromedriver_path: Optional[str],
) -> None:
    """Flujo completo para COMPRA o VENTA (incluye guard-rail y reintento de descarga)."""
    tipo_up = tipo_up.strip().upper()
    assert tipo_up in {"COMPRA", "VENTA"}, "tipo_up debe ser COMPRA o VENTA"

    out_dir = carpeta_base / f"SII_{rut}" / f"RCV_{tipo_up.capitalize()}"
    driver, wait, tmp_profile = build_driver(
        download_dir=out_dir,
        headless=headless,
        chrome_binary=chrome_binary,
        chromedriver_path=chromedriver_path,
    )

    try:
        caps = driver.capabilities
        print(f"[RCV] {tipo_up} | Headless={headless} | Chrome={caps.get('browserVersion') or caps.get('version')} → {out_dir}")
        goto_rcv(driver, wait, rut, clave)
        _cerrar_alertas(driver, wait)

        for anho in range(int(anho_ini), int(anho_fin) + 1):
            m_ini = int(mes_ini) if anho == int(anho_ini) else 1
            m_fin = int(mes_fin) if anho == int(anho_fin) else 12

            for mes in range(m_ini, m_fin + 1):
                ms = f"{mes:02d}"
                try:
                    if _esta_en_login(driver):
                        _asegurar_sesion(driver, wait, rut, clave)
                        goto_rcv(driver, wait, rut, clave)

                    # (1) Período + Consultar
                    select_period_and_consult(driver, wait, anho=anho, mes=mes)
                    _cerrar_alertas(driver, wait)

                    # (2) Activar pestaña correcta
                    activate_tab(driver, wait, tipo_up=tipo_up)
                    _cerrar_alertas(driver, wait)

                    # Guard-rail: confirmar activa; reintento si no
                    if not _panel_visible(driver, tipo_up):
                        print(f"[WARN] {tipo_up} {anho}-{ms}: pestaña no activa. Reintentando…")
                        activate_tab(driver, wait, tipo_up=tipo_up)
                        time.sleep(0.5)
                    if not _panel_visible(driver, tipo_up):
                        raise RuntimeError(f"Pestaña {tipo_up} no activa tras reintentos")

                    print(f"[UI] Pestaña activa: {tipo_up} | {anho}-{ms}")

                    # (3) Snapshot antes de descargar
                    before = set(p.name for p in out_dir.glob("*"))

                    # (4) Descargar Resumenes y Detalles
                    download_resumen_y_detalle(driver, wait)

                    # (5) Verificar archivos nuevos (10s). Si no, reintentar descarga.
                    for _ in range(10):
                        after = set(p.name for p in out_dir.glob("*"))
                        if after - before:
                            break
                        time.sleep(1)
                    else:
                        print(f"[WARN] {tipo_up} {anho}-{ms}: sin archivos nuevos tras 10s, reintentando descarga…")
                        download_resumen_y_detalle(driver, wait)

                except Exception as e:
                    print(f"[ERR] {tipo_up} {anho}-{ms}: {e}")
                    # Dump de depuración
                    try:
                        dbg = (carpeta_base / "debug")
                        dbg.mkdir(parents=True, exist_ok=True)
                        with open(dbg / f"debug_{tipo_up}_{anho}-{ms}.html", "w", encoding="utf-8") as f:
                            f.write(driver.page_source)
                        driver.save_screenshot(str(dbg / f"debug_{tipo_up}_{anho}-{ms}.png"))
                    except Exception:
                        pass
                    # Reposiciona en el módulo y sigue
                    try:
                        goto_rcv(driver, wait, rut, clave)
                    except Exception:
                        pass
                    continue
    finally:
        try:
            driver.quit()
        except Exception:
            pass
        try:
            shutil.rmtree(tmp_profile, ignore_errors=True)
        except Exception:
            pass
