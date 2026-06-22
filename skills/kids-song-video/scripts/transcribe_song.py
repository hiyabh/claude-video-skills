# -*- coding: utf-8 -*-
"""Transcribe song.mp3 to word/segment timing with faster-whisper.

WHY faster-whisper (not `npx hyperframes transcribe`): on Windows the bundled
whisper.cpp is often missing ("whisper-cpp not found"). faster-whisper is pure
Python (pip install faster-whisper) and just works.

WHAT to trust: only the TIMING. Whisper mishears SINGING (and Hebrew), so the
caption TEXT must come from your known, correct lyrics. Use these segment
start/end times to place each known lyric line. The printed segments let you
map "which segment = which lyric line".

Run:  python transcribe_song.py
Out:  assets/whisper_words.json  + printed segment table
"""
import json, os
from faster_whisper import WhisperModel

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONG = os.path.join(PROJECT, "assets", "song.mp3")
OUT = os.path.join(PROJECT, "assets", "whisper_words.json")

print("loading model (downloads on first run)...")
model = WhisperModel("small", device="cpu", compute_type="int8")

print("transcribing...")
segments, info = model.transcribe(SONG, language="he", word_timestamps=True, vad_filter=False)

words, seg_dump, lines = [], [], []
for seg in segments:
    seg_dump.append({"start": round(seg.start, 2), "end": round(seg.end, 2), "text": seg.text})
    lines.append(f"{seg.start:6.2f} - {seg.end:6.2f}  {seg.text.strip()}")
    for w in (seg.words or []):
        words.append({"word": w.word, "start": round(w.start, 3), "end": round(w.end, 3)})

json.dump({"words": words, "segments": seg_dump}, open(OUT, "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
# also write a readable table (console encoding mangles Hebrew; read the file)
open(os.path.join(PROJECT, "assets", "segments.txt"), "w", encoding="utf-8").write("\n".join(lines))
print(f"\nsaved {len(words)} words → {OUT}")
print("readable segment table → assets/segments.txt  (open it to map lyrics to timing)")
