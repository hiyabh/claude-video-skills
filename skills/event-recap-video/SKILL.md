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
| `talking-head-fx` (skills hub) | One person talking to camera (a reel, a speech clip) → face-aimed zooms, captions, reel effects |

If the user provides a directory of raw event media and wants "ערוך סרטון" / "סרטון סיכום", use THIS skill.

## Mandatory Pre-Flight Questions

Before starting, ask the user (use `AskUserQuestion`):

1. **Aspect ratio** — 16:9 (YouTube/TV), 9:16 (Reels/Status), 1:1 (Instagram), or both.
   **If the user doesn't answer / autonomous session: default to 9:16 vertical** (user directive 2026-07-14 — community videos are shared on WhatsApp status/groups).
2. **Music** — royalty-free / instrumental / specific YouTube URL / no audio at all.
   **For kids/family events default to upbeat children's instrumental** ("מוזיקת ילדים קצבית", user preference 2026-07-14 — chosen over klezmer and Hava Nagila). Find via `yt-dlp "ytsearch3:..." --print title` to audition candidates by title/duration first.
3. **Closing logo** — does the user want a logo card at the end? If yes, ask where the file is

Then proceed autonomously. Do NOT ask which photos/videos to use — make editorial decisions yourself. In a non-interactive/autonomous session skip the questions entirely and use the defaults above.

## Core Vision (the result the user expects)

The example deliverable the user has approved: opens on a 5-photo collage then divides into 4 dramatic acts, H.264 + AAC, no on-screen text beyond the collage title, with music, ending on a powerful image + 2s logo card. **Default frame: 1080×1920 vertical (9:16)** — user directive 2026-07-14; 1920×1080 only when explicitly requested.

**Default target duration: 50 seconds** (user directive 2026-05-18, refined from earlier 73s). Only go longer if the user explicitly asks. Tight pacing makes the result feel energetic and shareable.

**When the user asks for "חצי דקה" / ~30s, use the proven compact structure** (delivered and approved 2026-07-14): ~13 shots, final ≈ 30–32s — see "Compact 30s variant" below. Adding a shot later (user iteration) may stretch it to ~32s; that's fine.

**Aesthetic principles** — these are non-negotiable defaults:

- **One title, on the collage only** — a beautiful poster-style Hebrew title is baked onto the opening collage (event name + community). This is the ONLY on-screen text (user directive 2026-07-07). No captions, lower-thirds, dates, or names anywhere else — the 4 acts stay text-free.
- **Open on a collage, not on black** — the first frame is a 5-photo mosaic at full brightness, no intro fade-in. See "Opening Collage" section below.
- **4-act dramatic structure** after the collage — see below
- **Ken Burns on every still** — gentle zoom/pan (1.0→1.15 max), never aggressive
- **Animated effect transitions — ALWAYS (user directive 2026-09-06: "תמיד לעשות מעברים מיוחדים עם אפקטים").** Every junction gets a different effect from `transitions.py` (spin, roll, flip, punch, pinwheel, whip, bounce, heartbeat pulses on stills) via `build_video_dramatic.py`. This is the default build path for every recap, not an option to be asked about. Plain `xfade` crossfades/wipes were rejected as "not impressive" and are only for the closing dip to black (`fadeblack`). See "Dramatic Mode" below.
- **Pacing varies by act** — slow open, fast climax, slow close
- **Fade-to-black closing only** — no fade FROM black at the start (the collage appears instantly)
- **Music (if any) fades in 2.5s, fades out 3.5s, trimmed to video length** — but if the track is offset to a beat drop, shorten the fade-in to ~1.2s (see "Never mux a track from t=0 without measuring its intro")
- **Powerful closing image** — not just any image; pick the most iconic one in the set
- **Optional logo card** — ~2s, logo on a BLACK background, faded to black at the end (blends seamlessly). **Size PROPORTIONALLY: `min(62% of frame width, 40% of frame height)`** — a round/tall logo at 70% width clips outside a 16:9 frame (user caught this 2026-07-14). The template now enforces the cap.
- **Persistent corner logo** — by DEFAULT, overlay the logo as a small watermark (~14% width) in one corner for the ENTIRE video, in addition to the end card (user directive 2026-07-07). See "Persistent Corner Logo (Watermark)".

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

### Compact 30s variant (approved 2026-07-14 — use when the user asks for "חצי דקה")

~13 shots, budget: sum(dur) ≈ 35–37s, sum(td) ≈ 4.3–4.6s, final ≈ 30–32s:

| Section | Shots | Durations |
|---|---|---|
| 0. Collage | 1 | 3.5s, 0.5s xfade |
| 1. Establishing | 3 (video ~4.5s, wide photo 2.5s, video ~4s) | 0.35–0.4s transitions |
| 2. Faces & show | 4 (photo 2.3s, video 3.5s, 2 photos 2.2–2.3s) | 0.3–0.35s transitions |
| 3. Climax (food/action + happy faces) | 3 stills, 2.2–2.3s each | 0.3–0.35s transitions |
| 4. Closing | hero photo 3.0s `zoom_in_slow` → logo card 2.2s | `fadeblack` 0.7s → 1.5s |

## Opening Collage (MANDATORY — every video opens this way)

The first ~3.8s of every output is a 5-photo asymmetric mosaic. The collage:
- Establishes scope ("many people"), emotion (faces/joy), and the climax craft/artifact — all at once
- Eliminates the "fade from black" cold start — the viewer is engaged from frame 0
- Carries the poster-style opening title (see "Opening Title" below) — the collage IS the title card

### Selection rule
Choose 5 photos covering these 5 buckets (one each):
1. **Wide crowd** — establishes scale
2. **Activity / action** — busy scene with multiple people interacting
3. **Joyful face** — a single hero portrait or strong expression
4. **Group of kids/faces** — multiple smiling subjects
5. **Hero craft/artifact** (PORTRAIT preferred) — the climactic image of the event, placed in the large right column

### Layout — vertical 9:16 (1080×1920, THE DEFAULT — user directive 2026-07-14)
- Top hero tile (1056×956): photo 5 — the iconic portrait moment
- 2×2 grid below (522×458 tiles): photos 1–4
- 12px white gaps between every tile
- `templates/build_collage.py` has both layouts behind an `ORIENTATION` switch

### Layout — landscape 16:9 (1920×1080, only when the user asks)
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

## Opening Title (MANDATORY — baked onto the collage)

After building the plain collage, bake a **poster-style Hebrew title** onto it with
[templates/add_collage_title.py](templates/add_collage_title.py). This is the only
on-screen text in the whole video (user directive 2026-07-07); the 4 acts stay clean.

The titler:
- Renders Hebrew **RTL-correct** via `python-bidi` (`get_display`) — never draw Hebrew
  with raw ffmpeg `drawtext`/PIL, it comes out reversed. `pip install pillow python-bidi`.
- Uses **Rubik-Bold** (rounded modern Hebrew display face) — swap for any Hebrew TTF/OTF.
- Composites a **bottom gradient scrim + radial glow** so photos stay vivid and letters pop.
- Three stacked lines, all sizes scale with frame width (works for 9:16, 16:9, 1:1):
  - `EYEBROW` — small gold kicker (e.g. the event category, "הפנינג")
  - `TITLE_LINES` — the big title, one list entry per line (YOU control the breaks)
  - `SUBTITLE` — soft-white community/organization name
- White title with dark stroke + soft drop shadow; gold eyebrow with airy letter-tracking.

It **overwrites the collage in place**, so the order is always:
`build_collage.py` → `add_collage_title.py` → `build_video.py`. Re-tuning the title means
re-running `build_collage.py` first (to restore the plain base). The baked title then rides
the collage's `zoom_in_slow` for a subtle, deliberate open. Always `Read` the titled collage
to confirm the Hebrew reads correctly (right-to-left, connected words) before rendering.

## Implementation Template

**The default builder is [templates/build_video_dramatic.py](templates/build_video_dramatic.py)** (with `transitions.py`, `analyze_clips.py`, `mix_music.py`) — see "Dramatic Mode" below. Copy it to the project folder, edit `SHOT_LIST`, and run.

[templates/build_video.py](templates/build_video.py) is the older xfade-only builder. Keep it only for re-running past projects that were built with it; do NOT start a new recap from it (user directive 2026-09-06). The rendering helpers it documents (orientation, blur-pad, Ken Burns, logo card) are shared by the dramatic builder:
- Auto-detecting orientation (landscape vs portrait sources) and applying blur-pad backgrounds for AR mismatch
- Ken Burns (`zoom_in`, `zoom_in_slow`, `zoom_out`, `pan_left`, `pan_right`, `pan_up`) on stills
- Trim points on video clips (`start` + `dur`)
- Cascading xfade transitions with proper offset math
- **NO intro fade-in** — the video opens instantly on the collage at full brightness
- Final fade-out only (`fadeblack` from logo, varies per closing)
- Logo card support (`type: "logo"`) on white background, no text
- `pulse` motion on stills — a heartbeat zoom (`1.06 + 0.07·e^(−6·(t mod 1.5)/1.5)`), one swell every `PULSE_PERIOD_SEC`. Use it on 1–2 stills per cut (never on every still) when the user wants "פעימות".

## Dramatic Mode — animated transitions + the clips' own sound (2026-09-06) — THE DEFAULT

**Always on.** Every recap is built this way, whether or not the user mentions effects
(directive 2026-09-06: "תמיד לעשות מעברים מיוחדים עם אפקטים"). The clip-audio timeline is
part of the same builder: keep the clips' sound whenever the clips have meaningful audio
(prayer, singing, speeches, cheering); mute it (no `a_lead`/`a_tail`, music only) when the
clips are just wind and chatter.

Built for the Selichot-at-Machpela recap after the user rejected the xfade cut:
*"זה צריך להיות מרשים גם במעבר… תמונה מתגלגלת החוצה, מתגלגלת פנימה, פעימות, סיבובים,
הופעה היעלמות, אפקטים אפקטים אפקטים"* — and *"אני רוצה לשמוע מתוך הסרטונים את התפילה
והצעקות"*. The templates:

| file | role |
|---|---|
| [templates/transitions.py](templates/transitions.py) | 12 frame-by-frame Pillow effects + easing curves |
| [templates/build_video_dramatic.py](templates/build_video_dramatic.py) | renders full intermediates → bodies + transition clips → concat; builds an explicit clip-audio timeline |
| [templates/analyze_clips.py](templates/analyze_clips.py) | "listen" to every clip: RMS per 0.5s (+ whisper transcript when it is speech) |
| [templates/mix_music.py](templates/mix_music.py) | music bed under the clip audio on a PLANNED dB envelope (no sidechain — see "Three traps") |

### The effect catalog (`transitions.EFFECTS`)

| name | what the viewer sees | good for |
|---|---|---|
| `spin_in` | B spins in from a dot at the centre (two turns), A recedes and dims | collage → first clip |
| `roll_out_left` | A rolls off the left edge like a wheel (−380°), B waits underneath | clip → wide photo |
| `roll_in_right` | B rolls in from the right, spinning, settles with overshoot | photo → clip |
| `rise_tilt` | B rises from below tilted −14°, straightens with a soft overshoot | photo → photo |
| `punch_in` | B slams in from 1.75× with an elastic pulse; A blows out in blur | into a loud clip |
| `flip_h` | card flip about the vertical axis (A squeezes to a line, B unfolds) | photo → photo |
| `pinwheel` | A spins away clockwise shrinking, B spins in counter-clockwise growing | clip → clip |
| `whip_left` | both frames rush left with horizontal motion blur | fast, into a climax |
| `shrink_spin_out` | A spins 540° into the centre and vanishes over a waiting B | into the hero closer |
| `drop_bounce` | B drops from the top and bounces into place | playful events |
| `zoom_blur_cross` | A rushes into the lens and dissolves, B lands from a blurred zoom | dreamy, slower |
| `split_reveal` | A tears into top/bottom halves that slide apart, B behind | photo → photo |
| `rotate_zoom_in` | B grows from 0.3× while un-tilting from −25°, soft overshoot | photo → photo |
| `cube_left` | pseudo-3D cube turn: A squeezes out left, B unfolds from the right | photo → photo |
| `spin_drop_out` | A tumbles down out of frame spinning (−200°), B waits behind | photo → photo |
| `iris_open` | B revealed through a growing soft-edged circle while straightening | into a landmark / hero |
| `fadeblack` | dip to black | into the logo card |
| `whip_right` / `whip_up` | whip pan right / whip tilt up with motion blur | fast cuts |
| `push_up` / `push_right` | clean push, B shoves A out of frame | fast cuts |
| `slide_over_down` | B slides down over a dimming A | fast cuts |
| `zoom_through` | A rushes into the lens and burns out, B settles | fast cuts |
| `flash_white` | camera flash: A blows out to white, B emerges | fast cuts, beat hits |
| `slice_in` | B arrives in 8 horizontal strips from alternating sides | fast cuts |

25 effects. A cut up to 26 shots can use each one once. Longer cuts: add an effect (one
function) before repeating one. When a repeat is unavoidable, keep ≥ 8 junctions between uses.

**"Use all the photos" still means no near-duplicates in a row (2026-09-23).** Two phones often
shoot the same scene from the same spot. 28/29 (the audience from behind) went in back to back and
the user caught it as a duplicate. Before an all-photos cut, correlate every pair of sources
(24×24 gray, normalised). If a pair scores ≥ ~0.7, check it by eye, and keep the twin in the
collage only, so "every photo appears" still holds. Afterwards, locate each photo inside the
DELIVERED mp4 (best-correlating frame at 10fps). The order of the hits must match `SHOT_LIST`.

**Fast mode (2026-09-23, "תעביר יותר מהר, מעברים מהירים"; also "use all the photos").**
Stills 1.4s, transitions 0.3-0.45s, so 31 photos + 4 clips come to ~47s. At 9-13 frames the
rotating effects flicker, so the 8 fast effects above (translation and light, no rotation) carry
most of the junctions. Rotations get 0.45-0.5s and appear only every few junctions. **Pick `td`
values that are whole frames (multiples of 1/30s, e.g. 0.3, 0.4, 0.5, or 0.333).** 0.35 and 0.45
are half frames: every body and transition rounds down, and 36 junctions drifted the cut
16 frames (0.5s) short of `shot_starts()`. That is harmless with music only, but it desyncs
clip audio.

Rules that came out of the first use:
- **Never repeat an effect in one cut** — 8 junctions, 8 different effects. The variety IS the request.
- **Durations 0.6–0.8s** for anything that rotates (spin/roll/pinwheel need the time to read); 0.5s for `whip_left`; 0.7s for `fadeblack`. Below 0.5s a rotation is just a flicker.
- **A rotating frame carries its blur bands with it** — a blur-padded landscape still rotates as the whole 9:16 frame, black corners show behind. That is fine and reads as a "card"; do not try to crop it.
- **Verify with a contact sheet, not single frames**: 6 frames across every transition, one row per junction (the driver code is in the 2026-09-06 journal). A single mid-frame hides a bad ease.
- Easings live in `transitions.py`: `ease_out_back` (overshoot) for anything that "settles", `ease_out_bounce` for drops, `ease_out_elastic` for punches, `ease_in_cubic` for exits.
- Adding an effect = one function `fx_name(a_rgba, b_rgba, p) -> RGBA` using `transform()` (scale/xscale/angle/alpha/blur/hblur/brightness) + `paste_center(canvas, im, dx, dy)`, registered in `EFFECTS`. ~200 frames of 1080×1920 render in ~40s.

### How the dramatic builder assembles the cut

1. Every shot renders to a full-length silent intermediate exactly as in `build_video.py` (`-frames:v` pins the frame count).
2. For junction *i* the tail `td` of shot *i* and the head `td` of shot *i+1* are extracted as PNG sequences, composited by the effect, and encoded as a short clip.
3. Each shot's **body** is the intermediate minus its incoming and outgoing transition portions (`-ss head -frames:v N`); the closing fade is applied to the last body.
4. Bodies and transition clips are joined with the **concat demuxer** (`-c copy`, all encoded with identical params). Timeline math is xfade-identical: `T[i+1] = Σdur[0..i] − Σtd[0..i]`, so `shot_starts()` is the single source of truth for both video and audio.
5. Check `nb_frames == round(total·FPS)` — it must match exactly (1077 = 35.9s × 30 on the first run).

### "Listen to the clips" — the prayer/speech is the soundtrack

When the user wants to hear what happens IN the clips, the clips' audio becomes the lead
and music is only a bed. Run `python analyze_clips.py` first and write the strong
windows next to each clip stem in the builder (e.g. `A: strongest chant 12.5–18`,
`B: loud 0–7.7 then silence`). Whisper does not transcribe singing — the **RMS profile
is the tool**; look for sustained loud stretches, "breath" dips, and dead tails.

Then place the audio on an explicit timeline with **J-cuts and L-cuts** using two keys on
each video shot:
- `a_lead` — seconds of the clip's audio played BEFORE the shot appears (source window
  starts at `start − a_lead`). Opening the film with the chant already under the collage
  (`a_lead: 2.0`, shot `start: 2.0`) is the strongest use.
- `a_tail` — seconds the audio keeps running AFTER the shot, under the following stills,
  until the next clip's audio takes over (crossfade `CLIP_XFADE`, 0.6s).

**Order the shots so the audio budget works out.** Total clip audio is finite (28s on the
Selichot job vs a 36s cut): clips + stills that share a clip's audio must be adjacent, and
the closing stills can sit on music alone as the wind-down. The builder asserts that every
window fits inside its source. Aim for one continuous stretch of clip audio (1.0→28.0s
there) rather than islands.

Levels: clips are gain-matched to `CLIP_LOUDNESS_LUFS = −14` (measured with `ebur128`,
applied with `volume` + `alimiter`), then `mix_music.py` adds the bed on a **planned dB
envelope** (`ENVELOPE_DB` breakpoints, linear ramps, `volume=…:eval=frame`): open −21 dB
under the collage, −30 dB under the chant, −20 dB on the music-only closing montage, then a
3.5s fade to −50 dB synced with the fade to black. Envelope values are **gain** applied to
the track — measure the track's mean with `volumedetect` first (this one sat at −12.5) and
set `gain = wanted level − mean`. Result: chant −13…−16 dB, closing bed −18…−25 dB, −14.7 LUFS.
The earlier `−9 dB` bed with a softer duck was rejected as *"שומעים המון מוזיקה"*; the
sidechain version that followed was rejected as pumping (see below).

**Verify smoothness with a 0.25s RMS scan** of the delivered file and list every >4 dB step
between adjacent windows. Steps inside the chant are the singing's own dynamics; steps in
the music-only stretch must be only the track's musical accents (≤ ~5 dB) and the planned
ramps. Anything else is a mix bug.

### "המעברים לא חלקים" — a freeze + jump inside transitions (2026-10-20, fixed in templates)

The user reported the transitions as not smooth, mostly at the start. A per-frame diff scan of
the delivered file found **6-10 identical frames in the second half of each transition, then a
one-frame jump**. Each transition clip was smooth on its own. There were two causes, and both are now
fixed in the templates:
1. **B-frames + concat `-c copy`:** every x264 part starts at DTS −0.067s, so the concat
   overlaps each part with the previous one and the muxer re-times frames. `VENC` now has `-bf 0`.
2. **`-loop 1` on the watermark logo** (a 25fps still) made `overlay` + `-r 30` duplicate and drop
   frames at the same spots. `add_watermark.py` now passes the logo without `-loop`, and `overlay`
   repeats the single frame by itself.

Also: the `pulse` motion snaps from zoom 1.06 to 1.13 at every period. Measured as an 18-unit
jump after frozen frames, it reads as a jerk, so avoid it when the user wants smoothness.
**Verify every delivery with the freeze scan:** decode at 108×192 gray, `np.abs(np.diff)`.
Any run of 3+ frames below 0.15 before the closing fade is a bug.

### Four traps found while building it

- **Sidechain ducking PUMPS under live singing (2026-09-06, round 4).** `sidechaincompress`
  keyed by the clip audio lets the music jump up in every breath of the chant and squash back
  down a moment later; the user heard it as *"משהו צורם שהולך וחוזר ונקטע"*. A planned
  envelope cannot react, so it cannot pump — that is why `mix_music.py` uses breakpoints, not
  a compressor. Also fade to −50 dB, not −80: a 60 dB drop over 3.5s reads as a cut.

- **Single-pass `loudnorm` breaks `adelay`.** Its 3s look-ahead re-times the stream: the
  segment plays from t=0 instead of from its delay, and `asetpts=N/SR/TB` does NOT fix it.
  Measure with `ebur128` and apply `volume=XdB,alimiter` instead (that is what
  `measure_lufs()` does). Verify placement with
  `silencedetect` on the audio track — the sound must start exactly at the planned second.
- **concat demuxer paths are relative to the list file, not to cwd.** Write entries as
  `relative_to(INTER)` when the list lives in `_intermediates/`.
- **`xfade=zoomin` (and any centre-zoom effect) zooms into whatever sits in the middle of
  the outgoing frame.** On the collage that was a red keyboard bag → a solid red frame.
  Check the centre of the outgoing frame before using centre-zoom effects.

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
   - `cp ~/.claude/skills/event-recap-video/templates/{build_video_dramatic.py,transitions.py,analyze_clips.py,mix_music.py} <folder>/` (the default builder — always)
   - `cp ~/.claude/skills/event-recap-video/templates/build_collage.py <folder>/`
   - `cp ~/.claude/skills/event-recap-video/templates/add_collage_title.py <folder>/`
   - `cp ~/.claude/skills/event-recap-video/templates/add_watermark.py <folder>/`
   - `cp ~/.claude/skills/event-recap-video/templates/organize_folder.py <folder>/`
5. **Build the collage** — edit the 5 photo filenames in `build_collage.py` and run `python build_collage.py`. Produces `photo_collage<SUFFIX>.jpg`.
6. **Bake the title** — edit `EYEBROW`/`TITLE_LINES`/`SUBTITLE` in `add_collage_title.py`, run `python add_collage_title.py`, then `Read` the result to confirm the Hebrew reads right-to-left. See "Opening Title" above.
7. **Edit `SHOT_LIST`** in `build_video.py` — collage is shot 0 (already in template), then ~20–25 shots across 4 acts
   - Run `python analyze_clips.py` first, then set `trans` per junction from the effect catalog (**a different effect at every junction, always**) and `a_lead`/`a_tail` on the video shots whose sound should be heard. See "Dramatic Mode".
8. **Build video** — `python build_video_dramatic.py` — produces intermediates, transition clips, the clip-audio timeline and the master mp4. Verify the transitions with a contact sheet (6 frames per junction) before moving on.
9. **If audio requested** — download with `yt-dlp -x --audio-format m4a` (or use provided file), then mux with ffmpeg using `afade` filters trimmed to video length. If yt-dlp returns **HTTP 403**, retry with `--extractor-args "youtube:player_client=android,web"` (worked 2026-09-06). The music is added by `mix_music.py` (ducked under the clip audio); use the plain mux only when the clip audio is deliberately muted.
10. **Persistent corner logo (MANDATORY)** — run `add_watermark.py` on the muxed master to overlay the logo in a corner for the whole video. See "Persistent Corner Logo (Watermark)". (The `logo` shot type still adds the big end card — both coexist.)
11. **Verify** — `ffprobe` final file, sample frames at 0.1s (must show the titled collage, NOT black), middle, and end. Use `Read` to spot-check visually — especially that the title Hebrew is correct.
12. **Clean up** — remove `_intermediates/`, preview JPGs, `_source_audio.m4a`, and the intermediate silent `<event>.mp4` (keep only the final muxed mp4)
13. **WhatsApp-light export (MANDATORY)** — transcode the final mp4 to a small, share-friendly copy (~10MB) so it sends without heavy WhatsApp re-compression. Name it `<deliverable> (ווטסאפ).mp4` (the `ווטסאפ` keyword keeps it in the root during organize). See "WhatsApp-light Export" below.
14. **Organize the folder (MANDATORY final step)** — edit `FINAL_VIDEO` in `organize_folder.py` and run `python organize_folder.py`. It sorts the project into `תמונות גלם/` (source photos), `סרטוני גלם/` (source clips), `סקריפטים/` (all `.py` + logos), and **leaves only the deliverable mp4, the WhatsApp-light copy, the titled `photo_collage*.jpg`, and the event flyer (`פרסום*`) in the root**. See "Folder Organization" below.

## WhatsApp-light Export (MANDATORY — after every recap)

WhatsApp aggressively re-compresses large videos. Ship a small copy alongside the
full-quality deliverable so it sends fast and stays crisp (user directive 2026-07-07).
Downscale to 720p-tall, higher CRF, 128k audio, faststart:

```bash
ffmpeg -y -i "<deliverable>.mp4" -vf "scale=720:1280:flags=lanczos" \
  -c:v libx264 -profile:v main -level 4.0 -preset slow -crf 28 -pix_fmt yuv420p \
  -c:a aac -b:a 128k -movflags +faststart "<deliverable> (ווטסאפ).mp4"
```

- For a 16:9 deliverable use `scale=1280:720`; for 1:1 use `scale=720:720`.
- Target ≤16MB (WhatsApp's friendly ceiling). If it lands larger, bump `-crf` to 30.
- Keep the `ווטסאפ` (or `whatsapp`) keyword in the filename — `organize_folder.py`
  keeps such files in the root instead of filing them under `סרטוני גלם/`.

## User-supplied logo and music (not shipped with this skill)

This bundle ships NO logo and NO music tracks. Both are inputs you provide per project:

- **Logo / watermark:** put your own transparent PNG in the project folder as `logo.png` (ASCII name),
  or change `LOGO` at the top of `templates/add_watermark.py` (and the `logo` shot's `name` in
  `build_video_dramatic.py`) to any file you have. Corner, size, padding and opacity are the
  constants `CORNER`, `SIZE_RATIO`, `PAD_RATIO`, `OPACITY`. No logo? Drop the `logo` shot from
  `SHOT_LIST` and skip `add_watermark.py`.
- **Music:** download or pick a royalty-free track yourself, place it in the project folder, and set
  `MUSIC` (and `MUSIC_ENTRY_SEC`) at the top of `templates/mix_music.py`. No music? Skip
  `mix_music.py` and keep the clip audio only.
- **Requirements:** `ffmpeg` on PATH and `pip install pillow numpy python-bidi` (analyze_clips, transitions and the collage title import them).
- **Folder paths:** every template resolves its working folder from `BASE_DIR` (default
  `./event-media`, or the script's own folder for the dramatic builder). Set it to your event folder.

## Persistent Corner Logo (Watermark)

By default, every recap carries the logo as a small, semi-transparent watermark in
one corner for the ENTIRE video — on top of the big logo card at the end (user
directive 2026-07-07). Apply it with [templates/add_watermark.py](templates/add_watermark.py)
on the muxed master (it re-encodes the video, copies the audio):

```bash
# equivalent one-liner (W = frame width; PAD/logo size scale with it)
ffmpeg -y -i "<master>.mp4" -loop 1 -i logo.png -filter_complex \
  "[1:v]scale=W*0.14:-1:flags=lanczos,format=rgba,colorchannelmixer=aa=0.88[wm];\
   [0:v][wm]overlay=main_w-overlay_w-PAD:PAD:format=auto,format=yuv420p[vout]" \
  -map "[vout]" -map 0:a? -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
  -c:a copy -movflags +faststart -shortest "<master>_wm.mp4"
```

- **Placement**: default top-right (`CORNER='tr'`); `tl`/`br`/`bl` also supported. Pick the
  corner that stays clearest of faces/action for the specific event.
- **Size** ~14% width, **opacity** ~0.88, **padding** ~3.5% width — small enough not to
  distract, visible enough to brand every frame.
- A **transparent-background** logo works best. A light/white mark reads over most footage;
  add a soft dark plate behind it if the footage is very bright.
- **Order**: build → mux audio → **watermark** → WhatsApp export (so the light copy is also
  watermarked) → organize. Applying it once, after mux, means a single extra re-encode.
- The end **logo card** (big, on black) is separate and still used — the watermark brands the
  body, the card closes the film.

## Folder Organization (MANDATORY — after every recap)

Once the video is delivered and verified, always tidy the project with
[templates/organize_folder.py](templates/organize_folder.py) (user directive 2026-07-07).
Final layout:

```
<root>/
  01 - <event>.mp4          # the finished recap video   — stays in root
  photo_collage<SUFFIX>.jpg  # the titled opening collage  — stays in root
  פרסום.jpeg                 # the event flyer / promo      — stays in root
  תמונות גלם/                # all source photos
  סרטוני גלם/                # all source video clips
  סקריפטים/                  # build_*.py, add_collage_title.py, organize_folder.py, logos
```

Rules baked into the script: the deliverable, any `photo_collage*`, and any file whose
name contains a flyer keyword (`פרסום` / `פלאייר` / `flyer`) stay in the root; `.py` files
and logo images go to `סקריפטים/`; videos to `סרטוני גלם/`; all other images to `תמונות גלם/`.
Idempotent and safe to re-run. Note: re-running the build scripts afterward needs the
photos/clips back in the root, so organize only once the deliverable is final.

**Revision rounds start by UN-organizing (2026-08-11).** The user almost always comes back with
notes, and the build scripts resolve everything relative to `BASE_DIR`. First command of any
follow-up round:
```bash
mv "תמונות גלם"/*.jpg . ; mv "סקריפטים"/*.py "סקריפטים"/logo.png .
```
This also restores any hand-made crops (`photo_v_*.jpg`) — reuse them, don't re-cut. Keep every
music track that was ever used, named with its BPM (e.g. `מוזיקת רקע - ילדים קצבית 143BPM.m4a`
alongside `... 123BPM (סבב 1).m4a`), so reverting to an earlier track is a 1-minute audio swap
with no re-render.

**"Remove the photos at seconds X,Y,Z" (2026-10-20): map every second to a photo by its frames.**
Extract frames at X.0 and X.5 from the delivered file, read them, and list *second → photo* back
to the user. Each listed second normally means one distinct photo. If two adjacent seconds
(32, 33) still show the same still, the later one means the photo that comes in next. State
that reading explicitly so it can be corrected. After removal, re-assign the outgoing effect
at the new junctions so that every junction stays unique. Report the new runtime too, because 5
stills less turned a 49.5s cut into 42s.

## Hard-Won Lessons (don't relearn these)

### Windows + Hebrew paths

`subprocess` on Windows cannot pass Hebrew-character paths to native binaries reliably (mojibake encoding). **Always** `os.chdir(BASE_DIR)` at script top, then pass only **relative filenames** to `ffprobe`/`ffmpeg`. This is already in the template.

**Set `BASE_DIR = Path(__file__).resolve().parent` instead of pasting the Hebrew path (2026-08-11).**
The scripts live inside the event folder, so this is always correct — and it removes the need to
write the Hebrew folder name into any file. Configuring the templates by editing that literal is
where the encoding breaks: a `python - <<'EOF'` heredoc in Git Bash mangles Hebrew string
literals into `????` and the patch silently fails to match.

Two more Git Bash traps when writing configurator scripts:
- **Windows paths in Python string literals need `r'...'`** — `'c:\Users\...'` raises
  `SyntaxError: (unicode error) ... truncated \UXXXXXXXX escape` because `\U` starts an escape.
- If a heredoc must carry Hebrew, write the file with the `Write` tool (UTF-8) and run it,
  or use `\uXXXX` escapes. Do not pipe Hebrew through a heredoc.

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

**Shrink the bands by cutting a 3:4 crop first — but only on intimate shots (2026-08-11).**
In a 1080×1920 frame the blur bands are brutal for landscape stills:

| source | photo occupies | blur band top/bottom |
|---|---|---|
| 16:9 (1280×720) | 1080×608 | **656 px each** |
| 4:3 (1280×960) | 1080×810 | 555 px each |
| 3:4 crop (540×720) | 1080×1440 | **240 px each** |

So `ffmpeg -i photo.jpg -vf "crop=540:720:X:0"` around the subject cuts the wasted frame by
almost two-thirds. Generate the crop, `Read` it, and check the subjects have margin — the
first attempt put two kids' faces 35 px from opposite edges and had to be widened to 660 px.
Native 9:16 sources (720×1280) need none of this and fill the frame perfectly — spread those
through the cut deliberately to break up the padded ones.

**Do NOT crop crowd shots this way.** A tighter crop means fewer people in frame, which
directly defeats a "show more crowd" request. Crowd frames stay full-width and keep their
blur bands — it is the correct trade.

### Stills from before the event started read as "bored" (2026-08-05)

At a show/ceremony, the photos in the folder are very often taken **while people wait**:
house lights up, empty stage, kids on the floor with snacks, flat expressions. Cut into
the recap with Ken Burns they look listless — the user's words were
"קצת משועממות כי כנראה לפני שההצגה התחילה".

**Sort the stills into before / during before building SHOT_LIST.** Tells for "before":
room lights fully on, performers absent or setting up, people standing/milling, food out.
Tells for "during": stage lit or backdrop in frame, performer mid-gesture, audience facing
one direction.

- If most stills are pre-show, **build the cut from video instead** — motion reads as alive
  even when the same scene photographed is static. A 10-of-11-video shot list is fine.
- **Harvest collage tiles from the clips**: `ffmpeg -ss T -i clip.mp4 -frames:v 1 -q:v 2 f.jpg`,
  then hand-crop a landscape band around the action (`crop=W:460:0:Y`) for the 2×2 grid.
  A 576×460 frame fills a 522×458 tile with no upscaling.
- Keep the one or two stills that show a **genuine laugh** — and separate them with other
  shots so consecutive stills don't stack into a "slideshow" stretch.
- Look specifically for **a child participating** (on stage with the performer, answering,
  dancing). One such moment carries the whole "the kids loved it" message.

### Never stack intimate shots — a community event must LOOK crowded (2026-08-11)

The first cut of the plasticine workshop put six consecutive 1–2 person shots in the middle
(mother+daughter, two boys, two kids, one boy, one girl, boy+girl). Every individual shot was
good, but the stretch made a 60-person community happening read as a set of portraits. The
user's note was simply `שיהיה יותר קהל בתמונות`.

- **Never place more than TWO intimate shots in a row.** Interleave a wide/crowd frame between
  them. The fixed cut alternated crowd → intimate → crowd → intimate through the whole middle.
- **Target: at least half the shots show many people.** The approved v2 ran 8 crowd frames out
  of 15 photo shots.
- **Count people, don't trust the "wide shot" label.** Reject wides where a large share of the
  frame is empty chairs, foreground backs-of-heads, or a distant crowd — two of the widest
  photos in the folder were rejected for exactly this and would have sold the opposite message.
  Prefer the frame where faces fill the mid-ground, even if it is less wide.
- Emotional close-ups still carry the story — keep the best of them, just never consecutively.
- Adding crowd shots grows the runtime. Ask whether to extend (~30s → ~33s) or trade away
  intimate shots; on 2026-08-11 the user chose to extend and keep everything.
- **Pair a faster cut with the faster track**: shot durations tightened 2.2–2.6s → 2.1–2.4s and
  transitions 0.3–0.35s → 0.28–0.3s so the cuts sit on the new 143 BPM beat.

### Clip curation — scan EVERY video frame-by-frame before choosing (2026-07-14)

The user rejected two clips as "לא משמעותיים בכלל": static crowd-from-behind pans
(backs of heads, strollers, empty walls). Before writing SHOT_LIST, extract frames
from every clip at 2s intervals (`ffmpeg -ss T -frames:v 1`) and `Read` them. Rules:
- **Reject**: static crowd-from-behind, backs of heads, accidental pocket recordings
  (check for floor/ceiling frames), empty-room stretches
- **Prefer**: stage interaction, kids PARTICIPATING (standing with the performer,
  answering, dancing), the performer mid-gesture facing the audience
- A clip's most interesting segment is often at its START (performer active) — don't
  default to a mid-clip offset without looking

### Zoom toward a specific person's face — `zoom_to` motion (2026-07-19)

When the user asks to zoom toward a named person ("זום לפנים של X"), the template
now supports `"motion": "zoom_to"` with `"fx"`/`"fy"` (face center as fractions of
the frame), zooming 1.0→1.30 toward that point with clamped x/y.

- **FIRST verify who the person is.** Extract a small crop around the face you
  think is theirs and `Read` it — or ask. On 2026-07-19 the zoom was applied to
  the wrong woman (the lecturer instead of the named participant with the blue
  head covering); the user had to correct with a photo reference. If the name
  isn't obviously resolvable to a face, ask before rendering.
- **Never `zoom_to` on a blur-padded photo** (3:4 source in a 9:16 frame): the
  zoom window climbs into the blur bands (verified — top band visible at every
  zoom level when the face is near the top). Instead cut a dedicated 9:16 crop
  around the person (`crop=540:960:X:Y`, ≥500px wide), use it via the `file` key,
  and compute fx/fy inside THAT crop.
- If the face is near the crop's edge, the clamp keeps the window in-frame — the
  motion still reads as "zooming toward them" even if they end up off-center.

### Happy-faces vertical crops — multiply shots from limited photo stock (2026-07-14)

When the user wants "more happy kids" but every good photo is already used, cut tight
9:16 crops from dense crowd photos — each crop reads as a NEW photo:
- `ffmpeg -i photo.jpg -vf "crop=540:960:X:Y" -q:v 2 photo_kids_a.jpg` (choose X/Y to
  frame 3–6 laughing faces; generate 3–4 candidates and `Read` them, keep the best)
- Add to SHOT_LIST with the `file` key: `{"type": "photo", "name": "photo_kids_a", "file": "photo_kids_a.jpg", ...}`
- Vary motion between consecutive crops (`zoom_in` then `pan_up`) so they don't feel
  like the same image
- A 540×960 crop upscaled to 1080×1920 is acceptably sharp; don't crop tighter than ~500px wide

### Three small traps from the wood-workshop recap (2026-09-22)

- **`subprocess.run(..., text=True)` decodes stderr as cp1255 on this machine.** When the
  output filename is Hebrew, ffmpeg's stderr contains bytes cp1255 cannot map, the reader
  thread dies with `UnicodeDecodeError` and `proc.stderr` comes back `None`. Always pass
  `encoding="utf-8", errors="replace"` when parsing ffmpeg/ffprobe output (ebur128, volumedetect).
- **`astats` measures per audio frame (~23 ms), not per `length`.** For the 0.25 s smoothness
  scan use `aresample=48000,asetnsamples=12000,astats=metadata=1:reset=1,ametadata=print:...`.
  Without `asetnsamples` every percussive hit shows as a 10-25 dB "step" and the scan is noise.
- **A 522×458 collage tile from a portrait photo crops to the vertical centre** and beheads a
  face sitting in the top 30 %. Cut a hand tile at the tile ratio (1.14 : 1, e.g.
  `crop=721:633:0:250`) and pass it as the bucket file.
- Also: `yt-dlp ... | tail -1 || fallback` never runs the fallback — `||` tests `tail`. Run the
  403 retry (`player_client=android,web`) as its own loop. Kept music tracks (`.m4a`) now go to
  `סקריפטים/` by `organize_folder.py`.

### Two ffmpeg traps that produce silently-broken output (2026-08-25)

**`-shortest` does NOT bound the watermark overlay when the master has no audio.**
`add_watermark.py` on a *silent* master (the correct order when muxing several audio
versions) produced a **99-minute, 74MB** file instead of 28 seconds: with only one
output stream, `-shortest` has nothing to compare against and `overlay` keeps pulling
frames from the `-loop 1` logo forever. It worked in earlier rounds only because audio
had already been muxed, giving `-map 0:a?` a second stream. The template now probes the
master and passes `-t <master_dur>` explicitly. If it already happened, the leading
seconds are fine — `ffmpeg -i broken.mp4 -t <DUR> -c copy out.mp4` recovers it with no
re-render.

**17+ concurrent 1080×1920 H.264 decoders exhaust RAM.** The cascading `xfade` concat
over 17 intermediates returned `get_buffer() failed / no frame!` and the encoder never
opened (8.4GB free of 31GB). Add `-threads 1` before **every** `-i` in `build_final`
(already in the template) — decode is not the bottleneck there anyway.

### "New files" from the user are often re-encoded duplicates — compare pixels (2026-08-25)

When the user drops a folder and says "use everything in here", **verify it is actually
new before building.** Re-sharing an album (Telegram, WhatsApp) re-encodes it: every
byte changes, so `md5sum` reports 100% new while the pictures are identical.

On 2026-08-25 a "חדשות" folder held 14 files. All 14 had fresh md5s. A perceptual
comparison found **9 photos and all 3 videos at diff=0.0** against material already in
the cut — only 2 photos were real. Padding the video with them would have repeated
frames already on screen.

```python
from PIL import Image
def sig(p):  # MAD < 6 = same image, < 15 = near-duplicate
    return list(Image.open(p).convert('L').resize((16,16)).getdata())
```
For clips, pre-filter by duration (Δ > 0.6s ⇒ different clip), then compare three
frames (start / middle / end). **Report the duplicate count to the user and let them
decide** — how much of it to include is their call, not a detail to absorb quietly.

### Audio choices

- "ללא אודיו" / "no audio" → pass `-an` everywhere
- User provides a YouTube URL → `yt-dlp -x --audio-format m4a -o "_source_audio.%(ext)s" <url>`
- No URL given → audition by title first: `yt-dlp --print "%(title)s | %(duration)s sec" "ytsearch3:<query>"`,
  then download the best match. For kids/family events: upbeat children's instrumental
  (user preference 2026-07-14). "Hava Nagila (Royalty Free Background Music)" is the
  fallback festive option. **Titles are a shortlist only — if rhythm matters, measure
  (see "More upbeat/rhythmic" below).**
- Known-good pick for kids/family events: *"Percussion Fun Energetic Upbeat Background Music
  Royalty Free"* (`zDeCCWxn8V4`, 76s) — 143.6 BPM, 4.63 onsets/sec, 49/51 harmonic-percussive,
  full energy from t=4s. Approved 2026-08-11 after the 123 BPM default was rejected as too slow.
- **Known-good pick, approved 2026-09-23 for a fast (1.4s/still) kids-workshop cut:**
  *"Happy Kids Fun Music (Royalty Free Music) Upbeat and Happy Background Music For Videos"*
  (`8si4MOBzUyA`, 116s) — E major r=0.62, 144 BPM, punch 2.93, 79% harmonic. There is a 0.8s
  silent break at 5.6s and the beat drops at **6.4s**, so enter there with a 0.3s fade-in. It beat "Happy Upbeat
  Instrumental" (`TsTz8T4ZBEA`, 185 BPM) and "Prinitza" (`GVenZmfSuPM`, Jewish-Israeli party)
  in a 3-version pick. The same user had rejected a Hasidic "ושמחת בחגך" playback as
  `המוזיקה לא טובה`. For a holiday-themed kids event, a punchy major-key kids track beats a
  soft holiday tune. Measured Jewish/klezmer candidates were all soft (punch ≤ 1.9).
- **Emotional / spiritual adult events ("נעימה מרגשת", women's prayer, hillula), 2026-10-20:**
  *"Cinematic Piano Strings 05 | Emotional Film Score Music | No Copyright"* (`iM4AqF8R9ME`, 160s):
  C major r=0.80, 81 BPM, 95% harmonic, -14.2 LUFS raw (needs no gain). It opens with a sting
  followed by a **dead gap at 2.5-3.0s (-56 dB)**. Enter at **3.25s** with a 1.5s fade-in. The rhythm
  thresholds above apply to kids only. For this mood, choose on major mode, a steady level, and
  a melody led by piano and strings. Avoid Hebrew "instrumental covers" of known singers (copyright). A pass
  that was only 2s granular missed the gap; the 0.25s RMS scan on the delivered file caught it.
- The audio is almost always longer than the video — trim to video length and apply `afade` in/out
- **Keep a copy of the chosen track in `סקריפטים/`** (e.g. `מוזיקת רקע - ילדים קצבית.m4a`)
  so later swaps/edits don't re-download
- **Swapping music on a finished deliverable needs NO re-render**: `ffmpeg -i master.mp4
  -i new.m4a -map 0:v -map 1:a -c:v copy -c:a aac -af "afade=..." -t DUR ...` — video
  stream copies through losslessly (used twice on 2026-07-14, works even after watermark)

### Never mux a track from t=0 without measuring its intro (2026-08-04)

Royalty-free tracks very often open with a soft build-up — and some end that
intro in near-silence right before the beat drops. Muxed from t=0 that lands a
dead-quiet stretch over the first third of a 40s recap. On 2026-08-04 the chosen
kids track sat at -26 dB, sagged to **-54 dB at 8s**, and only hit its real level
(-20 dB) at **9s**; the user immediately noticed "the music only starts at second 9".

**Always profile the track before muxing** — one second at a time, and read the numbers:
```bash
for s in $(seq 0 2 55); do
  v=$(ffmpeg -hide_banner -ss $s -t 1 -i track.m4a -af volumedetect -f null - 2>&1       | grep mean_volume | sed 's/.*mean_volume: //')
  echo "t=${s}s  $v"
done
```
(`-v error` suppresses volumedetect's output — use `-hide_banner` instead.)

- Pick the first second where the level reaches the track's steady loudness and
  **offset the audio input to it**: `-ss <drop> -i track.m4a` (before `-i`, so it seeks).
- Then verify the whole `<drop> → <drop+duration>` window has no further dips — a
  mid-track breakdown is just as damaging as a slow intro.
- With the music entering at full energy, **shorten the fade-in to ~1.2s**; the 2.5s
  ramp exists to ease into a gentle intro, and over a beat drop it just mutes the hook.
- Confirm on the muxed file with the same per-second scan, not by ear-guessing.

### "More upbeat/rhythmic" — MEASURE it, never pick by title (2026-08-11)

When the user rejects a track as not rhythmic enough (`יותר קצבית`), do NOT just download
another track whose title says "energetic". Titles lie. `librosa` is installed on this
machine — **measure the current track first to get a baseline, then measure every candidate
against it.** On 2026-08-11 the delivered track measured 123.0 BPM / 3.73 onsets-per-sec /
onset-strength std 2.63; those three numbers became the bar every candidate had to clear.

```python
import librosa, numpy as np
y, sr = librosa.load(f, sr=22050)
tempo, _ = librosa.beat.beat_track(y=y, sr=sr, start_bpm=140)
onsets   = librosa.onset.onset_detect(y=y, sr=sr, units='time')   # pulse density
strength = librosa.onset.onset_strength(y=y, sr=sr)               # .std() = punch
```

- **`onset_strength().std()` is the single best proxy for "feels rhythmic"** — it measures
  transient contrast (how hard the hits land). It moved 2.63 → 4.39 and that is what the
  user actually hears. BPM alone is a poor predictor.
- **`beat_track` makes octave errors — always re-run with 2–3 `start_bpm` seeds (60/120/180).**
  The winning track reported 95.7 BPM at seed 120 but locked to 143.6 at seed 180. Judging on
  the single default reading would have wrongly rejected the best candidate.
- **Check the harmonic/percussive split so you don't ship a drum loop**:
  `H, P = librosa.effects.hpss(y)` → the pick was 49% harmonic / 51% percussive (melody
  intact, much more drive than the old 63/37). A candidate at 37% harmonic was rejected as
  drums-only, and one at 82% harmonic was rejected as too gentle despite a 184 BPM reading.
- Search 3+ different query angles (`percussion`, `energetic`, `clapping/ukulele`) and pull
  6–8 candidates — measuring is cheap, and the first page of results is mostly the same tracks.

### "Happy" is a MAJOR KEY — and it is measurable (2026-08-11, round 3)

Optimising the rhythm metrics above **alone** produced a *percussion* track: 143.6 BPM and
huge punch, but the user came back a third time with `צריך מוזיקה קצבית שמחה לילדים`.
Measuring the mode explained it instantly — **both previously delivered tracks were in E minor.**
Neither could ever read as joyful no matter how fast it was, and the rejected one had a tonal
correlation of just **r=0.21** (almost no tonal centre — the ear hears drumming, not a tune).

Add key/mode detection (Krumhansl-Schmuckler) to the measurement script and treat it as a
**hard criterion for kids/family events**:

```python
MAJ = np.array([6.35,2.23,3.48,2.33,4.38,4.09,2.52,5.19,2.39,3.66,2.29,2.88])
MIN = np.array([6.33,2.68,3.52,5.38,2.60,3.53,2.54,4.75,3.98,2.69,3.34,3.17])
chroma = librosa.feature.chroma_cqt(y=y, sr=sr).mean(axis=1)
# roll chroma over all 12 tonics, correlate against both profiles, highest wins
```

**Full pass criteria for a kids-event track** (all must clear, not a weighted average):

| metric | threshold | why |
|---|---|---|
| **mode** | **major, r ≥ 0.45** | this *is* "happy" — the criterion that was missing for two rounds |
| **harmonic %** | **60-85%** | floor: melody-led, not a drum bed. **ceiling added 2026-08-25** |
| BPM | ≥ 130 | keeps the rhythm |
| onsets/sec | ≥ 4.0 | pulse density — **but see the bias note below** |
| punch (onset sd) | ≥ 3.0 | transient contrast |

- **`r < 0.3` means no tonal centre** — the track will not read as music to a listener,
  however good its rhythm numbers are. Treat it as an automatic reject.
- **The onset-density threshold is biased toward percussive material.** It was calibrated on
  a percussion track (4.71); melodic tracks carry rhythm through tempo + punch, and sustained
  notes simply do not register as onsets. The winning ukulele track missed the 4.0 bar by 0.07
  and was still the right pick — it beat the outgoing track on *every* metric and had the
  strongest tonality in the pool (F major r=0.87). Check a near-miss against the outgoing
  track before rejecting it on this metric alone.
- **Measure every candidate on the identical window** (e.g. 45s from t=0). The same track
  measured punch 2.63 on one window and 3.07 on another — inconsistent windows silently
  disqualify good candidates.
- **Sweep gain per track, never once for all.** The three finalists sat at -18.8, -13.8 and
  -12.8 dB mean; a single shared gain would have left one obviously weaker than the others.
- Good search angles for major-key kids music: `xylophone glockenspiel`, `marimba playful`,
  `ukulele claps whistle`. Known-good pick (2026-08-11): *"Upbeat Ukulele Background Music |
  Happy Clapping Ukulele Whistle"* (`IJ2pQ3iDsnU`, 139s) — F major r=0.87, 152 BPM, 78%
  harmonic; **enter at t=20s**, its intro sags to -27 dB at t=8.
  **Gone from YouTube as of 2026-08-25** ("video unavailable") — measure a fresh pool.

### The harmonic CEILING — 95% harmonic is why "happy" reads as "not rhythmic" (2026-08-25)

A track can pass every rhythm metric and still be rejected as `לא מספיק קצבית`. The
delivered pick measured 185 BPM and punch 3.45 — but **95% harmonic**, i.e. mallets with
no drum kit. There was no beat for the ear to lock onto. **Cap harmonic at 85%.**

Measuring 22 candidates over three search rounds exposed a systematic trade-off:

| punch | harmonic % |
|---|---|
| 4.25 | 5% |
| 4.15 | 34% |
| **3.45 (rejected pick)** | **95%** |
| 2.61 | 86% |

Nearly every track is either a drum loop or a melody — the 60-85% band is thin, and
generic "upbeat/energetic/happy" queries do not reach it. What worked was searching the
**percussion vocabulary** directly: `stomp`, `claps`, `dynamic claps`. Known-good pick
(2026-08-25): *"[No Copyright Music] Dynamic Claps - Stomp"* (`TgZ9atmoxl8`, 46s) —
C# major r=0.74, 144 BPM, punch 4.50, onsets 6.01/s, **67% harmonic**, loud from t=0
(needs **0 dB gain**, just `alimiter=limit=0.95` → -9.3 LUFS).

- **Compare processed-to-processed, never raw-to-raw.** Limiting costs punch, and a quiet
  track needing +18 dB loses far more than a loud one needing 0 dB. One candidate led on
  raw punch and fell to *last* after gain-matching.
- **A track with a soft intro is not disqualified — rescore it on the window you'd use.**
  Scanning every 28s window (step 2s) and keeping the highest-punch one changed the
  ranking; the winner scored 2.61 measured from t=0 and 4.50 on its real window.

### Silent bars: a track that fit at 28s can break at 33s (2026-08-25)

Stomp/clap tracks often drop one bar to near-silence before the beat returns. The chosen
track dips to **-20.8 dB at t=27** — harmless at 28.3s (it landed inside the fade-out),
audible as a hole once the cut grew to 33.1s. **Re-profile the track whenever the runtime
changes**, not just when the track changes.

Fix by splicing the bar out on the **beat grid**, not by eye — at 144 BPM a bar is
`4/144*60 = 1.667s`, so cut `[26.667, 28.333]` and the downbeats stay aligned:
```bash
ffmpeg -i track.m4a -filter_complex \
  "[0:a]atrim=0:26.667,asetpts=N/SR/TB[a];[0:a]atrim=28.333,asetpts=N/SR/TB[b];[a][b]concat=n=2:v=0:a=1[out]" \
  -map "[out]" -c:a aac -b:a 256k track_edit.m4a
```
Re-measure after splicing (punch/onsets improved to 4.50 / 6.19 here) and keep the edited
copy next to the original in `סקריפטים/`, named so the edit is obvious.

**Hasidic/holiday playbacks "breathe" every phrase (2026-09-23).** "ושמחת בחגך 2 - חסידי -
פלייבק" drops ~9 dB for ~4s every ~27s (11-15, 39-42, 69-72, 94-99s), so NO 40s window is
clean. Scan 0.5s RMS for the window with the highest minimum; if it still holds a bridge,
enter on the downbeat right after one bridge (42.55s) and splice the next one out on a
whole number of beats taken from `beat_track` (12 beats = 68.30→73.32), joined with
`acrossfade=d=0.03`. Check the inter-beat intervals across the splice afterwards.

### After two misses on a subjective axis, ship 3 versions to choose from (2026-08-11)

Music taste is not fully reachable by measurement. Once the user has rejected two tracks,
stop guessing a third time: shortlist the top 3 that pass every criterion, give each a
**distinct character** (glockenspiel / piano-xylophone / ukulele-claps), and render all three.

This is nearly free — the video never changes, only the audio is swapped:
```bash
ffmpeg -y -i "<deliverable>.mp4" -ss <entry> -i cand.m4a -map 0:v -map 1:a \
  -c:v copy -c:a aac -b:a 192k -af "volume=<N>dB,alimiter=limit=0.92,afade=..." \
  -t <DUR> -shortest -movflags +faststart "גרסה A - <character>.mp4"
```
`-c:v copy` preserves the rendered stream **including the watermark and logo card**. Name the
files by their instrument character (`גרסה A - פעמונים ומרימבה`) so the user can choose
without opening each one blind. After the pick: promote to the canonical name, re-export the
WhatsApp copy, delete the rest.

### Loudness-match the new track or "more energetic" lands quieter (2026-08-11)

A punchier track is usually a **more dynamic** one, which means a *lower* integrated
loudness at the same peak ceiling. Swap it in naively and the user hears a weaker video.
Measured on 2026-08-11: old deliverable **-8.9 LUFS**, new track window **-12.4 LUFS** —
a 3.5 LU drop that would have read as "you made it quieter", not "more rhythmic".

**Always compare LUFS between the OLD DELIVERABLE and the new candidate**, both including
fades, so it is apples to apples:
```bash
ffmpeg -hide_banner -i <file> -af ebur128=framelog=quiet -f null - 2>&1 | grep -A2 Integrated
```

- **`loudnorm` alone often fails to reach the target.** Its pass-1 JSON showed
  `target_offset: 3.50` — it wanted +3.5 dB but the true-peak ceiling blocked it, because the
  source already peaked at **0.0 dBFS** (`max_volume` via `volumedetect`). Single-pass
  loudnorm delivered only -12.8 LUFS against an I=-9.5 request.
- **Plain `volume=` gain clips** on such a track for the same reason.
- **What worked: `volume=NdB,alimiter=limit=0.92`, swept and measured.** Test 3 gain values
  and print LUFS *and* punch for each, then pick the knee:

  | filter | LUFS | punch |
  |---|---|---|
  | `volume=3dB` | -10.5 | 4.46 |
  | `volume=4.5dB` | -10.0 | 4.25 |
  | **`volume=6dB`** | **-9.4** | **4.04** |

  6 dB restored the old loudness while keeping punch 54% above the original baseline.
- **Verify punch on the DELIVERED file, not the source** — extract the muxed audio
  (`-vn -ar 22050 out.wav`) and re-measure. Limiting costs some transient contrast
  (4.58 → 4.39 here); confirm it is still far above the track you replaced.
- Landing within ~1 LU of the previous deliverable is imperceptible. Do not chase exact parity
  at the cost of flattening the dynamics you selected the track for.

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

- Render at the END of SHOT_LIST as `type: "logo"`, `name: "logo.png"`, `dur: 2.2`, `trans: "fadeblack"`, `td: 1.5`
- Background: pure BLACK (`color=c=black`) — blends seamlessly into the final fade-to-black (user directive 2026-07-07; was white)
- Logo size: **`min(62% of frame width, 40% of frame height)`**, centered — proportional in BOTH orientations. Never scale by width alone: a round logo at 70% width overflows a 16:9 frame top/bottom (user caught this 2026-07-14)
- Preceding shot uses `fadeblack` transition so it dips to black into the logo card
- If logo filename has non-ASCII (Hebrew) characters → copy to `logo.png` first
- Note: a transparent-background PNG logo works best on black — a light/white mark pops; a dark logo would vanish (invert or add a plate if so)

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

- ❌ Adding on-screen text ANYWHERE EXCEPT the collage title — no captions, lower-thirds, dates, or names over the 4 acts. The single poster title baked onto the opening collage (see "Opening Title") is the only allowed text.
- ❌ Rendering Hebrew title text with raw ffmpeg `drawtext` or PIL without `python-bidi` — it comes out reversed/mis-ordered. Always use `add_collage_title.py` (bidi-aware).
- ❌ **Fading in from black at the start.** The user explicitly rejected this on 2026-05-18 — they want the collage visible from frame 0. The template now defaults to no intro fade.
- ❌ **Opening on a single photo or video clip instead of the collage.** The collage is mandatory — it's how every video starts.
- ❌ Using hard cuts, plain crossfades, or xfade wipes (`smoothleft`, `circleopen`…) between shots. **Every junction gets an animated effect from `transitions.py`, every time, unasked** (user directive 2026-09-06). The only plain transition allowed is the closing `fadeblack` into the logo card.
- ❌ Repeating the same effect twice in one cut, or asking the user whether they want effects — they always do.
- ❌ **Burying the clips' own sound under music when the user wants to hear the clips.** Put the clip audio on the timeline first (J/L-cuts), gain-match it, and duck the music hard.
- ❌ `loudnorm` in the same filter chain as `adelay` — it silently shifts the segment to t=0.
- ❌ Ducking the music with `sidechaincompress` under singing/prayer — it pumps on every breath. Use the planned envelope in `mix_music.py`.
- ❌ Adding emoji or decorative overlays.
- ❌ Aggressive Ken Burns (zoom past 1.20).
- ❌ Mixing photos+video in single ffmpeg filter_complex without intermediate render — leads to encoding inconsistencies and frame jitter at transitions. Always render intermediates first, then xfade them.
- ❌ Asking the user "which photos do you want?" — they trust you to curate. Use the 4-act structure + collage rules to choose.
- ❌ Asking "is this OK?" mid-build — finish, deliver, iterate on feedback.
- ❌ **Picking video segments blind** (by offset math alone). Static crowd-from-behind footage got rejected as "not meaningful" (2026-07-14). Always extract + `Read` frames from every clip first.
- ❌ **Scaling the logo card by width only** — round/tall logos clip outside the frame. Cap by height too (see "Logo card").
- ❌ **Picking a "more upbeat" track by its title.** Measure BPM + onset density + onset-strength std with `librosa` against the outgoing track (see "More upbeat/rhythmic").
- ❌ **Shipping a MINOR-key track to a kids event.** "שמח" means major — check the mode, and reject anything with a tonal correlation below ~0.3 (see "Happy is a MAJOR KEY").
- ❌ **Optimising rhythm metrics alone** — that path lands on a percussion bed with no melody. Pair BPM/onsets with `harmonic ≥ 60%` and major mode.
- ❌ **Guessing a third track after two rejections** — render 3 candidates with `-c:v copy` and let the user pick.
- ❌ **Swapping in a new track without comparing LUFS to the old deliverable** — a punchier track is usually quieter, and the user hears "weaker", not "more energetic".
- ❌ **Six intimate shots in a row at a community event.** Never more than two consecutive 1–2 person frames; interleave crowd.
- ❌ **Cropping crowd shots to reduce blur bands** — fewer people in frame is the opposite of what was asked.

## Default Output Filenames

- Working/intermediate name: `<event_short_name>_<format>.mp4` (e.g. `kamtza_recap_vertical.mp4`)
- **Final deliverable gets a descriptive Hebrew name** per the global filename iron rule:
  `01 - <תיאור האירוע> - <שם הקהילה>.mp4` (e.g. `01 - טקס סיום השנה - שם הקהילה.mp4`)
- WhatsApp-light copy: same name + ` (ווטסאפ)` suffix
- Keep `build_video.py` in the project folder (moved to `סקריפטים/` by organize) for re-runs.

## Verification Steps Before Delivery

```bash
ffprobe -v error -show_entries format=duration,size \
  -show_entries stream=codec_type,codec_name,width,height \
  -of default=noprint_wrappers=1 <final.mp4>
```

Confirm: correct W×H, ~target duration, both video+audio streams present (or video-only if no-audio requested), file under ~150MB for 1080p ≤2:30.

Extract 2–3 frames at the start, middle, and end with `ffmpeg -ss T -frames:v 1`, then `Read` them to spot-check visually.
