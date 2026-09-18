# Camera Rig

The camera is the actor. Its motion IS the story.

## Lens choice (FOV)

| FOV | Effect | Use for |
|-----|--------|---------|
| 35° | Telephoto, compressed depth | Product close-ups, hero detail |
| 50° | Cinematic standard | Default for most scenes |
| 65° | Slightly wide, immersive | Establishing shots |
| 75°+ | Wide, distorted edges | Avoid unless intentional |

Animating FOV mid-scroll = "dolly zoom" (Vertigo effect). Powerful, use sparingly.

```js
gsap.to(camera, { fov: 35, onUpdate: () => camera.updateProjectionMatrix() });
```

## Position & lookAt

Always set `lookAt` AFTER position changes. Common mistake: tweening `position` but never updating `lookAt`.

```js
const target = new THREE.Vector3(0, 0, 0);
function update() {
  camera.lookAt(target);
}
gsap.to(target, { x: 2, y: 1, onUpdate: update });
gsap.to(camera.position, { z: 4, onUpdate: update }, '<');
```

For complex paths, use a `Vector3` for both position and target — animate the vectors, call `lookAt` once per frame.

## Dolly (push in / pull out)

```js
tl.to(camera.position, { z: '-=4', ease: 'power2.inOut', duration: 1 });
```

Pure z-axis change. Combine with FOV change for cinematic compression.

## Orbit (around a point)

```js
const radius = 5;
const proxy = { angle: 0 };
tl.to(proxy, {
  angle: Math.PI * 2,
  duration: 1,
  ease: 'none',
  onUpdate: () => {
    camera.position.x = Math.sin(proxy.angle) * radius;
    camera.position.z = Math.cos(proxy.angle) * radius;
    camera.lookAt(0, 0, 0);
  },
});
```

For slow majestic orbits, use `none` (linear). For dramatic reveals, use `power2.inOut`.

## Spline path

For non-circular paths, use `CatmullRomCurve3`:

```js
const curve = new THREE.CatmullRomCurve3([
  new THREE.Vector3(0, 0, 8),
  new THREE.Vector3(2, 1, 5),
  new THREE.Vector3(0, 2, 2),
  new THREE.Vector3(-2, 1, 0),
]);
const proxy = { t: 0 };
tl.to(proxy, {
  t: 1,
  ease: 'power1.inOut',
  onUpdate: () => {
    curve.getPointAt(proxy.t, camera.position);
    camera.lookAt(0, 0, 0);
  },
});
```

`getPointAt` (vs `getPoint`) gives uniform speed along the curve — feels more natural.

## ScrollTrigger pinning

```js
ScrollTrigger.create({
  trigger: '#cinema',
  start: 'top top',
  end: '+=300%',  // scroll 3× viewport height before unpinning
  pin: true,
  pinSpacing: true,  // reserves space so layout doesn't jump
  scrub: 1,          // 1s smoothing — feels less twitchy than scrub: true
  anticipatePin: 1,  // prevents jitter at start
});
```

`end` examples:
- `+=200%` — 2 viewport heights of scroll
- `bottom top` — until trigger's bottom hits viewport top

## Multi-section camera path

Use a master timeline with labels per section:

```js
const tl = gsap.timeline({
  scrollTrigger: { /* ... */ scrub: 1, pin: '#cinema' }
});

tl.addLabel('intro')
  .to(camera.position, { z: 6 }, 'intro')
  .addLabel('product', '+=1')
  .to(camera.position, { z: 2, x: 1 }, 'product')
  .to(camera.rotation, { y: Math.PI / 4 }, 'product')
  .addLabel('outro', '+=1')
  .to(camera.position, { z: 10, y: 3 }, 'outro');
```

Labels make scroll progress legible and refactorable.

## Camera shake (optional flourish)

```js
const shake = { x: 0, y: 0 };
gsap.to(shake, {
  x: () => (Math.random() - 0.5) * 0.05,
  y: () => (Math.random() - 0.5) * 0.05,
  repeat: -1,
  duration: 0.05,
  onUpdate: () => {
    camera.position.x += shake.x;
    camera.position.y += shake.y;
  },
});
```

Use during impact moments (text reveal, model snap-in). Disable during smooth dollies.

## Common bugs

- **Camera spins wildly** → forgot to call `lookAt` after position change
- **Scroll feels laggy** → `scrub: true` is too tight; try `scrub: 1` or `scrub: 0.5`
- **Pin section jumps on scroll start** → add `anticipatePin: 1`
- **Camera jitters at high zoom** → `near` plane too small; raise to `0.5`
