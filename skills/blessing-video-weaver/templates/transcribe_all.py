# -*- coding: utf-8 -*-
"""Transcribe all sibling clips to word-level Hebrew transcripts (faster-whisper)."""
import json
import os
import sys
import time

from faster_whisper import WhisperModel

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE, "סרטונים")
OUT_DIR = os.path.join(BASE, "work", "transcripts")
MODEL_SIZE = sys.argv[1] if len(sys.argv) > 1 else "small"
ONLY = sys.argv[2] if len(sys.argv) > 2 else None

os.makedirs(OUT_DIR, exist_ok=True)
model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")

clips = sorted(f for f in os.listdir(SRC_DIR) if f.lower().endswith((".mp4", ".mov")))
if ONLY:
    clips = [c for c in clips if ONLY in c]

for clip in clips:
    name = os.path.splitext(clip)[0]
    out_path = os.path.join(OUT_DIR, name + ".json")
    if os.path.exists(out_path):
        print(f"skip (exists): {name}", flush=True)
        continue
    t0 = time.time()
    use_vad = "--no-vad" not in sys.argv
    segments, info = model.transcribe(
        os.path.join(SRC_DIR, clip),
        language="he",
        word_timestamps=True,
        vad_filter=use_vad,
        vad_parameters={"min_silence_duration_ms": 400} if use_vad else None,
    )
    words = []
    seg_list = []
    for seg in segments:
        seg_list.append({"start": round(seg.start, 2), "end": round(seg.end, 2), "text": seg.text.strip()})
        for w in seg.words or []:
            words.append({"text": w.word.strip(), "start": round(w.start, 2), "end": round(w.end, 2)})
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"clip": clip, "model": MODEL_SIZE, "segments": seg_list, "words": words}, f, ensure_ascii=False, indent=1)
    print(f"done: {name} | {len(seg_list)} segments | {time.time()-t0:.0f}s", flush=True)

print("ALL DONE")
