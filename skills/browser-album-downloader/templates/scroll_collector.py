"""
Browser Album Downloader — Infinite-Scroll Pattern
===================================================
For sites that don't have a "next photo" lightbox (Pinterest boards, Tumblr blogs,
Bandcamp galleries). Instead of walking photos one-by-one, scroll to the bottom,
collect all image URLs at once, then download in parallel.

USAGE: same as album_downloader.py — edit constants, then run in your own terminal.
"""

import hashlib
import re
import sys
import time
from pathlib import Path

import requests
from playwright.sync_api import sync_playwright

# =============================================================================
# CONFIGURE
# =============================================================================

PAGE_URL = "REPLACE_ME"
PLATFORM = "pinterest"   # pinterest | tumblr | generic_scroll

PLATFORM_CONFIGS = {
    "pinterest": {
        "img_filter": lambda src: "i.pinimg.com" in src,
        "upscale_url": lambda src: re.sub(r"/\d+x/", "/originals/", src),
        "locale": "en-US",
    },
    "tumblr": {
        "img_filter": lambda src: "media.tumblr.com" in src,
        "upscale_url": lambda src: re.sub(r"_\d+\.", "_1280.", src),
        "locale": "en-US",
    },
    "generic_scroll": {
        "img_filter": lambda src: True,
        "upscale_url": lambda src: src,
        "locale": "en-US",
    },
}

MAX_SCROLLS = 100        # safety cap
SCROLL_PAUSE = 1.5       # wait for lazy-load between scrolls
NO_NEW_THRESHOLD = 3     # stop after N scrolls with no new images

SCRIPT_DIR = Path(__file__).parent
DOWNLOAD_DIR = SCRIPT_DIR / "downloads"
USER_DATA_DIR = SCRIPT_DIR / ".browser_profile"
DOWNLOAD_DIR.mkdir(exist_ok=True)
USER_DATA_DIR.mkdir(exist_ok=True)


def log(m): print(f"[+] {m}", flush=True)
def warn(m): print(f"[!] {m}", flush=True)


def main() -> int:
    if PAGE_URL == "REPLACE_ME":
        warn("Edit PAGE_URL constant at top of file.")
        return 1

    cfg = PLATFORM_CONFIGS[PLATFORM]
    log(f"Platform: {PLATFORM}")

    try:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    except Exception:
        pass

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
            viewport={"width": 1400, "height": 900},
            locale=cfg["locale"],
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(PAGE_URL, timeout=30_000, wait_until="domcontentloaded")

        print("=" * 70)
        print("  ACTION REQUIRED: log in if needed, then press ENTER.")
        print("=" * 70)
        input(">>> ")

        log("Scrolling to bottom and collecting images...")
        seen: set[str] = set()
        no_new_count = 0

        for i in range(MAX_SCROLLS):
            srcs = page.evaluate(
                """() => Array.from(document.querySelectorAll('img'))
                    .map(i => i.src).filter(s => s && s.startsWith('http'))"""
            )
            filtered = [s for s in srcs if cfg["img_filter"](s)]
            upscaled = {cfg["upscale_url"](s) for s in filtered}
            new = upscaled - seen
            seen.update(new)
            log(f"Scroll {i + 1}: {len(new)} new (total {len(seen)})")

            if not new:
                no_new_count += 1
                if no_new_count >= NO_NEW_THRESHOLD:
                    log("No new images after several scrolls -> done.")
                    break
            else:
                no_new_count = 0

            page.evaluate("window.scrollBy(0, window.innerHeight * 2)")
            time.sleep(SCROLL_PAUSE)

        log(f"Total unique images: {len(seen)}")
        cookies = ctx.cookies()

        sess = requests.Session()
        for c in cookies:
            sess.cookies.set(c["name"], c["value"], domain=c.get("domain", ""))

        ok = fail = 0
        for idx, url in enumerate(sorted(seen), 1):
            ext = ".jpg"
            m = re.search(r"\.(jpe?g|png|webp|gif)", url.lower())
            if m:
                ext = "." + m.group(1).replace("jpeg", "jpg")
            fname = f"img_{idx:04d}_{hashlib.md5(url.encode()).hexdigest()[:8]}{ext}"
            dest = DOWNLOAD_DIR / fname
            if dest.exists() and dest.stat().st_size > 1000:
                log(f"[{idx:04d}] exists: {fname}")
                ok += 1
                continue
            try:
                r = sess.get(url, timeout=30, verify=False)
                r.raise_for_status()
                dest.write_bytes(r.content)
                log(f"[{idx:04d}] saved ({len(r.content) // 1024} KB)")
                ok += 1
            except Exception as e:
                warn(f"[{idx:04d}] failed: {e}")
                fail += 1
            time.sleep(0.3)

        log("=" * 50)
        log(f"DONE. Downloaded: {ok}  Failures: {fail}")
        log(f"Files in: {DOWNLOAD_DIR}")
        log("=" * 50)
        input(">>> Press ENTER to close... ")
        ctx.close()
        return 0


if __name__ == "__main__":
    sys.exit(main())
