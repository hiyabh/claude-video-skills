# Design — אמונה בת 40

## Palette
- bg-deep: #160D2B (edges)
- bg-core: #2A1850 (radial center)
- gold: #F6C453
- gold-bright: #FFE08A
- ivory: #FFF8EC
- rose: #FF8FB1
- violet: #9F7AEA

## Typography
- Display: 'Secular One', 'Heebo', sans-serif — titles
- Body: 'Heebo', sans-serif — kickers, subtitles
- All text RTL (direction: rtl)

## Motion
- Springy entrances (back.out, elastic.out), varied eases
- Confetti: seeded PRNG only (mulberry32), finite repeats
- No exit animations except final scene / overlay outs

## Canvas
- 576×1024 portrait, 30fps
- Cards: opaque radial bg. Lower-thirds: transparent (webm alpha)
