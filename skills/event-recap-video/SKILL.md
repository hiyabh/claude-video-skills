---
description: "Produce professional event-recap montage videos from raw photos+clips. TRIGGER on Hebrew: 'סרטון סיכום', 'סרטון של האירוע', 'סרטון מהאירוע', 'ערוך סרטון מהחומרים', 'סרטון מהתמונות', 'סרטון מהקליפים', 'סרטון לאירוע', 'תסכם באירוע בסרטון'. English: 'event recap video', 'event summary video', 'montage from these', 'edit this footage', 'highlight reel'. Use when user provides a folder of mixed JPGs+MP4s from a community/family/school event (march, ceremony, wedding, school play, conference) and wants a single polished cut. Not for AI-generated videos (that's video-production), not for HTML compositions (that's hyperframes)."
---

# Event Recap Montage Video

Professional 1:30–2:30 montage videos edited from raw event photos & clips, using `ffmpeg` directly via a Python orchestrator. Output is a single polished mp4 — no on-screen text, optional music, optional closing logo card.

## When to Use vs Other Video Skills

| Skill | Use For |
|---|---|
| **event-recap-video** *(this one)* | User has REAL photos+videos from an event → polished montage cut |
| `video-production` | User wants AI to GENERATE a video from scratch (script + AI images + TTS) |
| `hyperframes` | HTML/CSS-based animated compositions with synced captions & overlays |
| `remotion-best-practices` | React-driven programmatic video with motion design |

If the user provides a directory of raw event media and wants "ערוך סרטון" / "סרטון סיכום", use THIS skill.

## Mandatory Pre-Flight Questions

Before starting, ask the user (use `AskUserQuestion`):

1. **Aspect ratio** — 16:9 (YouTube/TV), 9:16 (Reels/Status), 1:1 (Instagram), or both
2. **Music** — royalty-free / instrumental / specific YouTube URL / no audio at all
3. **Closing logo** — does the user want a logo card at the end? If yes, ask where the file is

Then proceed autonomously. Do NOT ask which photos/videos to use — make editorial decisions yourself.

## Core Vision (the result the user expects)

The example deliverable the user has approved: **~50s** total, 1920×1080, H.264 + AAC, opens on a 5-photo collage then divides into 4 dramatic acts, no on-screen text, with optional music, ending on a powerful image + 2s logo card.

**Default target duration: 50 seconds** (user directive 2026-05-18, refined from earlier 73s). Only go longer if the user explicitly asks. Tight pacing makes the result feel energetic and shareable.

**Aesthetic principles** — these are non-negotiable defaults:

- **No on-screen text** of any kind (no titles, no captions, no lower-thirds)
- **Open on a collage, not on black** — the first frame is a 5-photo mosaic at full brightness, no intro fade-in. See "Opening Collage" section below.
- **4-act dramatic structure** after the collage — see below
- **Ken Burns on every still** — gentle zoom/pan (1.0→1.15 max), never aggressive
- **Crossfade transitions** — no hard cuts, no wipes, no swipes
- **Pacing varies by act** — slow open, fast climax, slow close
- **Fade-to-black closing only** — no fade FROM black at the start (the collage appears instantly)
- **Music (if any) fades in 2.5s, fades out 3.5s, trimmed to video length**
- **Powerful closing image** — not just any image; pick the most iconic one in the set
- **Optional logo card** — 2s on white background, faded to black at the end

## Structure: Opening Collage + 4 Acts (50s target)

| Section | Duration | Content | Pacing |
|---|---|---|---|
| **0. Opening Collage** | 3.5–4s | 5-photo mosaic — instant appearance, gentle zoom_in_slow, crossfades into Act 1 | `zoom_in_slow`, 0.5s xfade to Act 1 |
| **1. Establishing** | ~16s | Wide shots, the SCALE of the event, the place, the atmosphere | 3 shots — one long video (~7–8s), one wide photo (3s), one anchor video (~5–6s); 0.4s transitions |
| **2. Faces & Detail** | ~13s | Close-ups of faces, hands, expressions — mosaic mode | 5–6 shots — 2.0–2.5s per still, 4.5s for one busy video; 0.3s transitions |
| **3. Climax** | ~7s | The peak — density + action | 4 fast shots — 2.0–2.3s per still; 0.2s transitions |
| **4. Closing** | ~9s | Emotional wind-down, hero image, logo | 2 photos (3.2s + 5.5s, `zoom_in_slow`) → 2s logo card; 0.5–0.7s transitions, fadeblack on logo |

**Total target: ~50s** (community/family events). Total shot count: ~17 (1 collage + 3 + 6 + 4 + 3). Only stretch if user explicitly asks for longer.

### Quick budget math
- Sum of all `dur` ≈ 55.8s
- Sum of all `td[0..N-2]` ≈ 5.8s
- Final duration = sum(dur) − sum(td[0..N-2]) ≈ 50s

## Opening Collage (MANDATORY — every video opens this way)

The first ~3.8s of every output is a 5-photo asymmetric mosaic. The collage:
- Establishes scope ("many people"), emotion (faces/joy), and the climax craft/artifact — all at once
- Eliminates the "fade from black" cold start — the viewer is engaged from frame 0
- Acts as a thumbnail-quality title card without using any text

### Selection rule
Choose 5 photos covering these 5 buckets (one each):
1. **Wide crowd** — establishes scale
2. **Activity / action** — busy scene with multiple people interacting
3. **Joyful face** — a single hero portrait or strong expression
4. **Group of kids/faces** — multiple smiling subjects
5. **Hero craft/artifact** (PORTRAIT preferred) — the climactic image of the event, placed in the large right column

### Layout (1920×1080)
- Left side (2×2 grid, 588×522 tiles): photos 1–4
- Right side (696×1056 hero column): photo 5 (portrait works best here)
- 12px white gaps between every tile

### Build command
```bash
ffmpeg -y -hide_banner -loglevel error \
  -f lavfi -t 1 -i color=c=white:s=1920x1080 \
  -i photo_WIDE_CROWD.jpg \
  -i photo_ACTIVITY.jpg \
  -i photo_JOY.jpg \
  -i photo_GROUP.jpg \
  -i photo_HERO_PORTRAIT.jpg \
  -filter_complex "[1:v]scale=588:522:force_original_aspect_ratio=increase:flags=lanczos,crop=588:522[tl];[2:v]scale=588:522:force_original_aspect_ratio=increase:flags=lanczos,crop=588:522[tr];[3:v]scale=588:522:force_original_aspect_ratio=increase:flags=lanczos,crop=588:522[bl];[4:v]scale=588:522:force_original_aspect_ratio=increase:flags=lanczos,crop=588:522[br];[5:v]scale=696:1056:force_original_aspect_ratio=increase:flags=lanczos,crop=696:1056[hero];[0:v][tl]overlay=12:12[a];[a][tr]overlay=612:12[b];[b][bl]overlay=12:546[c];[c][br]overlay=612:546[d];[d][hero]overlay=1212:12[outv]" \
  -map "[outv]" -frames:v 1 -q:v 2 photo_collage<PHOTO_SUFFIX>.jpg
```

Save with the same `PHOTO_SUFFIX` as the rest of the photos (e.g. `photo_collage_2026-05-18_14-53-58.jpg`) so the template treats it as a regular photo input. A ready-made script lives at [templates/build_collage.py](templates/build_collage.py).

### Adding to SHOT_LIST
The collage is the FIRST entry, with `zoom_in_slow` and a slightly longer fade-out so the transition into Act 1 feels deliberate:
```python
{"type": "photo", "name": "photo_collage", "dur": 3.8, "motion": "zoom_in_slow", "trans": "fade", "td": 0.6},
```

## Implementation Template

A working build script is at [templates/build_video.py](templates/build_video.py). Copy it to the project folder, edit `SHOT_LIST` for the event, and run.

The template handles:
- Auto-detecting orientation (landscape vs portrait sources) and applying blur-pad backgrounds for AR mismatch
- Ken Burns (`zoom_in`, `zoom_in_slow`, `zoom_out`, `pan_left`, `pan_right`, `pan_up`) on stills
- Trim points on video clips (`start` + `dur`)
- Cascading xfade transitions with proper offset math
- **NO intro fade-in** — the video opens instantly on the collage at full brightness
- Final fade-out only (`fadeblack` from logo, varies per closing)
- Logo card support (`type: "logo"`) on white background, no text

## Workflow (every event-recap task)

1. **Inventory** — `ls` the folder, count photos+videos, run `ffprobe` on each video to get duration+resolution
2. **Survey** — quickly view 10–15 photos with the `Read` tool to identify:
   - **5 collage candidates** (wide crowd, activity, joy, group of faces, hero portrait artifact)
   - The widest crowd/establishing shots (Act 1 candidates)
   - The most emotionally powerful close-ups (Act 2 candidates)
   - The most action-packed crowd shots (Act 3 candidates)
   - The most powerful single image (Act 4 closer)
3. **Ask the 3 pre-flight questions** above
4. **Copy templates** to the working folder:
   - `cp ~/.claude/skills/event-recap-video/templates/build_video.py <folder>/`
   - `cp ~/.claude/skills/event-recap-video/templates/build_collage.py <folder>/`
5. **Build the collage** — edit the 5 photo filenames in `build_collage.py` and run `python build_collage.py`. Produces `photo_collage<SUFFIX>.jpg` in 1920×1080.
6. **Edit `SHOT_LIST`** in `build_video.py` — collage is shot 0 (already in template), then ~20–25 shots across 4 acts
7. **Build video** — `python build_video.py` — produces intermediates + final mp4
8. **If audio requested** — download with `yt-dlp -x --audio-format m4a` (or use provided file), then mux with ffmpeg using `afade` filters trimmed to video length
9. **If logo requested** — already handled by the `logo` shot type at end of SHOT_LIST
10. **Verify** — `ffprobe` final file, sample frames at 0.1s (must show full collage, NOT black), middle, and end. Use `Read` to spot-check visually.
11. **Clean up** — remove `_intermediates/`, preview JPGs, `_source_audio.m4a`, and the intermediate `<event>_landscape.mp4` (keep only `<event>_final.mp4`)

## Hard-Won Lessons (don't relearn these)

### Windows + Hebrew paths

`subprocess` on Windows cannot pass Hebrew-character paths to native binaries reliably (mojibake encoding). **Always** `os.chdir(BASE_DIR)` at script top, then pass only **relative filenames** to `ffprobe`/`ffmpeg`. This is already in the template.

### Filename suffixes

Telegram-exported event media usually has a common timestamp suffix like `photo_1_2026-05-13_22-25-35.jpg`. In `SHOT_LIST` use short names (`photo_1`), and define a `PHOTO_SUFFIX` constant that gets appended at file lookup. Videos in the same export typically use the full stem already (`video_2026-05-13_22-25-35 (2).mp4`), so they don't need the suffix.

### zoompan formulas

Use **linear** formulas (`min(1.0+0.15*on/frames,1.15)`), NEVER iterative (`min(zoom+0.0015,1.15)`) — iterative formulas drift with rounding and look unstable. The template uses linear.

### xfade offset math (cascading)

For N intermediates with durations `d[i]` and transition durations `td[i]` between shot i and i+1:
- `offset_i = sum(d[0..i]) - sum(td[0..i-1]) - td[i]`
- The total final duration is `sum(d) - sum(td[0..N-2])` (the last shot's `td` is treated as a closing fade-out, not a between-shot xfade)

This formula is in the template's `build_final`.

### Orientation mismatch → blur pad

A portrait clip in a landscape output (or vice versa) MUST be blur-padded so the frame is fully filled:
```
[0:v]split=2[bg_in][fg_in];
[bg_in]scale=W:H:force_original_aspect_ratio=increase,crop=W:H,boxblur=30:5[bg];
[fg_in]scale=W:H:force_original_aspect_ratio=decrease[fg];
[bg][fg]overlay=(W-w)/2:(H-h)/2
```
Never letterbox to black bars — always blur-pad. Same-orientation sources get a direct scale+crop.

### Audio choices

- "ללא אודיו" / "no audio" → pass `-an` everywhere
- User provides a YouTube URL → `yt-dlp -x --audio-format m4a -o "_source_audio.%(ext)s" <url>`
- The audio is almost always longer than the video — trim to video length and apply `afade` in/out

### Fade durations (the user's stated preferences — updated 2026-05-18)

- **Audio fade-in: 2.5s** (starts at 0, while video already showing the collage at full brightness)
- **Audio fade-out: 3.5s, syncs with the video's fade-to-black**
- **Video fade-in: NONE** — the collage appears instantly at frame 0. The user explicitly asked to remove the intro fade-from-black.
- **Video fade-out: ≥1.5s** into the closing color (black via logo card)

Asymmetric audio vs video on the open is intentional: visually we want immediate engagement, but the audio still ramps in gently.

### Powerful closing image — selection criteria

Not "the last chronologically-shot image". Pick the most **iconic** one in the set. Examples that worked:
- A "sea of [symbols]" wide shot (flags, candles, balloons)
- A child silhouette against sunset
- A hero portrait at the emotional peak
- The most dramatic wide-angle of the crowd/group

Avoid: backs of heads, blurry candids, anything with a parked car in the foreground, anything with mundane background (recycling bins, scaffolding).

### Logo card

- Render at the END of SHOT_LIST as `type: "logo"`, `name: "logo.png"`, `dur: 2.0`, `trans: "fadeblack"`, `td: 1.5`
- Background: pure white (`color=c=white`)
- Logo width: ~45% of frame width, centered
- Preceding shot uses `fadewhite` transition into the logo card for smooth feel
- If logo filename has non-ASCII (Hebrew) characters → copy to `logo.png` first

### Music + Video mux command

```bash
ffmpeg -y -i VIDEO.mp4 -i AUDIO.m4a -map 0:v -map 1:a \
  -c:v copy -c:a aac -b:a 192k \
  -af "afade=t=in:st=0:d=2.5,afade=t=out:st=$((DUR-3.5)):d=3.5" \
  -t $DUR -shortest -movflags +faststart \
  OUTPUT.mp4
```
Replace `$DUR` and `$((DUR-3.5))` with computed values — `bc` isn't on Git Bash on Windows, do math in Python or in the shell as integers.

## Anti-Patterns (don't do these)

- ❌ Adding any on-screen text — titles, captions, dates, names. The user has explicitly rejected this.
- ❌ **Fading in from black at the start.** The user explicitly rejected this on 2026-05-18 — they want the collage visible from frame 0. The template now defaults to no intro fade.
- ❌ **Opening on a single photo or video clip instead of the collage.** The collage is mandatory — it's how every video starts.
- ❌ Using hard cuts. Always use crossfades.
- ❌ Adding emoji or decorative overlays.
- ❌ Aggressive Ken Burns (zoom past 1.20).
- ❌ Mixing photos+video in single ffmpeg filter_complex without intermediate render — leads to encoding inconsistencies and frame jitter at transitions. Always render intermediates first, then xfade them.
- ❌ Asking the user "which photos do you want?" — they trust you to curate. Use the 4-act structure + collage rules to choose.
- ❌ Asking "is this OK?" mid-build — finish, deliver, iterate on feedback.

## Default Output Filenames

- `march_jerusalem_landscape.mp4` style — `<event_short_name>_<format>.mp4`
- For 2-format requests: `<name>_landscape.mp4` + `<name>_vertical.mp4`
- Keep `build_video.py` in the project folder for re-runs.

## Verification Steps Before Delivery

```bash
ffprobe -v error -show_entries format=duration,size \
  -show_entries stream=codec_type,codec_name,width,height \
  -of default=noprint_wrappers=1 <final.mp4>
```

Confirm: correct W×H, ~target duration, both video+audio streams present (or video-only if no-audio requested), file under ~150MB for 1080p ≤2:30.

Extract 2–3 frames at the start, middle, and end with `ffmpeg -ss T -frames:v 1`, then `Read` them to spot-check visually.
