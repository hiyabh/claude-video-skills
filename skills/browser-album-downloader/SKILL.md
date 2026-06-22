---
name: browser-album-downloader
description: Download photo/media albums from sites that require login and cannot be scraped with yt-dlp/gallery-dl/curl. Opens a real Chromium browser via Playwright, lets the user log in manually (Claude never sees credentials), then walks the album and downloads every photo at full resolution. Use when user wants to download Facebook private albums, Instagram private profile media, Google Photos shared albums, Pinterest private boards, WhatsApp Web media, LinkedIn galleries, Slack file attachments, or any image gallery behind authentication. Triggers — "תוריד אלבום", "הורד תמונות מ-Facebook", "Google Photos shared album", "download private album", "Facebook album scraper", "Instagram private photos", "אלבום פרטי", "אין לי גישה לדף", "תוריד את כל התמונות מהקישור", and any case where universal-downloader (yt-dlp / gallery-dl) fails because the content is gated behind login/permissions/session-cookies. NOT for public videos (use universal-downloader's yt-dlp), NOT for public image galleries (use gallery-dl).
---

# Browser Album Downloader

Download photo albums from authenticated/private sources using a headed browser. User logs in manually — Claude never touches credentials.

## When To Use This Skill (vs `universal-downloader`)

| Scenario                                                                 | Use                            |
| ------------------------------------------------------------------------ | ------------------------------ |
| Public YouTube/Vimeo/TikTok video, public Twitter media                  | `universal-downloader` (yt-dlp)|
| Public image gallery (Pixiv, public Pinterest, public Instagram profile) | `universal-downloader` (gallery-dl)|
| Direct file URL (`.pdf`, `.zip`, `.mp4`)                                 | `universal-downloader` (curl)  |
| **Private FB album** / **shared FB photos** / `set=ms.c...` URLs         | **this skill**                 |
| **Google Photos shared album** (login required, FE-only auth)            | **this skill**                 |
| **Instagram private profile** / **stories of private accounts**          | **this skill**                 |
| Pinterest private board, LinkedIn gallery, Slack file gallery            | **this skill**                 |
| Anything yt-dlp says "Login required" AND gallery-dl can't authenticate  | **this skill**                 |

Rule of thumb: if `yt-dlp --cookies-from-browser chrome <URL>` and `gallery-dl <URL>` both fail because the content is gated or rendered only after JS+auth, fall through to this skill.

## How It Works

1. **Persistent profile** at `<project>/.browser_profile/` — user logs in once, future runs reuse the session
2. **Headed Chromium** (visible window) — required so user can log in and verify the right page is open
3. **Manual gate** — script pauses with `input()` prompt until user types ENTER, confirming "the first photo of the album is now visible in fullscreen"
4. **Auto-walk** — clicks "next photo" arrow (in target site's locale), waits for URL change, scrapes the highest-resolution image, downloads via `requests` with the browser's cookies
5. **Dedup** — tracks seen IDs (`fbid`, `media_id`, etc.) to detect when the album loops back to start

## IRON RULES

### RULE 1: Never ask user for credentials

The user logs in manually inside the visible browser window. Claude must never:
- Suggest entering passwords into the script
- Read `.browser_profile/` cookies and transmit them anywhere
- Use `--cookies-from-browser` against the user's main Chrome (use the persistent profile instead)
- Ask for app passwords, 2FA codes, session tokens

### RULE 2: Headed mode only

`headless=True` defeats the purpose — user needs to see the login form and verify the right page is open. Always:

```python
ctx = p.chromium.launch_persistent_context(
    user_data_dir=str(USER_DATA_DIR),
    headless=False,                # NEVER True for this skill
    viewport={"width": 1400, "height": 900},
)
```

### RULE 3: Confirm user is on the right page before scraping

Two human checkpoints:
1. Initial: `input(">>> Press ENTER when you're logged in and see the first photo... ")`
2. Final: `input(">>> Press ENTER to close browser... ")` — gives user a chance to manually rescue anything missed

### RULE 4: Polite pacing (1.2-2.5s between photos)

Facebook/Instagram aggressively rate-limit. Hardcoded `MIN_DELAY = 1.2` between navigations. Do not lower below 1s unless user explicitly asks and accepts ban risk.

### RULE 5: Multi-strategy image URL extraction

Sites change layout. Always try in order:
1. `<meta property="og:image">` (most reliable for FB)
2. Largest visible `<img>` with `scontent`/`fbcdn`/`googleusercontent`/etc. in src
3. Background-image CSS on photo container
4. JSON-in-script extraction (last resort)

### RULE 6: Stop on loop, not on count

Use `seen_ids: set[str]` — when you encounter an ID you've already saved, the album has looped. Always set `MAX_PHOTOS` cap (default 500) as a hard safety stop.

### RULE 7: Headed Chromium needs interactive terminal

User MUST run the script themselves in their own PowerShell/CMD. Claude cannot run it via Bash tool because the `input()` prompt blocks indefinitely. **Always tell the user the exact command and wait for their report.**

```bash
cd <project_dir>; python download_album.py
```

(PowerShell uses `;` not `&&` for command chaining.)

### RULE 8: One platform = one selector config

Different sites have different "next photo" selectors. Maintain `PLATFORM_CONFIGS` dict keyed by domain — never hardcode FB selectors into a generic script. See `templates/album_downloader.py` for the pattern.

---

## Playbooks

### Playbook 1: Facebook private/shared album

URL shape: `https://www.facebook.com/photo/?fbid=<ID>&set=ms.c...` (message attachment) or `set=a.<ID>` (regular album) or `set=pcb.<ID>` (post-attached).

```bash
# 1. Copy template
cp ~/.claude/skills/browser-album-downloader/templates/album_downloader.py <project>/download_album.py

# 2. Edit ALBUM_URL constant + PLATFORM = "facebook"

# 3. User runs in their own PowerShell:
cd <project>; python download_album.py

# 4. User logs in, navigates to first photo, presses ENTER
# 5. Script downloads to ./downloads/photo_NNN_<fbid>.jpg
```

Selectors used: `a[aria-label="התמונה הבאה"]` (Hebrew UI) and `a[aria-label="Next photo"]` (English). Falls back to `ArrowRight` keyboard.

### Playbook 2: Google Photos shared album

URL shape: `https://photos.app.goo.gl/<short>` or `https://photos.google.com/share/<long>?key=<key>`

Different DOM — photos are in a virtualized grid. Click a thumbnail to open lightbox, then walk with arrow keys.

```python
PLATFORM = "google_photos"
NEXT_SELECTORS = [
    'div[aria-label="הצג את הפריט הבא"]',
    'div[aria-label="View next item"]',
]
IMG_FILTER = lambda src: "googleusercontent.com" in src
URL_PARAM_FOR_DEDUPE = None  # Google Photos uses path segments not query params
```

For Google Photos prefer **Takeout** (`takeout.google.com`) when the user owns the album — it's a one-click ZIP. This skill is for albums *shared with* the user that aren't in Takeout scope.

### Playbook 3: Instagram private profile / saved posts

```python
PLATFORM = "instagram"
NEXT_SELECTORS = [
    'button[aria-label="Next"]',
    'svg[aria-label="הבא"]',
]
IMG_FILTER = lambda src: "cdninstagram.com" in src or "fbcdn.net" in src
```

User must be logged in AND following the private account (or have it own the saved post).

### Playbook 4: Pinterest private board

```python
PLATFORM = "pinterest"
# Pinterest uses infinite scroll — different pattern.
# Strategy: scroll to bottom repeatedly, collect all <img src*="i.pinimg.com">,
# convert `/236x/` to `/originals/` for full-res, then download.
```

See `templates/scroll_collector.py` for the scroll-based pattern.

### Playbook 5: Slack file gallery / Notion gallery

```python
PLATFORM = "generic_gallery"
# Slack: aria-label="Next file"
# Notion: keyboard ArrowRight on image lightbox
# Both use authenticated CDN URLs that expire — download immediately, don't queue
```

### Playbook 6: Add support for a new platform

1. Inspect the target page in DevTools — find:
   - "Next" button selector (try aria-label first, both in user's locale and English)
   - URL pattern that changes per photo (querystring? path segment?)
   - Image CDN domain (for filtering relevant `<img>` tags)
2. Add entry to `PLATFORM_CONFIGS` in `templates/album_downloader.py`
3. Test on a small album (5-10 photos) before running 100+
4. Update this SKILL.md with a new Playbook

---

## Decision Tree

```
User asks to download album/photos from URL
 ├── URL is public + non-gallery → universal-downloader (yt-dlp/curl)
 ├── URL is public image gallery → universal-downloader (gallery-dl)
 ├── URL requires login
 │   ├── User OWNS the content → suggest official export FIRST
 │   │   ├── Facebook: facebook.com/dyi
 │   │   ├── Google Photos: takeout.google.com
 │   │   ├── Instagram: Settings → Download Your Information
 │   │   └── If user prefers script anyway → this skill
 │   ├── User does NOT own (shared with them, lost access, etc.)
 │   │   └── this skill — Playbook matching the platform
 │   └── User does not have access at all (banned, removed)
 │       └── STOP. Cannot bypass. Suggest asking the owner.
 └── Unknown platform → Playbook 6 (add new config)
```

---

## Pre-Flight Questions (ask before building)

1. **How many items?** (5-20 = quick custom script; 100+ = use template; 1000+ = warn about rate limits)
2. **Can the user access the page in their own browser right now?** If no → STOP, can't bypass auth.
3. **Does the user own the content?** If yes → suggest official export tool first.
4. **What platform?** → pick matching playbook.
5. **Python installed + comfortable running terminal commands?** Always offer to install missing deps via Bash tool.

---

## Environment Setup

```bash
# Python is required (check first):
python --version

# Install Playwright + browser:
python -m pip install playwright requests
python -m playwright install chromium
```

Both already installed in the user's standard env (verified 2026-05-24). Re-run only if `import playwright` fails.

---

## Why User Must Run the Script (not Claude via Bash)

The script uses `input()` to gate execution behind manual login. If Claude runs it via the Bash tool:
- The Bash tool waits for command exit, which never happens (script blocks on input)
- Tool times out after 2 min, leaving Chromium orphaned
- User can't see the browser window if it's spawned from Claude's process tree

Therefore: **always hand the script to the user with a copy-pasteable PowerShell command, then wait for their report.**

Exception: if the user has a terminal session shared with Claude (tmux, screen, or VSCode integrated terminal piped to Claude), Claude can run the script there. Verify first.

---

## Error Recovery

| Error                                                                | Cause                              | Fix                                                                            |
| -------------------------------------------------------------------- | ---------------------------------- | ------------------------------------------------------------------------------ |
| `Could not find image URL` on every photo                            | Page didn't fully load / wrong page| User: confirm photo is in fullscreen lightbox, not grid view                   |
| Script downloads 1 photo then stops                                  | "Next" selector mismatch           | Inspect element, add correct aria-label to PLATFORM_CONFIGS                    |
| Downloads are 200×200 thumbnails not full-res                        | Wrong `<img>` picked               | Strengthen extraction: filter by `naturalWidth > 800` not `> 400`              |
| `TimeoutError: page.goto`                                            | Slow login / network               | Increase `PAGE_TIMEOUT` to 60_000, or have user navigate manually after login  |
| Loop never ends (more than MAX_PHOTOS)                               | Album has gallery + grid mixed     | Add aggressive dedup: hash image bytes after download, skip duplicates         |
| Facebook shows "Content unavailable"                                 | User actually doesn't have access  | STOP. Verify with user. Suggest reaching out to album owner                    |
| `[SSL: CERTIFICATE_VERIFY_FAILED]` when downloading via `requests`   | MITM proxy in env                  | Add `verify=False` to `requests.get(...)` calls (suppress warning too)         |
| Browser opens but page is blank                                      | Persistent profile corrupted       | Delete `.browser_profile/` and re-run                                          |
| User says "I'm logged in but script can't see album"                 | Cookies didn't transfer            | Confirm user is in the SAME headed Chromium window the script opened (not their main Chrome)|

---

## Post-Download

1. Report file count, total size, output folder
2. Show first 3 filenames for verification
3. Offer next-step actions (organize, rename, compress, upload to Drive, build a gallery/video)
4. **Delete `.browser_profile/`** if the user wants to revoke session — contains login cookies

```bash
ls -la ./downloads | head
du -sh ./downloads
```

---

## Files in This Skill

| File                                  | Purpose                                                 |
| ------------------------------------- | ------------------------------------------------------- |
| `SKILL.md`                            | This file — overview, rules, playbooks                  |
| `templates/album_downloader.py`       | Generic template with PLATFORM_CONFIGS dict             |
| `templates/scroll_collector.py`       | Alternative pattern for infinite-scroll sites (Pinterest, Tumblr)|
| `scripts/check_environment.sh`        | Verifies Python, Playwright, Chromium are installed     |
| `README.md`                           | Quick-start for end users                               |
