---
name: epic-video-studio
description: "Produce a high-end, wow-factor custom video by orchestrating THREE engines together — HyperFrames (the compositor: kinetic text, titles, captions, transitions, audio, final MP4 render), Manim (math/concept/explainer animations rendered to MP4), and Text-To-Lottie (vector micro-animations authored as lottie.json). This is the master pipeline skill: it plans the video, decides which engine renders each beat, generates every asset, assembles them in HyperFrames, and renders the final cut. TRIGGER on Hebrew: 'סרטון מטורף', 'תעשה סרטון מטורף', 'סרטון מושלם', 'סרטון אדיר', 'סרטון אנימציה מקצועי', 'סרטון הסבר עם אנימציות', 'סרטון עם טקסט מעברים ואנימציות', 'תבנה לי סרטון וואו', 'סרטון מוטיון גרפיקס'. English: 'make me an insane video', 'epic explainer video', 'crazy motion-graphics video', 'wow video with animations', 'polished animated video', 'kinetic typography plus animation', 'build the full video pipeline'. USE THIS (not the others) when the video needs MORE THAN ONE of: kinetic typography/transitions, explainer/math animation, and vector micro-animation. NOT for photo/clip montages from an event (use event-recap-video), NOT for AI-generated live-action footage (use video-production), NOT when a single HTML composition with no Manim/Lottie suffices (use hyperframes directly)."
---

# Epic Video Studio — the 3-engine orchestration pipeline

This skill is the **conductor**. It does not replace `hyperframes`, `manim-composer`,
or `text-to-lottie` — it drives them in the right order and wires their outputs
together into one polished video. Read this first, then invoke the per-engine
skills for the actual authoring.

## The three engines and their jobs

| Engine | Owns | Produces | How it lands in the final video |
|--------|------|----------|---------------------------------|
| **HyperFrames** | Timeline, kinetic text/titles, captions, transitions, audio sync, **final render** | The composition itself (HTML → MP4) | It IS the shell — everything else embeds into it |
| **Manim** | Math / concept / data / "explainer" animation (3b1b style) | `assets/*.mp4` | `<video muted playsinline>` inside a non-timed wrapper div |
| **Text-To-Lottie** | Lightweight vector motion: icons, logo reveals, accents, loaders, data-driven flourishes | `assets/*.json` (Bodymovin) | `lottie` adapter → registered on `window.__hfLottie` |

**Golden rule:** HyperFrames is always the outermost layer that unifies and renders.
Manim and Text-To-Lottie only produce **assets** that get embedded.

## Which engine for which beat?

Decide per beat during planning:
- Pure **text / title card / lower-third / transition / caption** → HyperFrames native (GSAP).
- **Explaining a concept, equation, graph, step-by-step, geometry, data transform** → Manim clip.
- **A small vector accent**: animated icon, logo reveal, checkmark, loader, badge,
  micro-interaction, decorative flourish → Text-To-Lottie.
- A beat can layer all three (e.g. Manim clip in the background + Lottie icon overlay
  + kinetic headline on top). That layering is exactly what makes it feel "insane".

## Ordered workflow

### 0. Plan (always)
- Invoke the **`hyperframes`** skill for intent → structure → beats (read its
  `references/video-composition.md`; brand vs. layout).
- For any explainer beats, invoke **`manim-composer`** to plan scenes (scenes.md).
- Produce a one-screen beat sheet: for each beat, note **engine(s)**, duration,
  text, and asset filenames. This is the contract for step 2.

### 1. Scaffold the HyperFrames project
- `npx hyperframes init` (see `hyperframes-cli`). Create an `assets/` folder.

### 2. Generate assets — in parallel where possible
- **Narration / audio** (optional): `hyperframes-media` → `tts` for voiceover,
  then `transcribe` to get caption timings.
- **Manim clips**: author each Scene per `manimce-best-practices`, then
  `manim render` → `assets/<scene>.mp4`. Prefer transparent or
  composition-matched backgrounds so they layer cleanly.
- **Lottie animations**: invoke the **`text-to-lottie`** skill. It scaffolds the
  Skottie player (`npx degit diffusionstudio/lottie <dir>`), you write
  `public/lottie.json`, preview live (`npm run dev`, pin frames with
  `?frame=N&paused=1`), then copy the verified JSON to `assets/<name>.json`.

### 3. Assemble in HyperFrames
- Build the **end state first** (final layout of every beat) before adding motion —
  this is a HyperFrames hard rule; it prevents invisible overlaps.
- Embed Manim MP4s: `<video muted playsinline>` in a **non-timed wrapper div**;
  audio always a separate `<audio>`. Never call `video.play()`/`audio.play()` from GSAP.
- Embed Lottie via the **`lottie`** adapter: `autoplay:false`, `loop:false`,
  push every instance onto `window.__hfLottie` (HyperFrames seeks them all to
  composition time). Animate a **wrapper**, never the media element itself.

### 4. Verify + render
- `npx hyperframes lint` → `npx hyperframes inspect` (layout audit).
- `npx hyperframes preview` — **visual check** (also catches the Skottie/lottie-web
  difference below).
- `npx hyperframes render` — final MP4. Confirm the file wrote and its size.

## ⚠️ The one gotcha that bites: Skottie ≠ lottie-web
- `text-to-lottie` authors and verifies against **Skottie** (Skia / `canvaskit-wasm`).
- HyperFrames' `lottie` adapter renders with **lottie-web / dotLottie**.
- Standard Bodymovin (shape layers `ty:4`, transforms, keyframes, fills/strokes)
  renders in **both**. Skottie-only features (slots, some expressions) may render
  differently or blank in lottie-web.
- **Always** re-verify each exported Lottie inside `npx hyperframes preview`
  (which uses lottie-web) before the final render. If it looks wrong, simplify the
  JSON to plain shape layers.

## Skills this orchestrates (all installed)
- Compositor: `hyperframes`, `hyperframes-cli`, `hyperframes-media`, `hyperframes-registry`,
  adapters `lottie` / `gsap` / `animejs` / `css-animations` / `waapi`
- Explainer animation: `manim-composer`, `manim-skill`, `manimce-best-practices`
- Vector motion generation: `text-to-lottie` (from `diffusionstudio/lottie`)

## Definition of done
- A single rendered MP4 from HyperFrames that combines at least two of the three
  engines (kinetic text/transitions + Manim and/or Lottie), passing `lint` and
  visually confirmed in `preview` before `render`.
- Every Lottie verified in lottie-web (via preview), not only in the Skottie player.

See `docs/video-pipeline.md` in the claude-general workspace for the same pipeline
as a quick-reference table.
