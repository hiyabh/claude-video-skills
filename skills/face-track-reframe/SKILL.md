---
name: face-track-reframe
description: "Reframe/crop a video to a different aspect ratio while keeping the speaker's face centered and never cut off, using dynamic face tracking. The crop window follows the face across the whole clip (handles a person who moves within the frame). TRIGGER on Hebrew: 'תחתוך סרטון', 'התאם יחס וידאו', 'תהפוך סרטון לעומד', 'סרטון אופקי לעומד', 'שהפנים לא ייחתכו', 'מעקב פנים', 'להתאים את הסרטון ליחס של השאר', 'crop ליחס עומד'. English: 'reframe video', 'crop video to portrait', 'horizontal to vertical', 'make this 9:16', 'keep the face in frame', 'face tracking crop', 'fit aspect ratio'. Use when a video's aspect ratio must change (e.g. landscape -> 9:16 portrait) without losing the face. NOT for editing montages (event-recap-video), NOT for generating video (video-production)."
---

# Face-Tracking Video Reframe

Crop a video to a target aspect ratio so it matches other clips (e.g. a horizontal
848x384 clip into a 9:16 portrait), while a **dynamic crop window tracks the speaker's
face** — the face stays centered and is never cut off, even as the person moves.

This solves the problem a static center-crop can't: when the face drifts left/right
(or up/down) over the clip, a fixed window clips it at the edges. Here the window
follows the detected face on a smoothed path.

## Requirements

- `ffmpeg` + `ffprobe` on PATH
- Python with `opencv-python` and `numpy`
  - check: `python -c "import cv2, numpy"` — if it fails: `pip install opencv-python numpy`

## How to Use

The script does everything (detect → smooth track → crop → scale → mux original audio).

```bash
python ~/.claude/skills/face-track-reframe/reframe.py INPUT [options]
```

Run it from the folder containing the video (so relative output lands there), or pass
absolute paths. On Windows PowerShell, quote paths with Hebrew/spaces.

### Options

| Option | Default | Meaning |
|---|---|---|
| `-o, --output` | `<name>_reframe.mp4` | output path |
| `--aspect W:H` | `9:16` | target ratio, e.g. `4:5`, `1:1`, `16:9` |
| `--size WxH` | (derived) | exact output resolution — use to match other clips byte-for-byte (e.g. `464x848`) |
| `--smooth SEC` | `0.6` | tracking smoothing window; raise for steadier motion, lower to track faster |
| `--crf N` | `18` | x264 quality (lower = better/larger) |

### Recommended workflow

1. **Probe the target clips first** to learn the dominant resolution/ratio to match:
   ```bash
   ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 OTHER.mp4
   ```
   Most portrait phone clips are `9:16` (e.g. `464x848`, `576x1024`, `1080x1920`).
2. **Run with `--size`** set to that resolution so the output drops straight into the set:
   ```bash
   python ".../reframe.py" "שמחה.MP4" --size 464x848 -o "שמחה_עומד.mp4"
   ```
3. **Verify** by extracting a few frames across the clip and viewing them — confirm the
   face is centered start/middle/end:
   ```bash
   for t in 1 $((DUR/2)) $((DUR-1)); do ffmpeg -v error -ss $t -i OUT.mp4 -frames:v 1 _chk_$t.jpg -y; done
   ```
   Read the JPGs. If the face drifts to an edge, raise `--smooth` won't help — instead the
   clip likely has two people / fast motion; consider lowering `--smooth` to track tighter.

## How It Works

1. **Detect** — every frame is scanned with OpenCV Haar cascades (frontal, then profile,
   then mirrored profile for the other side). Largest face wins. ~80%+ frames usually hit.
2. **Fill + smooth** — missing frames are linearly interpolated; the face-center path is
   moving-average smoothed (`--smooth` seconds) for natural, jitter-free motion.
3. **Window** — crop dims are derived from source-vs-target ratio:
   - source wider than target → crop **width**, track horizontally (the common case)
   - source taller than target → crop **height**, track vertically
4. **Render** — each frame is cropped at its tracked origin, Lanczos-scaled to the output
   size, and piped to ffmpeg, which re-muxes the **original audio** (`libx264`/`aac`).

## Notes & Limits

- Built for a **single speaker**. With multiple faces it follows the largest one.
- Haar cascades miss heavily-turned/occluded faces — interpolation covers short gaps.
- Output never upscales beyond what `--size` requests; default keeps the crop's native size.
- Always keep the original file; the script only writes the new output.
