#!/usr/bin/env node
// Scaffold a starter Three.js + GSAP ScrollTrigger scene.
// Usage: node scaffold-scene.mjs <out-dir>
//
// Generates:
//   <out-dir>/index.html
//   <out-dir>/main.js
//   <out-dir>/style.css
//   <out-dir>/package.json
//
// Then: cd <out-dir> && npm install && npm run dev

import { mkdir, writeFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { join, resolve } from 'node:path';

const outDir = resolve(process.argv[2] || './threejs-scene');

if (existsSync(outDir)) {
  console.error(`Directory exists: ${outDir}`);
  process.exit(1);
}

await mkdir(outDir, { recursive: true });

const indexHtml = `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Three.js Scroll Cinema</title>
  <link rel="stylesheet" href="./style.css" />
</head>
<body>
  <section id="cinema">
    <canvas id="canvas"></canvas>
    <div class="overlay">
      <h1>Scroll</h1>
    </div>
  </section>
  <section class="filler"><h2>End</h2></section>
  <script type="module" src="./main.js"></script>
</body>
</html>
`;

const styleCss = `* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { height: 100%; }
body { font: 16px/1.5 system-ui, sans-serif; background: #0a0a0a; color: #fff; }

#cinema { position: relative; width: 100%; height: 100vh; }
#canvas { position: absolute; inset: 0; width: 100%; height: 100%; }
.overlay {
  position: absolute; inset: 0;
  display: grid; place-items: center;
  pointer-events: none;
}
.overlay h1 { font-size: clamp(3rem, 10vw, 8rem); letter-spacing: -0.03em; }

.filler {
  height: 100vh;
  display: grid; place-items: center;
  background: linear-gradient(180deg, #0a0a0a, #111);
}

@media (prefers-reduced-motion: reduce) {
  .overlay h1 { animation: none !important; }
}
`;

const mainJs = `import * as THREE from 'three';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

// ---------- scene ----------
const canvas = document.getElementById('canvas');
const scene = new THREE.Scene();
scene.background = new THREE.Color('#0a0a0a');

const camera = new THREE.PerspectiveCamera(50, innerWidth / innerHeight, 0.1, 100);
camera.position.set(0, 0, 8);

const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.outputColorSpace = THREE.SRGBColorSpace;

// ---------- lights ----------
scene.add(new THREE.AmbientLight(0xffffff, 0.3));

const key = new THREE.DirectionalLight(0xffffff, 1.4);
key.position.set(4, 6, 4);
key.castShadow = true;
key.shadow.mapSize.set(1024, 1024);
scene.add(key);

const rim = new THREE.DirectionalLight(0xff7755, 0.6);
rim.position.set(-3, 2, -4);
scene.add(rim);

// ---------- subject ----------
const geo = new THREE.IcosahedronGeometry(1.2, 1);
const mat = new THREE.MeshStandardMaterial({
  color: '#bccaff',
  roughness: 0.3,
  metalness: 0.6,
  flatShading: true,
});
const hero = new THREE.Mesh(geo, mat);
hero.castShadow = true;
scene.add(hero);

// ---------- floor ----------
const floor = new THREE.Mesh(
  new THREE.PlaneGeometry(20, 20),
  new THREE.MeshStandardMaterial({ color: '#1a1a1a', roughness: 0.9 }),
);
floor.rotation.x = -Math.PI / 2;
floor.position.y = -1.6;
floor.receiveShadow = true;
scene.add(floor);

// ---------- scroll-driven timeline ----------
if (!reduceMotion) {
  const tl = gsap.timeline({
    scrollTrigger: {
      trigger: '#cinema',
      start: 'top top',
      end: '+=300%',
      scrub: 1,
      pin: true,
      anticipatePin: 1,
    },
  });

  tl.to(camera.position, { z: 4, ease: 'power2.inOut' }, 0)
    .to(hero.rotation, { y: Math.PI * 1.5, ease: 'power2.inOut' }, 0)
    .to(camera.position, { z: 2, x: 1, y: 0.5, ease: 'power2.inOut' }, 0.8)
    .to(hero.rotation, { y: Math.PI * 3, x: Math.PI / 4, ease: 'power2.inOut' }, 0.8)
    .to(camera.position, { z: 6, x: 0, y: 1, ease: 'power3.inOut' }, 1.6);
}

// ---------- resize ----------
window.addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});

// ---------- loop ----------
renderer.setAnimationLoop(() => renderer.render(scene, camera));
`;

const packageJson = `{
  "name": "threejs-scroll-cinema-starter",
  "version": "0.0.1",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "gsap": "^3.12.5",
    "three": "^0.160.0"
  },
  "devDependencies": {
    "vite": "^5.0.0"
  }
}
`;

await Promise.all([
  writeFile(join(outDir, 'index.html'), indexHtml),
  writeFile(join(outDir, 'main.js'), mainJs),
  writeFile(join(outDir, 'style.css'), styleCss),
  writeFile(join(outDir, 'package.json'), packageJson),
]);

console.log(`Scaffolded at ${outDir}`);
console.log(`Next: cd ${outDir} && npm install && npm run dev`);
