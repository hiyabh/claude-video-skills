---
name: dvar-torah-animation
description: >-
  Turn a written or recorded Torah-thought / drasha (parsha insight, mussar talk, holiday
  sermon) into a finished, animated 9:16 social video — Hebrew TTS or supplied narration,
  per-word niqqud karaoke captions synced with Whisper, a fast-cut B-roll background of 2D
  illustrations (Google Gemini image) each timed to the exact moment the narrator reaches
  its topic, optional Veo 3.1 live animation, a tempo speed-up pass, and a logo/credit
  endcard — composited in HyperFrames and rendered to MP4 (master + share).
  TRIGGER on Hebrew: 'הנפש דרשה', 'סרטון דבר תורה מונפש', 'תעשה דבר תורה מונפש', 'דרשה מונפשת',
  'סרטון על הפרשה', 'דבר תורה מצויר', 'הנפשה של דבר תורה', 'סרטון פרשת שבוע', 'תנפיש את הדרשה'.
  English: 'animated dvar torah', 'animate this sermon', 'parsha video', 'drasha animation',
  'Torah thought video', 'animated Jewish sermon'. USE THIS when the output is a SPOKEN
  Torah/drasha turned into an animated reel with thematic illustrated B-roll behind narration
  + captions. NOT for a sung song (use kids-song-video), NOT for an event montage
  (use event-recap-video), NOT for generic motion-graphics (use epic-video-studio).
---

# Dvar Torah Animation — הנפשת דרשות

## Overview

Turn a drasha into a polished **9:16 animated reel**: narration (TTS or supplied) + per-word
niqqud **karaoke captions** + a **fast-cut illustrated background** where every shot is timed to
the exact second the narrator reaches its topic, finished with a **credit endcard**. Built and
proven on the *Chukat — זוגיות ופרנסה* video.

Core principle — **the visual must never precede the audio.** A boring drasha video is one where
11 illustrations each sit on screen for 15-20s. A great one cuts every ~5s to a *new* image that
matches *the words being spoken right now*. Getting that sync exactly right is the whole game, and
it has one non-obvious trap (the intro-silence offset) documented below.

## 🧢 Characters MUST be religious-Zionist (Dati-Leumi) — mandatory
Every human figure must fit the **religious-Zionist (ציונות דתית / Dati-Leumi)** world, NOT
chareidi and NOT secular. This is a hard requirement, not a style preference:
- **Men & boys** wear a **knitted kippah (kippah seruga)** — the Dati-Leumi marker — **NOT a
  chareidi black hat / shtreimel**; modern-modest dress, shirt with tzitzit, beard optional.
- **Married women** cover their hair with a **tichel/headscarf** (face visible); a **bride wears a
  tichel, NOT a face veil**; modest long sleeves + skirt.
- **Girls** do not cover their hair (only married women do).
- **Exception — biblical/Temple scenes**: period desert garb; clergy (Aharon/Kohen Gadol) in
  accurate bigdei kehuna (choshen + mitznefet), and must not touch a woman.
This is enforced by the STYLE block in [`references/image-generation.md`](references/image-generation.md);
the exact wording was approved by the user after several rejected rounds — do not soften it, and
**eyeball the modesty-sensitive frames** before continuing.

## The pipeline at a glance

| # | Step | Engine | Local / External | Cost |
|---|------|--------|------------------|------|
| 1 | Script + segment it | Claude (direct) | Local | Free |
| 2 | Narration audio | HyperFrames TTS *or* supplied MP3 | Local/given | Free |
| 3 | Word-level caption timing | faster-whisper | Local | Free |
| 4 | Illustrations (2D B-roll) | **Google Gemini image** (`gemini-3-pro-image`) | External | ~$0.02–0.13/img |
| 5 | *(optional)* Live animation | **Veo 3.1** fast/lite | External | ~$0.10–3/clip |
| 6 | Fast-cut timed background | ffmpeg (Ken Burns + xfade) | Local | Free |
| 7 | Compose (captions, cards) + render | HyperFrames + GSAP | Local | Free |
| 8 | *(optional)* Tempo speed-up | ffmpeg atempo + rescale | Local | Free |
| 9 | Credit endcard + master/share | PIL + ffmpeg | Local | Free |

Only the **images** (and optional **Veo clips**) leave the machine.

## ⭐ The one thing that matters most: timing the background to the words

This is the heart of the skill — read [`references/background-timing.md`](references/background-timing.md)
**before building any background.** The short version:

1. Each background shot gets an explicit **anchor time** = the composition-time second the
   narrator says that topic's words.
2. **THE TRAP:** the narration MP3 usually has a **~2.5s silence at the start** (for the intro
   title card). So word timings in the composition are offset +2.5s from the raw Whisper
   transcript. The **`GROUPS` array inside `index.html` is the ground truth** (it already
   includes the offset). Derive anchors from `GROUPS`, NOT from a raw `captions.json` at origin 0
   — or every image will appear ~2.5s too early. This was the actual bug we hit.
3. Shots cross-fade IN at their anchor (offset = anchor), so a visual never precedes its words.
4. Aim ~5–6s per shot, ~30–40 shots for a 3-minute drasha. Reuse hero shots where a topic
   repeats, with a different Ken-Burns motion so repeats don't read as identical.

## Reference files (read the one you need)

- [`references/image-generation.md`](references/image-generation.md) — Gemini `gemini-3-pro-image`,
  the **religious-Zionist modesty STYLE block** (kippah/tzitzit, headscarf-not-veil, bride in a
  tichel), domain accuracy (Aharon's bigdei kehuna), normalize to 1080×1920.
- [`references/veo-animation.md`](references/veo-animation.md) — Veo 3.1 first-frame animation,
  **per-model quota**, the `predictLongRunning` billing warning, fast vs lite.
- [`references/background-timing.md`](references/background-timing.md) — ⭐ anchors, the intro
  offset, fast cuts, xfade chain, Ken Burns presets.
- [`references/composition.md`](references/composition.md) — HyperFrames assembly, **tempo
  speed-up + rescale**, the credit endcard, lint pitfalls, render + verify, master/share.
- [`scripts/`](scripts/) — working templates: `gen_scenes.py`, `build_bg_fast.py`,
  `scale_timing.py`, `make_endcard.py`, `make_final.py`. Copy into `build/`, edit the CONFIG block.

## Ordered workflow

### 0. Discovery (Hebrew)
Confirm: **the drasha text** (or recording) · **parsha/topic** · **target audience** (this drives
illustration style + modesty level — default **religious-Zionist**) · **length** · supplied
narration MP3 or generate TTS · whether to spend on **Veo** or stay **free** (Ken-Burns-only).
Create `build/`; echo back a one-paragraph plan; confirm before spending on images.

### 1. Script → segments (local)
Split the drasha into narration paragraphs (`narration_segs.json`: idx, text, start, end). If
reusing an existing project's audio+captions (same text), reuse them fully — saves TTS.

### 2. Narration + caption timing
TTS via `hyperframes-media` (Kokoro) **or** use a supplied MP3. Transcribe with Whisper for
**word-level** timing. Captions become the `GROUPS` array in the composition (see composition.md).
**Remember the intro-silence offset** when the composition prepends a title card.

### 3. Illustrations (the B-roll)
`gen_scenes.py`: one illustration per topic beat, 9:16, **same STYLE block every call** for visual
consistency. Generate **2–3× more images than narration paragraphs** so cuts can be fast. Verify a
few sensitive ones visually (clergy garments, modesty) before continuing — see image-generation.md.

### 4. *(optional)* Live animation
Animate key stills with Veo 3.1 (`veo-animation.md`). Quota is **per-model** — when `*-fast` is
exhausted, `*-lite` still works. Stills not animated by Veo are animated for free via Ken Burns.

### 5. Fast-cut timed background
`build_bg_fast.py`: define `SHOTS = [(kind, ref, anchor), …]` with anchors read from `GROUPS`.
Veo clips → ping-pong + loop; stills → Ken Burns zoompan. xfade-chain at the anchors. Pad to the
composition duration. **Never `python build.py | head -N`** — SIGPIPE kills long ffmpeg builds
mid-run; redirect to a log instead.

### 6. Compose + render
Drop the background + audio into the HyperFrames `clip/`, keep the caption/brand/closing-card JS.
`npm run check` (move any backup `*_orig.html` OUT of `clip/` — duplicate `data-composition-id`
errors). Render `--fps 30 --quality high`.

### 7. *(optional)* Speed-up pass
`scale_timing.py` at `TEMPO≈1.10`: `atempo` the audio (pitch preserved) and divide **every**
timing (`GROUPS`, `DUR`, `LAST`, `data-duration`, and the background anchors) by the same TEMPO.
~1.10 takes a 3:14 drasha to ~2:58 — noticeable but natural.

### 8. Endcard + delivery
`make_endcard.py` (PIL + python-bidi, RTL) for a 2s logo/credit card → `make_final.py` concatenates
it and emits **master** (high) + **share** (crf26 + faststart). Verify timing by sampling frames
right after a few anchors and confirming the **image and the caption talk about the same topic**.

## Hard-won insights (do not relearn these)
- **Anchor from `GROUPS`, not raw captions** — the intro-silence offset (~2.5s) is the #1 sync bug.
- **`| head -N` on a long build = SIGPIPE = dead build.** Use `> log 2>&1`.
- **Veo quota is per-model.** 429 on `veo-3.1-fast` ≠ blocked; `veo-3.1-lite` is a separate bucket
  and near-identical quality for flat 2D art.
- **`predictLongRunning` bills immediately** — it *starts* generation; never "test" it without
  saving the operation name.
- **Characters are religious-Zionist (Dati-Leumi), and it's literal.** Men/boys: **knitted kippah
  (kippah seruga), NOT a chareidi black hat** + tzitzit; women: **headscarf (tichel), not a face
  veil**; a **bride wears a tichel, face uncovered**; clergy in accurate bigdei kehuna
  (choshen/mitznefet). Verify these specific frames visually.
- **Reuse the whole `clip/`** from a prior drasha — swap only `assets/background.mp4` + `audio.mp3`;
  captions/cards are just timed JS you rescale.
- **Tempo + sync are coupled.** If you speed the audio, you MUST rescale captions AND background
  anchors by the same factor or sync breaks.
