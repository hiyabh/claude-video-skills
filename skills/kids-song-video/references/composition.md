# Composition — HyperFrames (captions, Ken Burns, render)

> **Start from a known-good skeleton:** copy
> [`templates/composition-stills.html`](../templates/composition-stills.html) (image layers +
> Ken Burns + crossfades) or [`templates/composition-live.html`](../templates/composition-live.html)
> (single live-video background) into the project's `clip/index.html` and adapt the `GROUPS`
> array (caption text + timing), durations, and asset names. Both are real, rendered, working
> compositions with all pitfalls below already handled.

How to assemble the video in HyperFrames. A kids song video is NOT the dense
"corporate" house style — it is **full-bleed art + big friendly karaoke captions +
gentle ambient motion**. Ignore the 8-10-elements-per-scene density rule.

## Project setup

```bash
npx hyperframes init clip --example blank --resolution portrait \
    --skip-transcribe --skip-skills --non-interactive
# portrait = 1080x1920 (9:16). The blank example does NOT create index.html — you write it.
cp <song>.mp3 clip/assets/song.mp3
cp images/*.png clip/assets/images/
```

## PITFALLS (each one cost a debug cycle — do these)

1. **Include GSAP yourself.** The runtime does NOT auto-inject it. Without
   `<script src="gsap.min.js"></script>` in `<head>`, your inline `gsap.timeline()`
   throws and NOTHING animates (snapshots come out as the bare background — the tell).
   Download it locally for offline render reliability:
   `curl -L -o clip/gsap.min.js https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js`
2. **Initialize the registry:** `window.__timelines = window.__timelines || {};`
   before `window.__timelines["id"] = tl;` (lint error otherwise).
3. **No `repeat: -1`.** Infinite repeats break the deterministic frame-seek renderer.
   Use a finite count: `repeat: Math.floor(DUR / cycle) - 1` (for floating notes etc.).
4. **Embed Hebrew fonts locally** — system Hebrew fonts aren't present in headless
   Chrome. Download @fontsource woff2 into `clip/fonts/` and `@font-face` them:
   `https://cdn.jsdelivr.net/npm/@fontsource/rubik/files/rubik-hebrew-{500,700,900}-normal.woff2`
   and `@fontsource/suez-one/files/suez-one-hebrew-400-normal.woff2` (display title).
   Rubik supports niqqud; weight 900 = bold karaoke text.
5. **One root composition.** Don't leave a second file with `data-composition-id` in
   the project root (e.g. `index_still.html`) — the runtime discovers both → duplicate
   audio. Keep backups in a `_backup/` subfolder.
6. **Duplicate media warning:** if you show the same image twice, copy it to a second
   filename (`scene_07_b.png`).

## Captions — RTL Hebrew karaoke

- Text comes from your **known niqqud lyrics**; timing from whisper segments
  (see [`scripts/transcribe_song.py`](../scripts/transcribe_song.py)). Map each lyric
  line to a segment's start/end. Read `assets/segments.txt` to align (console mangles
  Hebrew; the file is correct).
- Build groups in JS: `var GROUPS = [[text, start, end], ...]`, one DOM `.cap` div
  per group, fade in (`back.out`) at `start`, fade out + **hard kill** at `end`:
  `tl.set("#cg-"+i, {opacity:0, visibility:"hidden"}, end);`
- Style: `direction: rtl; unicode-bidi: isolate; text-align: center;` font Rubik 900,
  ~78px, white with a dark stroke/shadow. Portrait position: a bottom band
  (`bottom: ~250px`) over a bottom **scrim** gradient for legibility. Never cover the
  child's face.

## Background: stills (v1) vs live video (v2)

**Stills version** — 9-10 image layers, each a wrapper `div.layer`(opacity:0) holding
an `<img>` with NO `data-*` (you own opacity/transform via GSAP). Crossfade
(`opacity 0→1` / `1→0`, ~0.7s overlap) + Ken Burns (`fromTo` scale 1.05↔1.18 + small
x/y) per layer. DOM order = paint order, so place layers chronologically.

**Live version** — replace ALL image layers with ONE framework-managed `<video>`
(the concatenated Veo background, see [live-animation.md](live-animation.md)):

```html
<video id="bg" class="clip" data-start="0" data-duration="<DUR>" data-media-start="0"
       data-track-index="1" src="assets/background.mp4" muted playsinline></video>
```
Drop the Ken Burns / crossfade JS (the video has its own motion + seamless cuts).
Keep song + captions + title + notes. Make the bg slightly LONGER than the song.

## Title + ambient

- Title card: Suez One display font, fades out a few seconds in. If the song starts
  with vocals immediately (after trimming a Suno intro), anchor the title to the TOP
  (not center) so it coexists with the first bottom caption.
- Floating music notes (♪♫♬): a few absolute divs drifting up with finite-repeat
  yoyo tweens. Gentle — kids content, not chaos.

## Verify BEFORE rendering (saves a 4-min render)

```bash
npx hyperframes lint                              # fix all ERRORS (warnings usually ok)
npx hyperframes snapshot --at 2,13,40,70,92 --describe false
# open clip/snapshots/contact-sheet.jpg → confirm art, captions, title all render.
# If frames are just the flat background → GSAP didn't load (pitfall #1).
```

## Render

```bash
cd clip && npx hyperframes render -o "../<תיאור עברי>.mp4" --quality high -f 30
```
~3027 frames for 100s @30fps; ~4 min with multiple workers. Output: 1080x1920 H.264 +
AAC. Then extract a few frames from the FINAL mp4 to confirm audio/visual sync.

## Filename (Iron Rule)

Descriptive Hebrew name matching the song title, e.g. `דוד עולה לרגל.mp4`; the live
cut gets a distinct name, e.g. `דוד עולה לרגל - מונפש.mp4`.
