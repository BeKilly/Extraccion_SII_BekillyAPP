import argparse
import os
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

def autodetect_binary():
    candidates = [
        os.environ.get("GOOGLE_CHROME_BIN"),
        os.environ.get("CHROME_BIN"),
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/snap/bin/chromium",
    ]
    for p in candidates:
        if p and os.path.exists(p):
            return p
    return None

def autodetect_chromedriver():
    return shutil.which("chromedriver")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chrome-binary", default=None)
    parser.add_argument("--chromedriver", default=None)
    parser.add_argument("--headless", action="store_true", default=True)
    args = parser.parse_args()

    opts = Options()
    if args.headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--remote-debugging-port=9222")

    if args.chrome_binary:
        opts.binary_location = args.chrome_binary
    else:
        auto = autodetect_binary()
        if auto:
            opts.binary_location = auto

    if args.chromedriver:
        service = Service(args.chromedriver)
    else:
        cd = autodetect_chromedriver()
        service = Service(cd) if cd else Service()  # Selenium Manager fallback

    print("Using Chrome binary:", getattr(opts, "binary_location", None))
    print("Using chromedriver:", getattr(service, "path", None))

    driver = webdriver.Chrome(service=service, options=opts)
    try:
        caps = driver.capabilities
        browser_ver = caps.get("browserVersion") or caps.get("version")
        cd_ver = (caps.get("chrome") or {}).get("chromedriverVersion", "").split(" ")[0]
        print("Browser version:", browser_ver)
        print("Chromedriver version:", cd_ver)
        driver.get("about:blank")
        ua = driver.execute_script("return navigator.userAgent")
        print("User-Agent:", ua)
        print("OK: Selenium pudo iniciar Chrome en headless.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
