---
name: kids-song-video
description: >-
  Create a personalized animated children's song music video with AI — kid picks a topic,
  Claude writes Hebrew lyrics (with niqqud), the user generates a sung track in Suno,
  Claude auto-generates a consistent character (optionally from a photo of the real child)
  via the Google Gemini image API, builds RTL niqqud karaoke captions synced with Whisper,
  composites in HyperFrames (Ken Burns / parallax / floating notes), and renders the final
  MP4 — optionally bringing the stills to life with Veo 3.1 first+last-frame animation.
  TRIGGER on Hebrew: 'סרטון שיר לילד', 'קליפ שיר ילדים', 'תעשה שיר מצויר לילד', 'שיר מונפש לילד',
  'סרטון שיר ילדים עם AI', 'קליפ שיר לילדה', 'תכין שיר עם אנימציה לילד'. English: 'kids song
  video', 'animated children song', 'children song music video', 'make a song video for my kid',
  'nursery song animation'. USE THIS when the output is a SUNG children's song turned into an
  animated music video. NOT for generic motion-graphics (use epic-video-studio), NOT for
  event montages (use event-recap-video), NOT for an explainer (use manim/epic-video-studio).
---

# Kids Song Video — קליפ שיר ילדים מונפש עם AI

## Overview

Turn a child's idea into a finished, personalized **animated music video** in one sitting —
optionally with **real AI-generated live animation**. The kid picks a topic, Claude writes the
Hebrew lyrics, a real sung song is generated (Suno), AI draws a consistent character (optionally
based on a photo of the actual child), the scenes are composited with synced karaoke captions, and
everything renders to a single MP4. As a second pass, the still scenes can be brought to life with
Veo first+last-frame video.

Adapted from the guide ["איך יוצרים שיר ילדים מצויר עם AI"](https://yuvkesh.onrender.com/blog/kids-song-video-ai-he).
Core idea — **"הורה שבונה מסך, לא דוחף מסך"**: parent and child *create* together. Keep the child in
the loop at every creative decision (topic, character, favorite line, the likeness of "their"
character). Speak plain Hebrew; keep the tech invisible.

## The pipeline at a glance

| # | Step | Engine | Local / External | Cost |
|---|------|--------|------------------|------|
| 1 | Lyrics (niqqud) | Claude (direct) | Local | Free |
| 2 | Sung song | **Suno** (guided-manual) | External | Free tier |
| 3 | Character + scenes | **Google Gemini image** (auto) | External | ~$0.02–0.13/img |
| 4 | Caption timing | faster-whisper | Local | Free |
| 5 | Compose + render | HyperFrames + GSAP | Local | Free |
| 6 | **(optional) Live animation** | **Veo 3.1** (first+last frame) | External | ~$3–26 |

Only the **song**, the **images**, and the optional **Veo clips** leave the machine. Everything
else (lyrics, timing, compositing, rendering) is local.

## Reference files (read the one you need)

- [`suno-guide.md`](suno-guide.md) — Suno prompt template, niqqud rule, **trimming the junk intro**.
- [`references/image-generation.md`](references/image-generation.md) — Gemini auto art: anchor
  character, reference-photo personalization, domain accuracy.
- [`references/composition.md`](references/composition.md) — HyperFrames assembly, RTL karaoke
  captions, **the GSAP/fonts/lint pitfalls**, render + verify.
- [`references/live-animation.md`](references/live-animation.md) — Veo first+last-frame chain,
  cost tiers, slow-mo + concat into one background.
- [`scripts/`](scripts/) — working templates: `generate_images.py`, `transcribe_song.py`,
  `generate_video.py`, `build_background.sh`. Copy into the project and edit the CONFIG block.

## Ordered workflow

### 0. Discovery (with the child, in Hebrew)
Ask: **נושא** · **גיל יעד** (vocabulary/tempo/length) · **דמויות** · **mood** (שמח-קצבי /
רגוע-לפני-שינה) · **אורך** (~1–2 דק') · **יחס מסך** (16:9 טלוויזיה/יוטיוב, 9:16 טלפון/שורטס).
Also ask **whether they want to base the character on a photo of their child** (great
personalization). Create the project folder; echo back a one-paragraph plan; confirm.

### 1. Lyrics (local)
Claude writes them directly: short, sweet, a **repeating chorus** the child can sing back; simple
concrete imagery; gentle rhyme; 2–3 verses + chorus + a short outro; give it a title. Read it to
the child; let them swap a word/character. **Write the lyrics with full niqqud** (the make-or-break
detail for Suno). Save `מילים - <title>.md`.

### 2. Song — Suno (guided-manual) — ⚠️ ESCALATION
No local sung-vocal generator exists. Prepare the niqqud lyrics + a short English style prompt +
structure tags (`[Verse]`,`[Chorus]`,`[Outro]`), per [`suno-guide.md`](suno-guide.md). Hand the
user a copy-paste pack + step-by-step. They create it on suno.com and save `assets/song.mp3`.
**Wait** for the file — its real duration/rhythm drive everything. After it arrives: probe the
duration, and **trim any Suno junk intro** (see suno-guide.md).

### 3. Character + scenes (auto — Google Gemini)
Generate the hero ONCE, then reuse it as a reference on every scene (**anchor character**) for
consistency. If a photo was provided, generate the hero FROM it (fix EXIF rotation first) and get a
likeness OK from the parent before the rest. Generate 6–8 narrative-ordered scenes. Full details +
script: [`references/image-generation.md`](references/image-generation.md). View every image; fix
drift and domain accuracy.

### 4. Caption timing (local)
`pip install faster-whisper`, then [`scripts/transcribe_song.py`](scripts/transcribe_song.py)
(`npx hyperframes transcribe` often fails on Windows — whisper-cpp missing). Trust the **timing**
only; the caption **text** is your known niqqud lyrics. Map lines via `assets/segments.txt`.

### 5. Compose + render (local — HyperFrames)
Full-bleed art + big RTL niqqud **karaoke captions** + Ken Burns + gentle floating notes + title
card, song as master audio. Mind the pitfalls (include GSAP locally, embed Hebrew fonts, init
`window.__timelines`, no `repeat:-1`, one root composition). **Snapshot before rendering.** Full
recipe + skeleton: [`references/composition.md`](references/composition.md). Render to a descriptive
Hebrew filename.

### 6. (Optional) Live animation — Veo 3.1
If the user wants real motion: generate a seamless **chain** of first+last-frame clips
(scene1→2→…→N→1), assemble into one slow-mo'd background, and swap it in for the still layers.
Confirm the cost tier first (their Google billing). Full recipe:
[`references/live-animation.md`](references/live-animation.md).

### 7. Deliver + verify
Descriptive Hebrew filename (live cut gets its own, e.g. `… - מונפש.mp4`). Extract frames from the
FINAL mp4 to confirm audio sync, caption timing, no clipped characters, correct aspect ratio.

## Escalation points (offer alternatives before asking — Iron Rule #1)
1. **Suno (always manual):** user runs Suno, returns `song.mp3`.
2. **Image API key:** read `GOOGLE_API_KEY` from the environment (get one free at Google AI Studio).
   If missing → offer to add a key, or fall back to manual Midjourney prompts.
3. **Veo spend:** live animation costs real money on the user's Google billing — present tiers
   (Lite/Fast/Standard) and confirm before generating.

## Anti-patterns
- Don't animate/caption before `song.mp3` exists — the song defines all timing.
- Don't skip niqqud (Suno) — it's the difference between Hebrew and gibberish.
- Don't skip the anchor-character reference — the kid will look different every scene.
- Don't render before a snapshot — a flat-background snapshot means GSAP didn't load.
- Don't drift art styles between images; don't over-animate (gentle suits kids).
- Don't ship the Suno junk intro — trim it and shift caption timings.

## Definition of Done
A single rendered **MP4**: a real sung Hebrew song (intro trimmed), a consistent animated character
(optionally resembling the real child), karaoke niqqud captions synced to the vocals, a Hebrew
title/outro, gentle ambient motion, the correct aspect ratio, and a descriptive Hebrew filename —
plus, if requested, a fully **live (Veo-animated)** cut.

## Credits & References
- Original guide: <https://yuvkesh.onrender.com/blog/kids-song-video-ai-he>
- [Suno](https://suno.com) · HyperFrames (local) · Google Gemini image + Veo (via `GOOGLE_API_KEY`)
