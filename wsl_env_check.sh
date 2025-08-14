#!/usr/bin/env bash
set -e

echo "=== SO/WSL ==="
uname -a || true
grep -i wsl /proc/version || true

echo
echo "=== DISPLAY/GUI (para no-headless) ==="
echo "DISPLAY=$DISPLAY"
echo "WAYLAND_DISPLAY=$WAYLAND_DISPLAY"

echo
echo "=== Python/venv ==="
echo "which python: $(which python || true)"
python -V || true
echo "which pip: $(which pip || true)"
pip -V || true
python -c "import sys; print('sys.executable:', sys.executable)" || true
python -c "import selenium; print('selenium:', selenium.__version__)" 2>/dev/null || echo "selenium: NO INSTALADO"

echo
echo "=== Navegadores instalados ==="
which -a google-chrome || true
which -a chromium || true
which -a chromium-browser || true
google-chrome --version 2>/dev/null || true
chromium --version 2>/dev/null || true
chromium-browser --version 2>/dev/null || true

echo
echo "=== chromedriver ==="
which -a chromedriver || true
chromedriver --version 2>/dev/null || true

echo
echo "=== Permisos en /mnt/c ==="
TEST_DIR="/mnt/c/_wsl_write_test_$$"
mkdir -p "$TEST_DIR" && touch "$TEST_DIR/test.txt" && echo "OK: escritura en /mnt/c permitida" || echo "ERROR: sin permisos de escritura en /mnt/c"
rm -rf "$TEST_DIR"

echo
echo "=== Rutas candidatas (útiles para tu config.yaml) ==="
[ -x /usr/bin/google-chrome ] && echo "chrome_binary: /usr/bin/google-chrome"
[ -x /usr/bin/chromium ] && echo "chrome_binary: /usr/bin/chromium"
[ -x /usr/bin/chromium-browser ] && echo "chrome_binary: /usr/bin/chromium-browser"
[ -x /snap/bin/chromium ] && echo "chrome_binary: /snap/bin/chromium"
[ -x /usr/bin/chromedriver ] && echo "chromedriver: /usr/bin/chromedriver"
[ -x /snap/bin/chromium.chromedriver ] && echo "chromedriver: /snap/bin/chromium.chromedriver"

echo
echo "=== Recomendación instalación (si faltan) ==="
echo "sudo apt update && sudo apt install -y chromium-browser chromium-chromedriver"