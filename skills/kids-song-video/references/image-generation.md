# Character Art — automatic, consistent (Google Gemini)

This replaces the old "write Midjourney prompts manually" path. Illustrations are
generated **automatically** with the Google Gemini image API. Script template:
[`scripts/generate_images.py`](../scripts/generate_images.py).

## API key (no new signup)

Set your own `GOOGLE_API_KEY` (from Google AI Studio) as an environment variable.
The script reads it from the `GOOGLE_API_KEY` env var. Verify which
image models the key can use:

```bash
gkey="${GOOGLE_API_KEY:?set GOOGLE_API_KEY first}"
curl -s "https://generativelanguage.googleapis.com/v1beta/models?key=$gkey" | grep -o 'models/[a-z0-9.-]*image[a-z0-9.-]*'
```

Prefer **`gemini-3-pro-image`** (a.k.a. Nano Banana Pro) — it accepts a reference
image, which is what makes character consistency work. `imagen-4.0-*` is text-only.

If the key is missing/empty → ESCALATE: offer to add a provider key, or fall back to
the manual Midjourney path. Other keys in the same `.env`: `FAL_KEY`, `XAI_API_KEY`,
`RUNWAY_API_KEY`, `ELEVENLABS_API_KEY`.

## Technique 1 — Anchor character (mandatory for consistency)

Generate the hero **once**, then pass that PNG as a reference image (+ a "same
character, identical face/hair/clothing" note) on **every** scene call. Without this,
the child looks different in every frame. The API call shape:

```json
{
  "contents": [{ "parts": [
    { "text": "<scene prompt> <STYLE>" },
    { "inlineData": { "mimeType": "image/png", "data": "<hero png base64>" } },
    { "text": "Keep the child's face, hair and clothing EXACTLY identical to the reference." }
  ]}],
  "generationConfig": { "responseModalities": ["IMAGE"], "imageConfig": { "aspectRatio": "9:16" } }
}
```
Response image bytes: `candidates[0].content.parts[].inlineData.data` (base64).

## Technique 2 — Reference photo of the real child (personalization)

If the parent provides a photo, generate the hero FROM it so the cartoon resembles
their kid (and keeps real details, e.g. a knitted kippah). This is a big delight win.

- **Fix orientation first.** Phone photos carry EXIF rotation; the API sees them
  sideways. `PIL.ImageOps.exif_transpose(img)` then downscale (~1024px) before upload.
- Prompt: "Create a full-body storybook cartoon of the child in the reference photo.
  KEEP the facial likeness (face shape, skin tone, eyes, hair) and the kippah/hat.
  Turn them into a cute ~5-year-old cartoon with a big smile. Dress them in
  <costume that fits the song>." Append a strong "MUST resemble the photo" note.
- Always show the generated hero to the parent for a likeness OK before generating
  the 8 scenes (cheap checkpoint; they care about this).

## Scene planning

- 6-8 scenes that follow the lyric narrative, in order (so the live-animation chain
  flows). One isolated hero + scene backgrounds.
- Keep ONE child in frame unless the lyric needs a crowd (the model sometimes
  duplicates the hero — say "ONLY ONE boy/girl" in the prompt).
- Same `STYLE` suffix on every call (palette, line weight, "storybook illustration").
- `aspectRatio`: "9:16" for shorts/phone, "16:9" for TV/YouTube.

## Verify + iterate

- View every generated PNG. Regenerate any scene that drifts (wrong character, wrong
  object). The script is idempotent per-name — just rerun a single scene.
- Domain accuracy matters: e.g. for a Beit-HaMikdash song the model defaults to a
  golden DOME (Dome of the Rock). Specify "tall RECTANGULAR stone temple, golden roof
  with spikes, columns, NO dome, not a mosque" to get the Jewish Temple.
- Keep reused scenes under distinct filenames if the composition references an image
  twice (HyperFrames lint warns on duplicate media src).
