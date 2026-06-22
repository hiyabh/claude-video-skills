"""
Browser Album Downloader — Generic Template
============================================
Downloads photo albums from authenticated sites (Facebook, Instagram, Google Photos,
Pinterest private boards, etc.) via a headed Chromium browser.

The user logs in MANUALLY in the visible browser window — this script never sees
credentials.

USAGE:
    1. Copy this file to your project: cp album_downloader.py <project>/download_album.py
    2. Edit ALBUM_URL and PLATFORM constants below
    3. Run in YOUR OWN PowerShell (NOT via Claude's Bash tool — the input() prompt blocks):
           cd <project>; python download_album.py
    4. Browser opens. Log in to the site. Navigate to first photo of album.
    5. Press ENTER in terminal. Script downloads everything to ./downloads/

Output: ./downloads/photo_001_<id>.jpg, photo_002_<id>.jpg, ...
"""

import hashlib
import re
import sys
import time
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import requests
from playwright.sync_api import TimeoutError as PWTimeout
from playwright.sync_api import sync_playwright

# =============================================================================
# CONFIGURE THESE FOR YOUR DOWNLOAD
# =============================================================================

ALBUM_URL = "REPLACE_ME"   # paste the URL of the first photo in the album
PLATFORM = "facebook"      # one of: facebook | instagram | google_photos | pinterest | generic

# =============================================================================
# PLATFORM CONFIGS — selectors and URL parsing per site
# =============================================================================

PLATFORM_CONFIGS: dict[str, dict] = {
    "facebook": {
        "next_selectors": [
            'a[aria-label="התמונה הבאה"]',
            'a[aria-label="Next photo"]',
            'div[aria-label="התמונה הבאה"]',
            'div[aria-label="Next photo"]',
            'a[aria-label*="הבאה"]',
            'a[aria-label*="Next"]',
            '[data-name="MWPhotoViewerNextButton"]',
        ],
        "img_filter": lambda src: "scontent" in src or "fbcdn" in src,
        "id_param": "fbid",            # in querystring
        "id_path_regex": None,
        "locale": "he-IL",
    },
    "instagram": {
        "next_selectors": [
            'button[aria-label="Next"]',
            'button[aria-label="הבא"]',
            'svg[aria-label="Next"]',
            'svg[aria-label="הבא"]',
        ],
        "img_filter": lambda src: "cdninstagram" in src or "fbcdn.net" in src,
        "id_param": None,
        "id_path_regex": r"/p/([^/]+)/",   # /p/<shortcode>/
        "locale": "en-US",
    },
    "google_photos": {
        "next_selectors": [
            'div[aria-label="הצג את הפריט הבא"]',
            'div[aria-label="View next item"]',
            'div[aria-label*="next"]',
            'div[aria-label*="הבא"]',
        ],
        "img_filter": lambda src: "googleusercontent.com" in src,
        "id_param": None,
        "id_path_regex": r"/photo/([^/?]+)",
        "locale": "he-IL",
    },
    "generic": {
        # Fallback — only ArrowRight keyboard navigation, accepts any large image
        "next_selectors": [],
        "img_filter": lambda src: True,
        "id_param": None,
        "id_path_regex": None,
        "locale": "en-US",
    },
}

# =============================================================================
# RUNTIME SETTINGS
# =============================================================================

MAX_PHOTOS = 500           # hard safety cap
MIN_DELAY = 1.2            # seconds between photo navigations (be polite)
PAGE_TIMEOUT = 30_000      # 30s navigation timeout

SCRIPT_DIR = Path(__file__).parent
DOWNLOAD_DIR = SCRIPT_DIR / "downloads"
USER_DATA_DIR = SCRIPT_DIR / ".browser_profile"

DOWNLOAD_DIR.mkdir(exist_ok=True)
USER_DATA_DIR.mkdir(exist_ok=True)


# =============================================================================
# HELPERS
# =============================================================================

def log(msg: str) -> None:
    print(f"[+] {msg}", flush=True)


def warn(msg: str) -> None:
    print(f"[!] {msg}", flush=True)


def get_current_id(page, cfg: dict) -> str | None:
    """Extract a unique identifier for the current photo to detect album loops."""
    try:
        url = page.url
        parsed = urlparse(url)

        if cfg.get("id_param"):
            qs = parse_qs(parsed.query)
            return qs.get(cfg["id_param"], [None])[0]

        if cfg.get("id_path_regex"):
            m = re.search(cfg["id_path_regex"], parsed.path)
            return m.group(1) if m else None

        # Fallback: hash the full URL
        return hashlib.md5(url.encode()).hexdigest()[:12]
    except Exception:
        return None


def extract_largest_image_url(page, cfg: dict) -> str | None:
    """
    Find the highest-resolution image on the current photo page.

    Strategies in order:
    1. og:image meta tag (most reliable for FB/IG)
    2. Largest visible <img> matching the platform's CDN filter
    """
    # Strategy 1: og:image
    try:
        og = page.locator('meta[property="og:image"]').first
        if og.count() > 0:
            url = og.get_attribute("content", timeout=2000)
            if url and cfg["img_filter"](url):
                return url
    except Exception:
        pass

    # Strategy 2: largest <img> matching filter
    try:
        filter_src = cfg["img_filter"]
        all_imgs = page.evaluate(
            """() => Array.from(document.querySelectorAll('img'))
                .filter(i => i.src)
                .map(i => ({
                    src: i.src,
                    w: i.naturalWidth || i.width || 0,
                    h: i.naturalHeight || i.height || 0,
                }))"""
        )
        candidates = [
            img for img in all_imgs
            if filter_src(img["src"]) and (img["w"] >= 400 or img["h"] >= 400)
        ]
        candidates.sort(key=lambda x: x["w"] * x["h"], reverse=True)
        if candidates:
            return candidates[0]["src"]
    except Exception:
        pass

    return None


def safe_filename(idx: int, photo_id: str | None, url: str) -> str:
    ext = ".jpg"
    m = re.search(r"\.(jpe?g|png|webp|gif)", url.lower())
    if m:
        ext = "." + m.group(1).replace("jpeg", "jpg")
    id_part = photo_id or hashlib.md5(url.encode()).hexdigest()[:10]
    # Sanitize id_part for Windows filenames
    id_part = re.sub(r"[^a-zA-Z0-9_-]", "_", id_part)[:30]
    return f"photo_{idx:03d}_{id_part}{ext}"


def download_image(url: str, dest: Path, cookies: list) -> bool:
    """Download via requests, reusing browser session cookies."""
    try:
        sess = requests.Session()
        for c in cookies:
            sess.cookies.set(c["name"], c["value"], domain=c.get("domain", ""))
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36"
            ),
            "Referer": "https://www.facebook.com/",
        }
        r = sess.get(url, headers=headers, timeout=30, stream=True, verify=False)
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        return dest.stat().st_size > 1000
    except Exception as e:
        warn(f"Download failed: {e}")
        return False


def click_next(page, cfg: dict) -> bool:
    """Click the next-photo arrow. Returns True if navigated."""
    old_url = page.url

    for sel in cfg["next_selectors"]:
        try:
            el = page.locator(sel).first
            if el.count() > 0 and el.is_visible():
                el.click(timeout=3000)
                page.wait_for_load_state("domcontentloaded", timeout=PAGE_TIMEOUT)
                for _ in range(30):
                    if page.url != old_url:
                        time.sleep(0.8)
                        return True
                    time.sleep(0.2)
                return False
        except Exception:
            continue

    # Fallback: ArrowRight keyboard
    try:
        page.keyboard.press("ArrowRight")
        page.wait_for_load_state("domcontentloaded", timeout=PAGE_TIMEOUT)
        for _ in range(30):
            if page.url != old_url:
                time.sleep(0.8)
                return True
            time.sleep(0.2)
    except Exception:
        pass

    return False


# =============================================================================
# MAIN
# =============================================================================

def main() -> int:
    if ALBUM_URL == "REPLACE_ME":
        warn("Edit ALBUM_URL constant at the top of this file first.")
        return 1
    if PLATFORM not in PLATFORM_CONFIGS:
        warn(f"Unknown PLATFORM '{PLATFORM}'. Choose from: {list(PLATFORM_CONFIGS)}")
        return 1

    cfg = PLATFORM_CONFIGS[PLATFORM]
    log(f"Platform: {PLATFORM}")
    log(f"Download dir: {DOWNLOAD_DIR}")
    log(f"Browser profile (persistent login): {USER_DATA_DIR}")

    # Suppress InsecureRequestWarning from urllib3 when verify=False
    try:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    except Exception:
        pass

    with sync_playwright() as p:
        log("Launching Chromium (headed mode for manual login)...")
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
            viewport={"width": 1400, "height": 900},
            locale=cfg["locale"],
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        log("Navigating to album URL...")
        try:
            page.goto(ALBUM_URL, timeout=PAGE_TIMEOUT, wait_until="domcontentloaded")
        except PWTimeout:
            warn("Initial nav timed out; continuing — you may navigate manually.")

        print()
        print("=" * 70)
        print("  ACTION REQUIRED:")
        print("  1. In the browser window, LOG IN if not already")
        print("  2. Navigate to the FIRST photo of the album (in fullscreen lightbox)")
        print("  3. Verify you can see the photo clearly")
        print("  4. Come BACK HERE and press ENTER to start downloading")
        print("=" * 70)
        try:
            input("\n>>> Press ENTER when ready... ")
        except KeyboardInterrupt:
            log("Aborted by user.")
            ctx.close()
            return 1

        cookies = ctx.cookies()
        log(f"Got {len(cookies)} cookies from browser session.")
        log("Starting download loop...")

        seen_ids: set[str] = set()
        downloaded = 0
        failures = 0
        idx = 1

        while idx <= MAX_PHOTOS:
            photo_id = get_current_id(page, cfg)
            log(f"[{idx:03d}] id={photo_id}")

            if photo_id and photo_id in seen_ids:
                log(f"Looped back to id={photo_id} -> album complete. Stopping.")
                break
            if photo_id:
                seen_ids.add(photo_id)

            # Wait for image render
            try:
                page.wait_for_selector('meta[property="og:image"]', timeout=10_000)
            except PWTimeout:
                pass
            time.sleep(0.6)

            img_url = extract_largest_image_url(page, cfg)
            if not img_url:
                warn(f"[{idx:03d}] Could not find image URL.")
                failures += 1
            else:
                fname = safe_filename(idx, photo_id, img_url)
                dest = DOWNLOAD_DIR / fname
                if dest.exists() and dest.stat().st_size > 1000:
                    log(f"[{idx:03d}] Already downloaded: {fname}")
                    downloaded += 1
                else:
                    log(f"[{idx:03d}] Downloading -> {fname}")
                    if download_image(img_url, dest, cookies):
                        downloaded += 1
                        log(f"[{idx:03d}] Saved ({dest.stat().st_size // 1024} KB)")
                    else:
                        failures += 1

            log(f"[{idx:03d}] Advancing to next photo...")
            if not click_next(page, cfg):
                log("No 'next' arrow available -> end of album.")
                break

            idx += 1
            time.sleep(MIN_DELAY)

        print()
        log("=" * 50)
        log(f"DONE. Downloaded: {downloaded}  Failures: {failures}")
        log(f"Files in: {DOWNLOAD_DIR}")
        log("=" * 50)
        print()
        log("Browser stays open. Close it manually when ready.")
        try:
            input(">>> Press ENTER to close browser and exit... ")
        except KeyboardInterrupt:
            pass
        ctx.close()
        return 0


if __name__ == "__main__":
    sys.exit(main())
