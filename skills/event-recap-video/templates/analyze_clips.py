#!/usr/bin/env python3
"""Listen to the raw clips: transcribe the prayer (Hebrew) with timestamps and
print an RMS-energy profile per half-second, so the strong moments (chanting,
shouting) can be placed deliberately in the cut."""

import os
import subprocess
import sys
from pathlib import Path

import numpy as np

os.chdir(Path(__file__).resolve().parent)
CLIPS = sorted(str(p) for p in Path(".").glob("*.mp4") if not p.name.startswith("01 - "))
SR = 16000
WINDOW_SEC = 0.5


def load_pcm(path):
    raw = subprocess.check_output([
        "ffmpeg", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", str(SR),
        "-f", "s16le", "-"])
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0


def energy_profile(y):
    n = int(SR * WINDOW_SEC)
    rows = []
    for i in range(0, len(y) - n, n):
        seg = y[i:i + n]
        rms = float(np.sqrt(np.mean(seg ** 2)) + 1e-9)
        rows.append((i / SR, 20 * np.log10(rms)))
    return rows


def transcribe(path):
    from faster_whisper import WhisperModel
    model = WhisperModel("small", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(path, language="he", word_timestamps=True,
                                   vad_filter=False, beam_size=5)
    return list(segments)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    for clip in CLIPS:
        print(f"\n===== {clip}")
        y = load_pcm(clip)
        prof = energy_profile(y)
        peak = max(v for _, v in prof)
        print("energy (dB RMS per 0.5s, * = within 3dB of peak):")
        line = []
        for t, v in prof:
            mark = "*" if v >= peak - 3 else " "
            line.append(f"{t:4.1f}:{v:5.1f}{mark}")
        for i in range(0, len(line), 6):
            print("  " + " | ".join(line[i:i + 6]))
        print("transcript:")
        for seg in transcribe(clip):
            print(f"  [{seg.start:5.1f} - {seg.end:5.1f}] {seg.text.strip()}")


if __name__ == "__main__":
    main()
