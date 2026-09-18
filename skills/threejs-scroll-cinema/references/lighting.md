# Lighting

Cinematic mood = lighting. Three.js has 6 light types; use 2-3, never all.

## Light types

| Light | Source | Use for |
|-------|--------|---------|
| `AmbientLight` | Everywhere, no direction | Fill — never alone |
| `HemisphereLight` | Sky color + ground color | Outdoor fill, more natural than ambient |
| `DirectionalLight` | Sun (parallel rays) | Key light, casts shadows |
| `PointLight` | Bulb (radial) | Lamps, fires, accents |
| `SpotLight` | Cone | Stage spots, headlights |
| `RectAreaLight` | Panel (soft rect) | Studio softboxes, screens |

## Three-point setup (default)

The cinematographer's classic. Cover 90% of cases.

```js
// 1. Key — main light
const key = new THREE.DirectionalLight(0xffffff, 1.2);
key.position.set(5, 8, 5);
key.castShadow = true;
key.shadow.mapSize.set(1024, 1024);
key.shadow.camera.near = 1;
key.shadow.camera.far = 50;
scene.add(key);

// 2. Fill — softer, opposite side, no shadow
const fill = new THREE.DirectionalLight(0xa3c8ff, 0.4);
fill.position.set(-4, 3, 2);
scene.add(fill);

// 3. Rim — behind subject, separates from background
const rim = new THREE.DirectionalLight(0xff9966, 0.6);
rim.position.set(-2, 4, -5);
scene.add(rim);

scene.add(new THREE.AmbientLight(0xffffff, 0.15));
```

Color temperature: warm key (~5600K white) + cool fill (~7000K bluish) creates depth.

## HDRI environment (best quality)

Use an HDR equirectangular image as the lighting source. Dramatic improvement over manual lights.

```js
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';

new RGBELoader().load('/hdri/studio.hdr', (tex) => {
  tex.mapping = THREE.EquirectangularReflectionMapping;
  scene.environment = tex;        // lights all PBR materials
  scene.background = tex;         // optional: visible HDRI
});
```

Free HDRIs: polyhaven.com (CC0).

When using HDRI, often you only need ONE additional directional light for shadows.

## Shadows

Shadows are expensive. Default off — opt in per light + per mesh.

```js
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;  // softer edges than default

key.castShadow = true;
key.shadow.mapSize.set(1024, 1024);  // higher = sharper, slower

heroMesh.castShadow = true;
floorMesh.receiveShadow = true;
```

Shadow camera frustum must wrap the casters:

```js
key.shadow.camera.left = -5;
key.shadow.camera.right = 5;
key.shadow.camera.top = 5;
key.shadow.camera.bottom = -5;
key.shadow.camera.near = 0.5;
key.shadow.camera.far = 30;
```

Too tight = clipped shadows. Too loose = pixelated shadows.

## Animating light on scroll

Light intensity, color, or position can be tweened — same as camera:

```js
tl.to(key, { intensity: 0.3, ease: 'power2.inOut' }, 'sunset')
  .to(key.color, { r: 1, g: 0.6, b: 0.3 }, 'sunset');
```

Changes mood: noon → sunset → night, all in one scroll.

## Tone mapping

Three.js renders linear — without tone mapping, scenes look flat or blown out.

```js
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
renderer.outputColorSpace = THREE.SRGBColorSpace;
```

`ACESFilmicToneMapping` is the cinematic default. Adjust `toneMappingExposure` (0.8-1.5) for mood.

## Materials & lighting

| Material | Lit by | Best for |
|----------|--------|----------|
| `MeshBasicMaterial` | Nothing | UI, billboards, unlit FX |
| `MeshLambertMaterial` | All lights, flat | Cheap; cartoon style |
| `MeshPhongMaterial` | All lights + specular | Mid-tier, slightly shiny |
| `MeshStandardMaterial` | All lights + PBR | Default for realism |
| `MeshPhysicalMaterial` | + clearcoat, sheen | Cars, fabric, glass |

Use `MeshStandardMaterial` for realistic; `MeshBasicMaterial` for UI overlays.

## Rules

1. **Never only ambient.** Flat = boring. Always pair with directional.
2. **Cap light count at 8.** More = perf cost, no visual gain.
3. **Single shadow caster.** Multiple shadow-casting lights destroys mobile FPS.
4. **HDRI > manual lights** for product shots.
5. **Tone mapping always on.**
6. **Shadow.mapSize ≤ 2048.** Anything larger is rarely worth it.

## Common bugs

- **Whole scene black** → no lights, or all materials `MeshBasicMaterial` was changed to `MeshStandardMaterial` (now needs lights)
- **Shadows look pixelated** → increase `shadow.mapSize` or tighten shadow camera
- **Shadows missing** → check `renderer.shadowMap.enabled`, light's `castShadow`, mesh's `castShadow`/`receiveShadow`
- **Colors washed out** → no tone mapping
- **HDRI rotates wrong** → `tex.mapping = THREE.EquirectangularReflectionMapping` not `ReflectionMapping`
