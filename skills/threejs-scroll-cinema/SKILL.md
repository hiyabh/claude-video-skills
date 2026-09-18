---
name: threejs-scroll-cinema
description: Build scroll-based cinematic 3D scenes with Three.js + GSAP ScrollTrigger. Covers camera animation, depth/parallax via layered images or meshes, lighting, easing, and scene-stitching. Use when user wants WebGL hero sections, immersive product reveals, scroll-driven 3D, layered parallax, "cinematic scroll", "Three.js hero", "סצנה תלת ממדית", or "סקרול קולנועי".
---

# Three.js Scroll Cinema

Build scroll-driven 3D experiences that feel like one continuous cinematic shot. Three.js for the scene, GSAP + ScrollTrigger for the timeline.

## When to use

- WebGL hero with camera dolly/zoom on scroll
- Product page where the model rotates/reveals as user scrolls
- Layered-image parallax that mimics depth without a full 3D model
- Multi-section storytelling stitched as a single camera path

## When NOT to use

- Static 3D viewer with no scroll → just `OrbitControls`, no ScrollTrigger
- Pure 2D parallax → use `framer-motion` skill instead
- Video playback synced to scroll → use plain `<video>` + ScrollTrigger
- Heavy game-like physics → out of scope

## Stack contract

```
three            ^0.160 (or latest)
gsap             ^3.12
gsap/ScrollTrigger
(optional) @react-three/fiber + @react-three/drei  // for React projects
(optional) lenis ^1.0                              // for smooth scroll
```

R3F note: if the project already uses React, prefer `@react-three/fiber`. Use `useScroll` from `@react-three/drei` for scroll progress; ScrollTrigger still works but R3F's render loop owns the canvas.

## The 7-step recipe

1. **Plan the scroll** — sketch what camera does at scroll % 0, 25, 50, 75, 100. Write each keyframe as `position`, `lookAt`, `fov`.
2. **Prompt for assets** — depth maps for parallax, glTF for models, HDRI for environment lighting.
3. **Install** — `npm i three gsap` (+ R3F if React).
4. **Wire scroll → scene state** — single ScrollTrigger pinning the canvas, `scrub: true`, mapped to a master GSAP timeline.
5. **Add layered depth** — either real meshes at staggered z, or 4-6 PNG planes with translateZ.
6. **Light + ease** — ambient + directional with shadow; `power2.inOut` between sections, never linear.
7. **Polish until continuous** — no hard cuts. If it feels segmented, blend boundaries with overlapping timeline sections.

## Core API

| Object | Purpose | Key props |
|--------|---------|-----------|
| `Scene` | World container | `.add(obj)`, `.background` |
| `PerspectiveCamera` | Cinematic lens | `fov`, `position`, `lookAt(v3)` |
| `WebGLRenderer` | Output | `setPixelRatio`, `setSize`, `shadowMap.enabled` |
| `Mesh` | Geometry + material | `position`, `rotation`, `scale` |
| `DirectionalLight` | Sun-like | `intensity`, `position`, `castShadow` |
| `AmbientLight` | Fill | `intensity`, `color` |
| `ScrollTrigger.create` | Scroll → progress | `trigger`, `start`, `end`, `scrub`, `pin` |
| `gsap.timeline()` | Sequence keyframes | `.to(target, {props}, position)` |

## Minimal pattern

```js
import * as THREE from 'three';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
gsap.registerPlugin(ScrollTrigger);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(50, innerWidth/innerHeight, 0.1, 100);
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
document.body.appendChild(renderer.domElement);

camera.position.set(0, 0, 8);
scene.add(new THREE.AmbientLight(0xffffff, 0.4));
const sun = new THREE.DirectionalLight(0xffffff, 1.2);
sun.position.set(3, 5, 4);
scene.add(sun);

// ... add meshes ...

const tl = gsap.timeline({
  scrollTrigger: {
    trigger: '#hero',
    start: 'top top',
    end: '+=300%',
    scrub: 1,
    pin: true,
  }
});
tl.to(camera.position, { z: 2, duration: 1 }, 0)
  .to(camera.rotation, { y: Math.PI/4, duration: 1 }, 0.5);

renderer.setAnimationLoop(() => renderer.render(scene, camera));
```

## Rules (non-negotiable)

1. **One render loop.** Use `renderer.setAnimationLoop` OR R3F. Never both. Never spawn extra `requestAnimationFrame`.
2. **Scrub, don't tween-on-trigger.** Scroll-driven scenes use `scrub: true` (or numeric for smoothing). Never trigger discrete `gsap.to` from a ScrollTrigger callback — you'll desync.
3. **Dispose on unmount.** Geometry, materials, textures, renderer — call `.dispose()`. Otherwise WebGL context leaks crash the tab.
4. **DPR cap = 2.** `setPixelRatio(Math.min(devicePixelRatio, 2))` — Retina × 3 wrecks mobile FPS.
5. **Respect `prefers-reduced-motion`.** If true: skip the cinema, render a static frame at scroll-50%.
6. **Mobile fallback.** Scenes with > 100k tris should detect mobile and swap to a poster image OR a simplified mesh count.
7. **No layout-shift on resize.** Update camera aspect + renderer size in `resize` handler, not on next render.
8. **Cross-link, don't duplicate GSAP.** Detailed ScrollTrigger usage lives in the [gsap skill](../gsap/SKILL.md). This skill assumes you've read it.

## Anti-patterns

| ✗ Wrong | ✓ Right |
|---------|---------|
| `setInterval(render, 16)` | `renderer.setAnimationLoop(render)` |
| `ScrollTrigger.create({ onEnter: () => gsap.to(camera, ...) })` | `gsap.timeline({ scrollTrigger: { scrub: true } })` |
| Animate `camera.position.x` AND a parent group's `x` for the same effect | Pick one transform owner |
| Linear easing between sections | `power2.inOut`, `expo.out` for natural motion |
| New `WebGLRenderer` per route | Single renderer, swap scenes |

## Performance budget

- 60fps desktop, 30fps mobile minimum
- < 200k triangles total
- < 8 lights (1 directional + 1 ambient + ≤ 6 point/spot)
- Texture size ≤ 2048² (use mipmaps)
- Single shadow caster, `shadow.mapSize` ≤ 1024

## Output checklist

- [ ] ScrollTrigger pins the canvas section
- [ ] Camera path planned at 5 scroll keyframes
- [ ] Layered depth (≥ 3 z-levels) for parallax
- [ ] Ambient + directional light, shadows on hero mesh
- [ ] DPR capped at 2
- [ ] `prefers-reduced-motion` fallback
- [ ] Resize handler updates aspect + size
- [ ] Dispose hook on unmount
- [ ] Tested at 320px, 768px, 1440px widths
- [ ] No `console.log` left in render loop

## References (loaded on demand)

- [Camera rig](references/camera-rig.md) — FOV, lookAt, dolly, orbit, ScrollTrigger pinning
- [Depth & parallax](references/depth-parallax.md) — layered planes, z-stagger, image-stack technique
- [Lighting](references/lighting.md) — ambient + directional + spot, shadow maps, HDRI
- [Easing & stitching](references/easing-and-stitching.md) — easing curves, blending sections
- [Performance](references/perf.md) — DPR cap, frustum culling, draw calls, mobile fallback
- [Scaffold script](scripts/scaffold-scene.mjs) — generates a starter scene + ScrollTrigger
