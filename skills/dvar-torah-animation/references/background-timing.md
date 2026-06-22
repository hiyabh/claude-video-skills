# ⭐ Background timing — the core of the skill

A drasha video lives or dies on whether each illustration appears **exactly when the narrator
reaches its topic**. Read this fully before building a background.

## The model: anchors
Each shot is `(kind, ref, anchor)`:
- `kind` — `'v'` (a Veo clip) or `'i'` (a still → Ken Burns).
- `ref` — which clip/still.
- `anchor` — the **composition-time second** the narrator says that topic's words.

Shot durations are derived: `dur[k] = anchor[k+1] - anchor[k]`, last shot runs to `TOTAL`. In the
xfade chain, **offset_k = anchor[k]**, so each shot fades IN exactly at its anchor — a visual never
precedes its words. Anchors must be monotonic; assert `min(dur) > D` (the crossfade).

## 🪤 THE TRAP — the intro-silence offset (the #1 bug)
The composition usually prepends a **title card** with a **~2.5s silence** at the head of the
narration MP3. Consequences:
- A raw Whisper `captions.json` runs at **origin 0** (no silence).
- But the audio *in the composition* — and therefore the words the viewer hears — is shifted
  **+2.5s**.
- The **`GROUPS` array inside `index.html` is the ground truth**: its word/group times already
  include the offset (they were authored against the real composition audio).

**Always derive anchors from `GROUPS`, never from a raw origin-0 transcript.** We shipped a version
where anchors came from origin-0 captions and every image landed ~2.5s early — the user caught it
immediately ("the images appear before the narration reaches that topic"). Open `index.html`, read
the `GROUPS` array, find the group whose words introduce a topic, use its `s` (start) as the anchor.

To get anchors: for each shot, pick the **first words that introduce its topic**, look up that
group's `s` in `GROUPS`, use it. Keep a one-line comment per shot quoting the words — it makes the
mapping auditable and is how you fix it later.

## Fast cuts
- ~**5–6s per shot**; ~30–40 shots for ~3 min. (11 shots × 18s each = "boring"; that was the
  original complaint.)
- **Reuse hero shots** where a topic recurs — but give the repeat a **different Ken-Burns motion**
  (vary by shot index, not by source) so it doesn't read as identical.
- Short crossfade `D = 0.4s` for snappy cuts.

## Ken Burns (stills → motion), jitter-free
Pre-scale large (≈3×) so sub-pixel pan is smooth, then `zoompan` with linear motion on `on`
(output frame), output `s=1080x1920`. Vary preset by shot index so repeats differ:
`0` zoom-in · `1` zoom-out · `2` pan-right · `3` pan-left · `4` pan-up. (See `build_bg_fast.py`.)

## Veo clips → seamless loop
Ping-pong (forward + `reverse` concat) → smooth loop, then `-stream_loop` to the shot length. Vary
the `-ss` start offset per appearance so a reused clip doesn't look identical.

## Assemble & length
- xfade-chain all shots; total = `sum(dur) + D` if you trim `D` off the last, or build anchors so
  `sum(dur) == TOTAL` then pad.
- `TOTAL` must equal the composition `data-duration`. Frame-rounding leaves a ~0.3s shortfall —
  fix with `tpad=stop_mode=clone:stop_duration=0.6` then `-t TOTAL` (a brief freeze on the final
  Shabbat-table / closing shot, which looks intentional).

## Verify (don't trust the build log)
Sample frames **just after a few anchors** and confirm the **image and the burned-in caption talk
about the same topic**. Three good spot-checks across the film beat one full strip. Example checks
that should line up: caption "to find a match" ↔ chuppah; "marriage counselor" ↔ Aharon reconciling
a couple; "check the tap" ↔ the glowing faucet.
