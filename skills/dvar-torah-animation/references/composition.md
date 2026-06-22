# Composition, tempo, endcard, render

HyperFrames composites everything: it embeds `assets/background.mp4` as the video layer +
`assets/audio.mp3` + a JS-driven caption/brand/closing-card timeline. To revise a drasha you
usually **swap only `assets/background.mp4` + `assets/audio.mp3`** and re-render.

## The composition (`clip/index.html`)
Key timed pieces (all in one `<script>`, registered on `window.__timelines`):
- `<video id="bg" data-duration="...">` + `<audio id="aud" data-duration="...">` — the layers.
- `var GROUPS = [...]` — per-group, per-word caption timings (`s`, `e`, `w:[[word,start,end]…]`).
  Karaoke highlight = `tl.set("#cg-i-wj",{className:"wd hot"},start)` then back to `wd` at `end`.
- `var DUR`, `var LAST` — composition length and last caption end.
- An intro **title card** (the ~2.5s head — source of the offset trap), a top **brand strip**, and
  a **closing card** ("שבת שלום").

### Lint pitfalls
- `npm run check` must be **0 errors** before render. The standing 2 GSAP warnings
  (`overlapping_gsap_tweens`, `gsap_studio_edit_blocked`) are pre-existing and fine.
- **Move any backup `*_orig.html` OUT of `clip/`** — two files with `data-composition-id` trigger
  `multiple_root_compositions` (and duplicate audio). Keep backups in `build/backup_orig/`.

## Tempo speed-up (optional but common — "make it a bit faster")
`scale_timing.py` at `TEMPO≈1.10`. **Tempo and sync are coupled** — speeding the audio alone breaks
everything; you must rescale in lockstep:
1. `atempo=TEMPO` on the audio (pitch preserved; valid 0.5–2.0).
2. Divide by TEMPO: **every** `GROUPS` time (group `s/e` and each word), `DUR`, `LAST`, and all
   three `data-duration` attributes.
3. Divide the **background anchors** by the **same TEMPO** (shared constant in `build_bg_fast.py`),
   rebuild the background, re-pad to the new `DUR`.
`1.10` takes a 3:14 drasha to ~2:58 — noticeably snappier, still natural for Torah narration.

## Credit endcard (logo + attribution)
`make_endcard.py` (PIL + **python-bidi** for RTL Hebrew; no reshaper needed for Hebrew). 1080×1920,
warm-dark gradient + gold radial glow, centered logo, gold/cream credit lines. Then `make_final.py`:
- builds a 2s endcard clip (`fade=t=in`, silent 48k stereo AAC),
- **concats** main + endcard (re-encode for a safe stream join — `concat=n=2:v=1:a=1`),
- emits **master** (crf18) and **share** (crf26 + `+faststart`).
Logo path for "בין קודש לקוד": `../לוגו חדש בין קודש לקוד.png`. Credit copy used:
*"דבר תורה מונפש / מתוך הבלוג ״שם הבלוג שלך״ / מאת הרב פלוני אלמוני"*.

## Render
```
npx hyperframes@<ver> render --fps 30 --quality high -o renders/clip_fast.mp4
```
A ~3-min 1080×1920 high render takes ~7–8 min. The CLI holds output until done — when you background
it, **redirect to a log (`> log 2>&1`), never pipe to `head`** (SIGPIPE kills it).

## Verify end-to-end
- Background duration == `DUR` == audio duration (after any tempo pass).
- Sample frames just after a few anchors → image matches the caption (see background-timing.md).
- Confirm the modesty-sensitive frames (bride tichel, clergy garments).
- Confirm the endcard appears after the closing card with the logo + credit.
