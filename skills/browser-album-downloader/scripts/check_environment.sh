#!/usr/bin/env bash
# Verifies the environment has everything needed for the browser-album-downloader skill.
# Run before invoking templates/album_downloader.py for the first time.

set -e
echo "[+] Checking Python..."
python --version || { echo "[!] Python not installed"; exit 1; }

echo "[+] Checking Playwright..."
python -c "import playwright; print('  playwright module OK')" || {
    echo "[!] Installing playwright..."
    python -m pip install --user playwright
}

echo "[+] Checking requests..."
python -c "import requests; print('  requests:', requests.__version__)" || {
    echo "[!] Installing requests..."
    python -m pip install --user requests
}

echo "[+] Checking Chromium browser..."
python -c "from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    b.close()
    print('  Chromium OK')" 2>/dev/null || {
    echo "[!] Installing Chromium..."
    python -m playwright install chromium
}

echo ""
echo "[+] Environment ready."
echo "[+] Next: copy templates/album_downloader.py to your project,"
echo "        edit ALBUM_URL + PLATFORM constants, then run:"
echo "          cd <project>; python download_album.py"
