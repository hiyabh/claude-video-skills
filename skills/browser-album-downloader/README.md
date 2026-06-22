# Browser Album Downloader

Skill for downloading photo albums from sites that require login (Facebook private albums, Google Photos shared albums, Instagram private profiles, Pinterest private boards, etc.) — when `yt-dlp` and `gallery-dl` from the `universal-downloader` skill cannot.

## When This Skill Activates

Triggers on: "תוריד אלבום", "הורד תמונות מ-Facebook", "download private album", "Google Photos shared album", "אין לי גישה לדף", and similar requests for downloading authenticated/gated photo content.

## Quick Start

1. Verify environment: `bash scripts/check_environment.sh`
2. Copy template: `cp templates/album_downloader.py <project>/download_album.py`
3. Edit `ALBUM_URL` and `PLATFORM` at the top of the script
4. User runs in their own PowerShell:
   ```
   cd <project>; python download_album.py
   ```
5. User logs in manually in the opened Chromium window
6. User navigates to first photo, presses ENTER in terminal
7. Script downloads all photos to `./downloads/`

## Why a Separate Skill from `universal-downloader`?

| `universal-downloader`                                | `browser-album-downloader` (this skill)              |
| ----------------------------------------------------- | ---------------------------------------------------- |
| Public content via yt-dlp / gallery-dl / curl         | Private content via real browser + manual login      |
| Headless, automated, one command                      | Headed browser, interactive, requires user terminal  |
| Works for 99% of YouTube/Vimeo/Twitter/public IG      | Required for FB private albums, Google Photos shares |
| Cannot bypass login walls                             | Reuses user's manual session                         |

## Files

- `SKILL.md` — full instructions, IRON RULES, playbooks per platform
- `templates/album_downloader.py` — generic "next photo" walker template
- `templates/scroll_collector.py` — infinite-scroll variant (Pinterest, Tumblr)
- `scripts/check_environment.sh` — environment verification
- `README.md` — this file

## Supported Platforms (built-in configs)

- Facebook (private albums, message-attached `ms.c...` URLs, post-attached `pcb.<id>`)
- Instagram (private profiles, saved posts)
- Google Photos (shared albums)
- Pinterest (private boards — uses scroll pattern)
- Tumblr (private blogs — uses scroll pattern)
- Generic fallback (`ArrowRight` keyboard navigation, any large image)

## Adding a New Platform

See `SKILL.md` → Playbook 6. Identify the "next" selector and image CDN domain, add an entry to `PLATFORM_CONFIGS` in the template.

## Privacy & Safety

- Claude never sees credentials — user logs in manually in browser window
- Session cookies stored in `<project>/.browser_profile/` — delete to revoke
- Polite rate limiting: 1.2-2.5s between photos (avoids ban)
- Two manual checkpoints (start, end) — user always in control

## When NOT to Use

- Public videos / public image galleries → use `universal-downloader` instead
- Content the user has **no access to at all** → cannot bypass, suggest contacting the owner
- Bulk scraping for resale / copyright violation → refuse and explain

## Provenance

Originally extracted from a successful Facebook album download session (2026-05-24, 112 photos from a private album). Generalized into a reusable skill at user request.
