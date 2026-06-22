---
name: universal-downloader
description: Download any content from any website — videos (YouTube, Vimeo, TikTok, Twitter/X, Instagram, Facebook, Twitch, 1000+ sites via yt-dlp), audio/music, image galleries (via gallery-dl), single files (curl), playlists, subtitles, live streams, and generic web resources. Use when user says "הורד", "תוריד", "download this", "save this video", "get this file", pastes a YouTube/Vimeo/TikTok/Instagram/Twitter URL, asks to save audio/mp3, rip a playlist, grab subtitles, or download anything from the web. Handles SSL MITM certs, authentication cookies, format selection (best/mp4/mp3), and output organization.
---

# Universal Downloader

Download anything from anywhere — video, audio, images, files, playlists, subtitles.

## Tool Matrix

| Source | Tool | Install |
|--------|------|---------|
| Video platforms (YouTube, Vimeo, TikTok, Twitter/X, Instagram, Facebook, Twitch, Reddit, Bilibili, 1000+ sites) | `yt-dlp` | ✅ installed |
| Audio extraction | `yt-dlp` + `ffmpeg` | ✅ both installed |
| Image galleries (Pixiv, Twitter media, Instagram, Reddit, Pinterest, DeviantArt, 300+) | `gallery-dl` | `pip install gallery-dl` |
| Single files / direct URLs | `curl -L -O` | ✅ installed |
| Large files / segmented | `aria2c -x 16` | `winget install aria2.aria2` |
| Full websites (mirror) | `httrack` or `wget --mirror` | optional |

## Default Output Location

```bash
~/Downloads/web/<category>/<site>/
```

Categories: `video/`, `audio/`, `images/`, `files/`, `playlists/`.

Always `mkdir -p` before download.

## IRON RULES (Windows + Claude Code env)

### RULE 1: Always use `--no-check-certificates` with yt-dlp

**Why:** User's environment has self-signed cert in chain (MITM proxy / antivirus TLS inspection). Without this flag every YouTube/Vimeo/etc download fails with `[SSL: CERTIFICATE_VERIFY_FAILED]`.

```bash
yt-dlp --no-check-certificates <URL>
```

### RULE 2: Use `-o` template with safe filename

YouTube titles contain forbidden Windows chars (`?`, `|`, `：`). yt-dlp handles most but always set explicit template:

```bash
-o "%(title).200B [%(id)s].%(ext)s"
```

`.200B` = byte-length limit (Windows MAX_PATH). `%(id)s` suffix prevents collisions.

### RULE 3: Prefer merged MP4

Default yt-dlp picks separate video+audio streams, merges via ffmpeg. Use:

```bash
-f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" --merge-output-format mp4
```

Falls back gracefully if no MP4 available.

### RULE 4: Don't re-download — use `--download-archive`

```bash
--download-archive ~/Downloads/web/.archive.txt
```

Records downloaded video IDs. Re-running on same playlist skips already-downloaded items.

### RULE 5: Always run in background for large files (>500MB)

Use `run_in_background: true` when ETA shown by yt-dlp > 2 min. Check progress with Read on tool-results file.

---

## Playbooks

### Playbook 1: Single video (YouTube / Vimeo / TikTok / 1000+ sites)

```bash
mkdir -p ~/Downloads/web/video && cd ~/Downloads/web/video
yt-dlp --no-check-certificates \
  -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" \
  --merge-output-format mp4 \
  -o "%(title).200B [%(id)s].%(ext)s" \
  --download-archive ~/Downloads/web/.archive.txt \
  "<URL>"
```

### Playbook 2: Audio only (MP3)

```bash
mkdir -p ~/Downloads/web/audio && cd ~/Downloads/web/audio
yt-dlp --no-check-certificates \
  -x --audio-format mp3 --audio-quality 0 \
  -o "%(title).200B [%(id)s].%(ext)s" \
  "<URL>"
```

`-x` = extract audio. `--audio-quality 0` = best bitrate (VBR).

### Playbook 3: Whole playlist / channel

```bash
mkdir -p ~/Downloads/web/playlists && cd ~/Downloads/web/playlists
yt-dlp --no-check-certificates \
  -o "%(playlist_title)s/%(playlist_index)03d - %(title).150B [%(id)s].%(ext)s" \
  --download-archive ~/Downloads/web/.archive.txt \
  --yes-playlist \
  "<PLAYLIST_URL>"
```

Add `--playlist-items 1-10` to limit range. Add `-I ::5` for every 5th item.

### Playbook 4: Subtitles

```bash
yt-dlp --no-check-certificates \
  --write-subs --write-auto-subs --sub-langs "he,en.*,iw" \
  --convert-subs srt \
  --skip-download \
  -o "%(title).200B [%(id)s].%(ext)s" \
  "<URL>"
```

Remove `--skip-download` to also download the video. `iw` = legacy Hebrew code on some platforms.

### Playbook 5: Private / age-restricted / login-required

```bash
# Step 1 — export cookies from browser (run once, outside Bash):
yt-dlp --cookies-from-browser chrome "<URL>"
# or manual export via browser extension "Get cookies.txt LOCALLY" to cookies.txt

# Step 2 — use cookies file:
yt-dlp --no-check-certificates --cookies ~/cookies.txt "<URL>"
```

`--cookies-from-browser` values: `chrome | chromium | edge | firefox | safari | opera | brave`.

### Playbook 6: Live stream recording

```bash
yt-dlp --no-check-certificates \
  --live-from-start \
  --wait-for-video 30 \
  -o "%(title).200B [%(id)s] %(epoch)d.%(ext)s" \
  "<LIVE_URL>"
```

`--live-from-start` = record from beginning (available only for some DVR-enabled streams).

### Playbook 7: Direct file URL (PDF, ZIP, MP4 link, etc.)

```bash
mkdir -p ~/Downloads/web/files && cd ~/Downloads/web/files
curl -L -O --insecure --retry 5 --retry-delay 2 \
  -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  "<URL>"
```

`-L` = follow redirects. `-O` = save with remote filename. `--insecure` = same reason as yt-dlp rule 1. `-A` = spoof user-agent (some CDNs block curl UA).

For files >500MB with aria2c available:
```bash
aria2c -x 16 -s 16 --check-certificate=false "<URL>"
```

### Playbook 8: Image gallery / profile scraping

```bash
pip install --user gallery-dl  # once
mkdir -p ~/Downloads/web/images && cd ~/Downloads/web/images
gallery-dl --no-check-certificate "<URL>"
```

Supports Pixiv, Instagram, Twitter, Reddit, Pinterest, DeviantArt, ArtStation, Behance, Flickr, Imgur, Tumblr, and more. Config at `~/.config/gallery-dl/config.json`.

### Playbook 9: List formats before download

```bash
yt-dlp --no-check-certificates -F "<URL>"
```

Shows all available resolutions/codecs. Pick format with `-f <code>` (e.g. `-f 137+140` for 1080p video + AAC audio).

### Playbook 10: Twitter / X video

```bash
yt-dlp --no-check-certificates \
  -o "%(uploader)s - %(id)s.%(ext)s" \
  "https://twitter.com/user/status/<ID>"
```

If tweet gated — add `--cookies-from-browser chrome`.

### Playbook 11: Instagram (reels, posts, stories)

```bash
# Needs login for most content:
yt-dlp --no-check-certificates --cookies-from-browser chrome \
  -o "%(uploader)s - %(id)s.%(ext)s" \
  "<INSTAGRAM_URL>"
```

For full profile scraping use `gallery-dl` instead — more reliable.

### Playbook 12: Whole site mirror

```bash
# If httrack available:
httrack "<URL>" -O ~/Downloads/web/mirror --mirror --robots=0

# Or wget (install via: pacman -S wget):
wget --mirror --convert-links --page-requisites --no-parent \
     --no-check-certificate -P ~/Downloads/web/mirror "<URL>"
```

Warning: can be many GB. Always confirm scope with user first.

---

## Decision Tree

```
URL given
 ├── YouTube / Vimeo / TikTok / Twitter / Instagram / Facebook / Twitch
 │   ├── Single item → Playbook 1 (video) or 2 (audio-only)
 │   ├── Playlist/channel → Playbook 3
 │   ├── Subtitle needed → Playbook 4
 │   ├── Login needed → Playbook 5
 │   └── Live → Playbook 6
 ├── Direct file URL (ends .pdf .zip .mp4 .mp3 .iso etc.)
 │   └── Playbook 7
 ├── Image gallery (Pixiv/Twitter/IG profile/etc.)
 │   └── Playbook 8
 └── Whole site
     └── Playbook 12
```

When uncertain which playbook fits: run Playbook 9 (list formats) first — if yt-dlp recognizes the URL, use Playbook 1-6; otherwise fall back to Playbook 7 (curl).

---

## Error Recovery

| Error | Cause | Fix |
|-------|-------|-----|
| `SSL: CERTIFICATE_VERIFY_FAILED` | MITM proxy | Add `--no-check-certificates` (yt-dlp) or `--insecure` (curl) |
| `Sign in to confirm you're not a bot` | YouTube bot detection | Add `--cookies-from-browser chrome` |
| `Video unavailable` | Geo-block | Add `--geo-bypass --geo-bypass-country US` |
| `Private video` | Needs auth | Playbook 5 |
| `Requested format not available` | Asked for specific fmt | Run Playbook 9 first, pick from list |
| `ERROR: unable to rename file` | Long Windows path | Shorten `-o` template; reduce `.200B` to `.100B` |
| `Filename too long` | Title >255 chars | Same — use `.100B` or `.80B` |
| `HTTP Error 403` | Hotlink protection | Add `-A "Mozilla/5.0..."` user-agent |
| Download stalls at Unknown B/s | Segment retry | yt-dlp auto-retries; be patient. If >60s stuck, kill and re-run (archive keeps progress) |

---

## Post-Download

1. Report final file path
2. Show file size (`ls -lh`)
3. For video: mention resolution/codec if non-default
4. For playlists: count items downloaded vs skipped

---

## Install Missing Tools

```bash
# yt-dlp (if missing):
winget install yt-dlp.yt-dlp

# ffmpeg (for merge/audio conversion):
winget install Gyan.FFmpeg

# gallery-dl (for image sites):
pip install --user gallery-dl

# aria2c (fast multi-connection):
winget install aria2.aria2

# wget (site mirroring):
pacman -S wget  # inside git-bash/msys
```

Update yt-dlp often — YouTube breaks extractors monthly:
```bash
yt-dlp -U
```
