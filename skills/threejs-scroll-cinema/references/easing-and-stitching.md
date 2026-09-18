# Easing & Scene Stitching

The difference between "stop-motion" and "one continuous shot" is easing + overlap.

## Easing cheatsheet

GSAP eases (visit greensock.com/ease-visualizer for a visual reference):

| Ease | Feel | Use for |
|------|------|---------|
| `none` (linear) | Mechanical | Constant scroll-mapped motion (rare) |
| `power1.inOut` | Gentle in/out | Subtle camera drifts |
| `power2.inOut` | Default cinematic | Most camera moves |
| `power3.inOut` | Snappy | Impact, reveals |
| `power4.inOut` | Aggressive | Dramatic snaps |
| `expo.out` | Fast start, soft land | Object reveals from off-screen |
| `expo.inOut` | Slow start, fast middle, soft land | Big reveals |
| `back.out(1.7)` | Overshoot | Springy UI, never camera |
| `elastic.out` | Bouncy | UI confetti, never cinema |
| `circ.inOut` | Smooth round | Camera arcs |
| `sine.inOut` | Subtle wave | Idle floats, breathing |

**Default:** `power2.inOut`. **Cinematic standard:** `power3.inOut`. **Never linear** for scroll-mapped 3D.

## Stitch rule — overlap, don't butt

Sections that just touch each other feel choppy. Overlap them by 10-20% so motion blends.

```js
const tl = gsap.timeline({ scrollTrigger: { /* ... */ scrub: 1 } });

// Section 1: 0 → 1.0
tl.to(camera.position, { z: 5, ease: 'power2.inOut' }, 0)
  .to(camera.rotation, { y: 0.3, ease: 'power2.inOut' }, 0);

// Section 2 STARTS at 0.8 (overlap with section 1)
tl.to(camera.position, { z: 2, ease: 'power2.inOut' }, 0.8)
  .to(camera.rotation, { y: 0.6, ease: 'power2.inOut' }, 0.8);

// Section 3 STARTS at 1.6
tl.to(camera.position, { z: 0, ease: 'power3.inOut' }, 1.6);
```

The 0.2 overlap = the boundary blur. Without it, you see the seam.

## Two-track choreography

Long scenes need two parallel "tracks" — camera, and content. Each owns its own timeline section.

```js
const cameraTrack = gsap.timeline();
cameraTrack
  .to(camera.position, { z: 5 }, 0)
  .to(camera.position, { z: 2 }, 1)
  .to(camera.position, { z: 0 }, 2);

const contentTrack = gsap.timeline();
contentTrack
  .from('.title', { opacity: 0, y: 50 }, 0.2)
  .from('.subtitle', { opacity: 0, y: 30 }, 0.6)
  .to('.title', { opacity: 0 }, 1.5);

const master = gsap.timeline({ scrollTrigger: { /* ... */ scrub: 1, pin: true } });
master.add(cameraTrack, 0).add(contentTrack, 0);
```

Tracks run in parallel, share the master scroll progress.

## Continuous scene checklist

Per the screenshot's step 7 — "feels like one continuous scene":

- [ ] No "tween-ends-then-other-tween-starts" gaps. Always overlap.
- [ ] Camera never freezes mid-scene unless intentional pause.
- [ ] No same-axis duplicates (don't rotate camera AND its parent group on Y).
- [ ] One ease language. Pick `power2.inOut` family and stick to it. Mixing `expo` with `back` jars.
- [ ] Audio (if any) bridges section boundaries — never hard-cuts.
- [ ] Section transitions hide their seams under motion (camera moving = seam invisible).
- [ ] Test scrubbing slowly AND quickly — should feel smooth at both speeds.

## Smoothing scroll input

Native scroll on Mac trackpad is buttery; on Windows mouse-wheel it's stuttery. Add `lenis` for uniform smoothness:

```js
import Lenis from 'lenis';
const lenis = new Lenis({ duration: 1.2, smoothWheel: true });
function raf(time) { lenis.raf(time); requestAnimationFrame(raf); }
requestAnimationFrame(raf);

// Tell ScrollTrigger to use lenis
lenis.on('scroll', ScrollTrigger.update);
gsap.ticker.add((time) => lenis.raf(time * 1000));
gsap.ticker.lagSmoothing(0);
```

Lenis adds ~5KB. Worth it for cinematic projects.

`scrub: 1` (1 second smoothing) is also a poor-man's lenis — no extra dep.

## Scrub values explained

```js
scrub: true   // hard sync, choppy on Windows wheel
scrub: 0.5    // half-second catchup smoothing
scrub: 1      // 1s catchup (default cinematic)
scrub: 2      // very lazy, feels delayed
```

Pick `1` unless you have a reason.

## Pause / hold / breathe

To freeze camera mid-scroll — add `+=N` to timeline position:

```js
tl.to(camera.position, { z: 5 }, 0)
  .addPause('+=0.5')              // hold for 0.5 of scroll
  .to(camera.position, { z: 2 }, '+=0.5');
```

Or insert a `to` of duration 0 with no targets. Or insert a label and tween nothing for that segment.

## Common bugs

- **Section feels choppy** → no overlap. Move section start back 10-20% of duration.
- **Final pose looks "snapped"** → switched ease at boundary; keep same ease across overlap.
- **Scrub feels delayed** → too high (try 0.5).
- **Scrub feels twitchy** → too low (try 1 or add lenis).
- **Pin section flickers** → `anticipatePin: 1` missing.
