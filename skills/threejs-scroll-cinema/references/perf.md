# Performance

WebGL on a phone = a budget. Spend wisely or your scene becomes a slideshow.

## Targets

| Device | FPS | Tris budget | DPR cap |
|--------|-----|-------------|---------|
| Desktop high-end | 60 | 500k | 2 |
| Desktop mid | 60 | 200k | 2 |
| Mobile high-end (iPhone 14+) | 60 | 100k | 2 |
| Mobile mid | 30 | 50k | 1.5 |
| Mobile low | poster fallback | n/a | n/a |

## DPR (device pixel ratio)

Retina × 3 means 9× the pixels. Cap it.

```js
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
```

On low-end phones, drop to `1.5`:

```js
const dpr = isMobile() ? Math.min(devicePixelRatio, 1.5) : Math.min(devicePixelRatio, 2);
renderer.setPixelRatio(dpr);
```

## Mobile detection + fallback

```js
function isMobile() {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

function isLowEnd() {
  return navigator.hardwareConcurrency <= 4 || (navigator.deviceMemory || 4) <= 4;
}

if (isLowEnd()) {
  document.querySelector('#cinema').innerHTML = '<img src="/poster.jpg" alt="Hero" />';
  return;  // skip Three.js entirely
}
```

## Reduced motion

```js
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

if (reduceMotion) {
  // Render a static frame at scroll 50%
  renderer.render(scene, camera);
  return;
}
```

## Geometry budget

- Hero mesh: ≤ 50k triangles
- Total scene: ≤ 200k triangles
- Use `BufferGeometryUtils.mergeGeometries` to combine static meshes → one draw call

## Texture budget

- Textures: ≤ 2048² (1024² is plenty for most)
- Format: WebP > JPG > PNG
- Use `KTX2 / Basis` compression for big textures (saves 5-10×)
- Always set `texture.anisotropy = renderer.capabilities.getMaxAnisotropy()` for sharp angles

## Draw calls

Aim for ≤ 50 draw calls. Check via:

```js
console.log(renderer.info.render);
// { calls, triangles, frame, lines, points }
```

Reduction tactics:
- Merge geometries
- Use instancing (`InstancedMesh`) for repeated objects (trees, particles)
- Use texture atlases (one big texture instead of many small)

## Lighting cost

| Setup | Cost |
|-------|------|
| 1 ambient + 1 directional | Cheap |
| + 1 shadow caster | Mid |
| + HDRI environment | Mid |
| Multiple shadow casters | Expensive |
| Real-time shadows on mobile | Avoid |

For mobile, consider baked lighting (textures with light pre-baked in).

## Frustum culling

Three.js culls automatically — but only if `mesh.frustumCulled = true` (default). Don't disable unless you really need.

## Animation loop hygiene

```js
// ✗ Wrong — uncapped, no pause
requestAnimationFrame(function loop() {
  renderer.render(scene, camera);
  requestAnimationFrame(loop);
});

// ✓ Right — uses Three.js loop, can be stopped
renderer.setAnimationLoop(() => renderer.render(scene, camera));

// To stop:
renderer.setAnimationLoop(null);
```

## Pause when off-screen

```js
const observer = new IntersectionObserver(([entry]) => {
  if (entry.isIntersecting) {
    renderer.setAnimationLoop(() => renderer.render(scene, camera));
  } else {
    renderer.setAnimationLoop(null);
  }
});
observer.observe(canvas);
```

Saves enormous battery on long pages where the scene scrolls off.

## Disposal — IRON RULE

WebGL objects don't garbage-collect. Manual disposal required when removing/swapping:

```js
function dispose(obj) {
  obj.traverse((child) => {
    if (child.geometry) child.geometry.dispose();
    if (child.material) {
      if (Array.isArray(child.material)) child.material.forEach((m) => disposeMaterial(m));
      else disposeMaterial(child.material);
    }
  });
}

function disposeMaterial(mat) {
  Object.keys(mat).forEach((key) => {
    if (mat[key]?.isTexture) mat[key].dispose();
  });
  mat.dispose();
}

// On unmount:
scene.remove(heroGroup);
dispose(heroGroup);
renderer.dispose();
```

Forgetting → memory leak → tab crash after 3-4 page swaps.

## Profiling

- Chrome DevTools → Performance tab → record while scrolling
- Look for: long frames (> 16.7ms), GC pauses, layout thrashing
- `stats.js` widget for in-page FPS:

```js
import Stats from 'stats.js';
const stats = new Stats();
document.body.appendChild(stats.dom);
renderer.setAnimationLoop(() => {
  stats.begin();
  renderer.render(scene, camera);
  stats.end();
});
```

## Common perf bugs

- **FPS drops on scroll only** → ScrollTrigger callback doing heavy work; move to render loop
- **Memory grows over time** → not disposing on swap
- **Tab crashes on iOS** → too many high-res textures; compress with KTX2
- **Stutters every few seconds** → garbage collection from new vector allocations in render loop. Reuse vectors.

```js
// ✗ Wrong — allocates every frame
renderer.setAnimationLoop(() => {
  const v = new THREE.Vector3(0, 0, 1);
  obj.position.add(v);
});

// ✓ Right — allocate once
const tmp = new THREE.Vector3(0, 0, 1);
renderer.setAnimationLoop(() => {
  obj.position.add(tmp);
});
```
