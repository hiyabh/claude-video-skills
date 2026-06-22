# Depth & Parallax

Two strategies: real geometry depth, or layered-image fakery. Pick based on asset budget.

## Strategy A — Real meshes at staggered z

Each layer is a `Mesh` (or group) at a different z-coordinate. Camera move = automatic parallax.

```js
const layers = [
  { mesh: bgMountains, z: -20, parallaxFactor: 0.1 },
  { mesh: midTrees,    z: -10, parallaxFactor: 0.4 },
  { mesh: fgRocks,     z: -2,  parallaxFactor: 1.0 },
];

layers.forEach(({ mesh, z }) => {
  mesh.position.z = z;
  scene.add(mesh);
});
```

Best for: real 3D assets, full freedom of camera path, dynamic lighting.

Cost: model authoring time, draw calls, file size.

## Strategy B — Layered PNG planes (image-stack)

Take a flat image, slice into 4-6 layers (background, midground, subject, foreground, vignette). Each is a `PlaneGeometry` with a transparent texture, positioned at different z.

```js
function makeLayer(textureUrl, z, scale = 10) {
  const tex = new THREE.TextureLoader().load(textureUrl);
  tex.colorSpace = THREE.SRGBColorSpace;
  const mat = new THREE.MeshBasicMaterial({ map: tex, transparent: true });
  const geo = new THREE.PlaneGeometry(scale * (innerWidth / innerHeight), scale);
  const mesh = new THREE.Mesh(geo, mat);
  mesh.position.z = z;
  return mesh;
}

scene.add(makeLayer('/layers/sky.png',     -8));
scene.add(makeLayer('/layers/mountain.png', -5));
scene.add(makeLayer('/layers/trees.png',   -2));
scene.add(makeLayer('/layers/subject.png',  0));
scene.add(makeLayer('/layers/grass.png',    1));
```

Camera dolly from z=8 → z=0 walks "into" the scene. Layers parallax automatically because they're at different z.

Best for: design-led scenes, fast iteration, no 3D modeling skills required, mobile-friendly.

Cost: less freedom for camera angle (planes look flat from the side).

## Slicing source images

Tools:
- Photoshop: layer masks, export each as transparent PNG
- Photopea: free Photoshop alternative in browser
- Procreate (iPad): same workflow
- AI: Stable Diffusion + segmentation models (BiRefNet, RMBG) for auto-extraction

Rule of thumb: 4-6 layers max. More = clutter, fewer = obviously fake.

## Depth-map displacement (advanced)

Single image + depth map → real parallax via vertex displacement.

```js
import { TextureLoader } from 'three';

const colorTex = new TextureLoader().load('/photo.jpg');
const depthTex = new TextureLoader().load('/photo-depth.png');

const geo = new THREE.PlaneGeometry(10, 10, 200, 200);
const mat = new THREE.MeshStandardMaterial({
  map: colorTex,
  displacementMap: depthTex,
  displacementScale: 1.5,
});
scene.add(new THREE.Mesh(geo, mat));
```

Generate depth maps with: MiDaS, ZoeDepth, Marigold (HuggingFace).

Camera tilt now reveals real 3D structure. Magic.

## Parallax math (when not using real depth)

For 2D-style parallax driven by scroll progress:

```js
const progress = { v: 0 };
ScrollTrigger.create({
  trigger: '#hero', start: 'top top', end: '+=200%', scrub: 1,
  onUpdate: (st) => { progress.v = st.progress; },
});

function update() {
  layers.forEach((layer, i) => {
    layer.mesh.position.y = -progress.v * (i + 1) * 0.5;
  });
}
renderer.setAnimationLoop(() => { update(); renderer.render(scene, camera); });
```

Each layer moves further per scroll — back layers slowest, foreground fastest. Mimics real parallax.

## Rules

1. **Z-spacing matters.** Layers at z=0,-1,-2 feel cramped. Use -8, -5, -2, 0, 1 for breathing room.
2. **Foreground vignette.** A dark/blurred PNG at z=2 just past the camera adds cinematic frame.
3. **Texture format.** Use `.webp` over `.png` when alpha allowed. ~50% smaller.
4. **Power-of-2 textures.** Three.js mipmaps require 1024², 2048². Non-POT textures lose mipmaps and look harsh.
5. **Subject at z=0.** Anchor the hero element at z=0 so camera math centers on it.

## Common bugs

- **Layers visible from wrong side** → set `material.side = THREE.FrontSide` (default is correct, but worth checking)
- **Edges glow** → texture has fringing; re-export with proper alpha matting
- **Layers stack incorrectly** → all layers at same z; use `renderOrder` or stagger z slightly
- **Mobile washed out** → texture not in sRGB; set `texture.colorSpace = THREE.SRGBColorSpace`
