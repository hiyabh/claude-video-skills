# Live animation — Veo 3.1 (optional)

Bring key stills to life. **Optional** — Ken Burns (free) is a perfectly good fallback, and in a
fast-cut background the difference is subtle. Spend on Veo only for hero beats, or skip entirely.

## Models & quota — the key insight
**Quota is per-model**, separate buckets:
- `veo-3.1-fast` — best quality, smallest daily quota. Exhausts first (429 "exceeded quota").
- `veo-3.1-lite` — **cheap, near-identical quality for flat 2D illustration**, separate bucket.
- `veo-3.1`, `veo-2.0` — further fallbacks, each its own bucket.

So a 429 on `*-fast` does **not** mean you're blocked — drop to `veo-3.1-lite` and keep going. On
the Chukat video, 4 clips ran on `*-fast` before it capped, then 7 on `*-lite`, all same style.

## ⚠️ Billing warning
`predictLongRunning` **starts (and bills) generation immediately** — it is not a dry run. Never
"just test" it. Always capture the returned **operation name** and poll it; losing the name means
you paid for a clip you can't fetch.

## Pattern
1. `POST .../models/<model>:predictLongRunning` with the still as the first frame + a short motion
   prompt ("gentle ambient motion, subtle parallax, the candle flames flicker").
2. Save `operation.name`. Poll `GET .../operations/<name>` until `done`.
3. Download the MP4. Clips are ~4–8s.
4. In the background builder, ping-pong each clip (forward+reverse) for a seamless loop, then loop
   to the shot length.

## When to prefer Ken Burns instead
- Symbolic stills (pipe, coins, scale, candles) — a slow zoom/pan reads as alive enough.
- Any shot under ~5s in a fast cut.
- Budget = free.
Mix freely: Veo for a few hero shots, Ken Burns for the rest. The fast-cut builder handles both
kinds (`kind='v'` vs `kind='i'`).
