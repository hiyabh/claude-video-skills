---
name: blessing-video-weaver
description: "Produce a full greeting/blessing compilation video (birthday, anniversary, farewell, bar/bat mitzvah) from a folder of raw self-recorded clips — one clip per person. Transcribes everything (Hebrew Whisper), writes a thematic weaving script (37+ segments across chapters, not clip-after-clip), normalizes/speeds/levels every source, renders kinetic Hebrew motion graphics in HyperFrames (intro, chapter cards, lower-thirds, outro, text-BEHIND-subject), assembles with varied ffmpeg xfade transitions + Ken Burns, and mixes ducked background music. TRIGGER on Hebrew: 'סרטון ברכות', 'סרטון יומולדת מסרטונים', 'סרטון יומולדת 40/50/60', 'כל האחים הקליטו', 'לשזור את הברכות', 'סרטון מכל המשפחה', 'סרטון פרידה מהעבודה', 'תעשה סרטון אחד מכל הסרטונים'. English: 'blessing compilation video', 'birthday greetings video from clips', 'weave these greeting clips', 'family tribute video'. USE THIS when input is SPEECH-driven greeting clips (one person per clip talking to camera) that must ALL appear, woven smartly. NOT for photo+clip event montages (event-recap-video, ~50s no-text), NOT for motion-graphics-only videos (epic-video-studio / hyperframes)."
---

# Blessing Video Weaver — שזירת סרטוני ברכה לסרטון אחד

Speech-first editing: the transcript drives the edit. Every clip's real content goes in
(user's typical demand: "כל מה שהוסרט יהיה בסרטון"), but interleaved by THEME, not
clip-after-clip. Proven end-to-end on a 9-clip / 10.7-min-raw → 10:19 final (2026-06-12).

## Pre-flight questions (AskUserQuestion, once)

1. **מוזיקה** — חגיגית רק בפתיח/מעברים | שקטה לכל האורך | שתיהן (ducking) | בלי
2. **אוויר מת** — מותר לחתוך שתיקות/גמגומים/סידור מצלמה? (תוכן אמיתי תמיד נשמר)

Defaults you don't ask about: portrait 9:16 if sources are portrait; canvas = highest
native resolution among sources (e.g. 576×1024@30); descriptive Hebrew output filename
+ a WhatsApp-friendly crf-25 copy.

## Pipeline (10 stages — templates/ has the proven scripts)

The templates are the WORKED EXAMPLE from the 2026-06-12 production (9 siblings,
Hebrew). Per project adapt: the `SEGS` table in cut_segments.py, the `CLIPS` map in
normalize_all.py, the chapter/lower/behind variable lists in gfx/render_gfx.py, and the
part lists in build_final.py. The ffmpeg flag choices, filter orders, and encoder
settings are the hardened parts — keep them.

| # | Stage | Tool / template | Output |
|---|---|---|---|
| 1 | Inventory | ffprobe every clip (W×H, dur, fps, **rotation side_data**) | plan table |
| 2 | Transcribe | [templates/transcribe_all.py](templates/transcribe_all.py) — faster-whisper | `work/transcripts/*.json` |
| 3 | Weaving script | manual authoring from transcripts | `work/script.md` |
| 4 | Normalize | [templates/normalize_all.py](templates/normalize_all.py) (+`face-track-reframe` skill for square/landscape clips) | `work/norm/*_n.mp4` |
| 5 | Cut segments | [templates/cut_segments.py](templates/cut_segments.py) — **two-stage, read its header** | `work/segments/` |
| 6 | Graphics | [templates/gfx/](templates/gfx/) HyperFrames project — intro, chapter cards, outro, lower-thirds, behind-text | `gfx/renders/` |
| 7 | Overlays | [templates/overlay_segments.py](templates/overlay_segments.py) + [templates/behind_composite.py](templates/behind_composite.py) | `work/titled/` |
| 8 | Assemble | [templates/build_final.py](templates/build_final.py) — two-level xfade cascade | `work/final_nomusic.mp4` |
| 9 | Music | [templates/mux_music.py](templates/mux_music.py) — sidechain ducking | final mp4 |
| 10 | QA + deliver | frames, volumedetect, re-transcribe check, WhatsApp copy | two mp4s |

## The weaving script (stage 3) — the heart of the skill

- Read ALL transcripts first. Identify: themes, the strongest/funniest moments, natural
  sentence boundaries, dead air, recurring motifs (e.g. a name pun like "בן ארבעים למאיה").
- Structure: **cold open** (2-3 punchy seconds-long openers) → kinetic title → **thematic
  chapters** (3-7, titled, each interleaving 3-5 speakers) → **finale** (everyone's closing
  blessings in rising emotional order, end on the punchiest "מזל טוב") → outro card.
- **Bloopers clip** (someone who couldn't get a clean take): split into 2-3 interludes
  spread through the video, affectionate framing (badges "טייק 1/טייק 2/מאחורי הקלעים"),
  never mocking. Place take-2 where its CONTENT fits a chapter theme.
- A bridge joke beats a hard cut: e.g. a sibling saying "לקח לי זמן לפתוח את המצלמה"
  right before the bloopers block.
- **Coverage checklist is mandatory**: every source second is either in a segment or
  explicitly classified dead-air. Write it at the bottom of script.md.
- Same speaker twice in a row → either merge into one cut (keep small pauses) or mark
  the second segment `punch` (static 1.08 punch-in masks the jump cut).
- Don't put the same speaker on both sides of a chapter card.

## Hard-won lessons (cost real debugging time — do NOT relearn)

### ffmpeg

- **`zoompan` default fps is 25.** On 30fps input it silently slows video 1.2x and
  desyncs A/V (metadata still LOOKS right — nb_frames can't show duplicated frames).
  ALWAYS `zoompan=...:fps=30`. This shipped broken once before being caught.
- **Speed change + zoompan never in one -vf chain.** zoompan regenerates CFR timestamps
  and silently undoes a preceding `setpts`. Two-stage: (A) trim+setpts/atempo+loudnorm →
  clean CFR intermediate; (B) punch+zoompan. cut_segments.py implements this.
- **`-t` must be an INPUT option (before `-i`) when speed filters are used.** As an
  output option it keeps reading source until the OUTPUT reaches t — sped content from
  beyond the intended cut bleeds in.
- **`crop` w/h expressions do not accept `t`** (only x/y do) — you cannot animate zoom
  with crop; that's why zoompan despite its quirks.
- Speaker talks slowly → `setpts=PTS/1.15` + `atempo=1.15` (pitch preserved). 1.15 is
  noticeable-but-natural.
- Per-SEGMENT `loudnorm=I=-15:TP=-1.5:LRA=11` (not per-clip) — weak voices get boosted
  where they're weak; levels match across speakers.
- xfade needs `format=yuv420p,settb=AVTB,fps=30` on every input; audio `acrossfade`
  with the SAME duration; offset formula `offset += dur[i-1] - td`. Silent graphics
  pieces get `anullsrc` lanes.
- **Two-level cascade** (chapters → film): each piece re-encoded max twice, one failure
  doesn't kill a 47-input monster graph, parts are reusable on revision rounds.
- Varied transitions that look good portrait: slideleft/right/up, smoothup/left/right,
  circleopen (into chapter cards), hlslice, radial, zoomin, dissolve, pixelize (playful,
  for bloopers), fadeblack only into the outro.
- Ducked music: music `loudnorm=I=-20` (speech is at -15), then
  `[mus][speech]sidechaincompress=threshold=0.02:ratio=10:attack=120:release=700`,
  `amix=normalize=0`, `alimiter=limit=0.97`. Music audibly swells in cards/transitions
  on its own. Verify: volumedetect on a card window vs a speech window.
- Windows + Hebrew paths: `os.chdir(BASE)` then RELATIVE filenames to ffmpeg/ffprobe.

### Whisper (Hebrew)

- `small` mangles Hebrew ("בלב עור גדול" for "מזל טוב גדול") — use **`large-v3-turbo`**
  (faster-whisper, int8 CPU, ~0.4x realtime). `pip install faster-whisper`.
- Set `HF_HUB_DISABLE_SYMLINKS=1` on Windows or model download crashes (WinError 1314).
- A clip returning **0 segments** = VAD ate quiet audio → retry `vad_filter=False`.
- Verify "empty" regions with `volumedetect` before discarding — a -0.3dB max in a
  blooper tail is laughter, i.e. content.

### HyperFrames graphics (Hebrew)

- Hebrew fonts are NOT auto-resolved: download Heebo + Secular One woff2 (hebrew+latin
  subsets) into `fonts/`, add @font-face with unicode-range. Lint warns if missed.
- Cards = standalone compositions (no `<template>`) rendered via
  `render -c compositions/chapter.html --variables-file vars/x.json` — variables file in
  UTF-8 is the only safe way to pass Hebrew on Windows (inline `--variables` mangles).
- Lower-thirds and behind-text render as **transparent VP9 webm** (`--format webm`,
  body background transparent) → composited by ffmpeg `overlay` with `-c:v libvpx-vp9`
  BEFORE that input (required to decode alpha), `eof_action=pass`.
- Text emoji like ❤ render BLACK unless you set CSS `color` explicitly.
- `direction: rtl` on every text container; RIGHT-anchored lower-third pill slides in
  from x:+360 (RTL-natural).

### Text-behind-subject ("שקופיות שצפות מאחורי האנשים")

- `npx hyperframes remove-background seg.mp4 -o cut.webm --quality best` (best, not
  balanced — the cutout layers over its OWN source, color must match). ~0.3-0.6s/frame
  on CPU → pick SHORT segments (3-10s): cold open, an emotional one-liner, the closer.
- Layer order in behind_composite.py: base mp4 → text webm → cutout webm.
- **Regenerate cutouts whenever the segment is re-rendered** — a cutout from a previous
  encode no longer aligns frame-for-frame.
- Word position: top 1-10% of frame. Check a frame — if the head occludes the word,
  raise it; partial occlusion IS the effect, unreadable is a bug.
- Render the text layer 10s long and let `eof_action=pass`/output length clip it — one
  render fits any segment duration.

### QA (all five, every delivery)

1. ffprobe final: streams, duration ≈ sum(parts) − sum(joins).
2. Extract frames at: cold open, each text-behind spot, 2-3 chapter cards, outro. Read them.
3. volumedetect: card window vs speech window (music must be lower under speech).
4. **Re-transcribe 15s of the final mix** — if Whisper still understands the speech over
   the music, a human will.
5. Coverage: every script.md row landed in a part (build log "built:" lines).

## Deliverables

- `<אירוע> - <תיאור>.mp4` (full quality, crf 17 parts → ~200MB for 10min portrait)
- `<אירוע> - <תיאור> (גרסה קלה לוואטסאפ).mp4` — crf 25 preset slow (~40% of full size)
- Keep in `work/`: transcripts, script.md, final_nomusic.mp4 (instant music remix:
  swap `music_raw.m4a`, rerun `mux_music.py`), all pipeline scripts.

## Related skills

- `face-track-reframe` — square/landscape clip → 9:16 with dynamic face tracking (stage 4)
- `hyperframes`, `hyperframes-cli`, `hyperframes-media` — graphics engine + remove-background
- `event-recap-video` — photo/clip montage (~50s, no text) — different animal
- `universal-downloader` — fetch royalty-free music (`yt-dlp -x --download-sections "*0:00-13:00"`)
