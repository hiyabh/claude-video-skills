# Live Animation (optional) — Veo 3.1 first+last-frame chain

Turn the still scenes into **real moving video**. The user's framing: image 1 is the
opening frame, image 2 is the closing frame, and a live clip animates between them;
then image 2 becomes the next opening frame, and so on — "until everything is alive",
looping back to the start. That is exactly **first+last-frame image-to-video**, chained.

Scripts: [`scripts/generate_video.py`](../scripts/generate_video.py) (generate) +
[`scripts/build_background.sh`](../scripts/build_background.sh) (assemble).

## Why the chain is seamless

Clip N animates `scene_N → scene_{N+1}`; clip N+1 animates `scene_{N+1} → scene_{N+2}`.
The boundary frame is identical, so clips concatenate with **hard cuts and no visible
seam** — no crossfade needed. Add a final `scene_last → scene_01` clip for a perfect
loop.

## Model + cost (ALWAYS confirm tier with the user — real money on their billing)

Same `GOOGLE_API_KEY`. Only **Veo 3.1** supports `lastFrame`:
`veo-3.1-lite-generate-preview` / `-fast-` / `-generate-preview` (and `veo-2.0` = first
frame only). **Verify current pricing** (it changes) — as of 2026:

| Tier | ~ $/sec | 8 clips × 8s |
|------|---------|--------------|
| 3.1 Lite | 0.05 | ~$3 |
| 3.1 Fast | 0.15 | ~$10 |
| 3.1 Standard | 0.40 | ~$26 |

We don't use Veo's generated audio (the Suno song is the track), so a cheap tier is
fine. Offer the choice; default recommend Lite/Fast.

## API (long-running operation)

```
POST /v1beta/models/<MODEL>:predictLongRunning?key=KEY
{ "instances": [{ "prompt": "...", "image": {bytesBase64Encoded, mimeType},
                  "lastFrame": {bytesBase64Encoded, mimeType} }],
  "parameters": { "aspectRatio": "9:16" } }
→ { "name": "models/.../operations/..." }
```
Poll `GET /v1beta/{operation.name}?key=KEY` every ~10s until `done:true`. Video at
`response.generateVideoResponse.generatedSamples[0].video` — either
`bytesBase64Encoded` or a `uri` (append `?key=KEY` to download). Output ≈ 8s, 720×1280.

**Test ONE clip first** (`python generate_video.py 1`) to validate the flow and spend
a few cents before committing to all 8.

## Assemble to a single background (fills the song length)

8 clips × 8s = 64s native; the song is usually longer. `build_background.sh`:
1. **Slow each clip** to fill the song, smoothly: `setpts=FACTOR*PTS` +
   `minterpolate=fps=30:mi_mode=mci` (motion-compensated → smooth slow-mo, ~44s/clip),
   and `scale=1080:1920`. `FACTOR = song_seconds / (n_clips * 8)`.
2. **Concat** (relative paths in the list — MSYS `/c/...` paths fail in ffmpeg; entries
   like `proc/clip_01.mp4` resolved from the list file's dir).
3. **Pad** the end (`tpad=stop_mode=clone:stop_duration=0.8`) so the bg is slightly
   longer than the song (else the tail freezes/blacks out).

Then wire `assets/background.mp4` into the live composition (see
[composition.md](composition.md) → "Live version").

## Note on tempo

`minterpolate` slow-mo looks dreamy. For a "happy & rhythmic" brief it can feel a touch
slow — reduce FACTOR (less stretch) and accept a shorter live montage, or generate more
clips. Confirm the vibe from a snapshot before the full render.
