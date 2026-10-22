#!/usr/bin/env python3
"""Dramatic shot-to-shot transitions rendered frame-by-frame with Pillow.

ffmpeg's xfade cannot rotate, roll or bounce. This module takes the last N frames
of shot A and the first N frames of shot B (extracted as PNGs) and composites
them with animated affine transforms (scale, rotation, translation, opacity,
blur) driven by easing curves. The result is written as a PNG sequence that
build_video.py encodes into a short transition clip.

Effect signature: effect(a_rgba, b_rgba, p) -> RGBA canvas, with p in [0, 1].
"""

import math
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter
from PIL import ImageDraw as ImageDrawModule

TAU = math.tau
BLACK = (0, 0, 0, 255)


# ---------------------------------------------------------------- easing
def ease_out_cubic(p):
    return 1 - (1 - p) ** 3


def ease_in_cubic(p):
    return p ** 3


def ease_in_out(p):
    return p * p * (3 - 2 * p)


def ease_out_back(p, overshoot=1.70158):
    c3 = overshoot + 1
    return 1 + c3 * (p - 1) ** 3 + overshoot * (p - 1) ** 2


def ease_out_bounce(p):
    n1, d1 = 7.5625, 2.75
    if p < 1 / d1:
        return n1 * p * p
    if p < 2 / d1:
        p -= 1.5 / d1
        return n1 * p * p + 0.75
    if p < 2.5 / d1:
        p -= 2.25 / d1
        return n1 * p * p + 0.9375
    p -= 2.625 / d1
    return n1 * p * p + 0.984375


def ease_out_elastic(p):
    if p in (0, 1):
        return p
    c4 = TAU / 3
    return 2 ** (-10 * p) * math.sin((p * 10 - 0.75) * c4) + 1


def clamp01(x):
    return max(0.0, min(1.0, x))


# ---------------------------------------------------------------- compositing
def new_canvas(size, color=BLACK):
    return Image.new("RGBA", size, color)


def transform(img, scale=1.0, xscale=1.0, angle=0.0, alpha=1.0, blur=0.0,
              hblur=0.0, brightness=1.0, vblur=0.0):
    """Return a transformed RGBA copy of img (rotation expands the bbox)."""
    im = img
    w = max(1, int(round(im.width * scale * xscale)))
    h = max(1, int(round(im.height * scale)))
    if (w, h) != im.size:
        im = im.resize((w, h), Image.BILINEAR)
    if hblur > 1:
        narrow = max(1, int(im.width / hblur))
        im = im.resize((narrow, im.height), Image.BILINEAR).resize((w, h), Image.BILINEAR)
    if vblur > 1:
        short = max(1, int(im.height / vblur))
        im = im.resize((im.width, short), Image.BILINEAR).resize((w, h), Image.BILINEAR)
    if blur > 0.5:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    if brightness != 1.0:
        im = ImageEnhance.Brightness(im).enhance(brightness)
    if angle % 360:
        im = im.rotate(angle, resample=Image.BILINEAR, expand=True)
    if alpha < 1.0:
        a = im.getchannel("A").point(lambda v: int(v * clamp01(alpha)))
        im.putalpha(a)
    return im


def paste_center(canvas, im, dx=0, dy=0):
    x = canvas.width // 2 - im.width // 2 + int(round(dx))
    y = canvas.height // 2 - im.height // 2 + int(round(dy))
    canvas.paste(im, (x, y), im)
    return canvas


# ---------------------------------------------------------------- effects
def fx_spin_in(a, b, p):
    """B spins in from a dot at the centre (two full turns), A recedes."""
    e = ease_out_back(p, 1.2)
    c = new_canvas(a.size)
    paste_center(c, transform(a, scale=1 + 0.12 * p, brightness=1 - 0.6 * p))
    paste_center(c, transform(b, scale=max(0.04, e), angle=720 * (1 - ease_out_cubic(p)),
                              alpha=min(1.0, p * 4)))
    return c


def fx_roll_out_left(a, b, p):
    """A rolls off the left edge like a wheel, revealing B underneath."""
    e = ease_in_cubic(p) * 0.6 + ease_in_out(p) * 0.4
    c = new_canvas(a.size)
    paste_center(c, transform(b, scale=1.10 - 0.10 * ease_out_cubic(p)))
    paste_center(c, transform(a, scale=1 - 0.35 * e, angle=-380 * e),
                 dx=-a.width * 1.35 * e, dy=a.height * 0.15 * e)
    return c


def fx_roll_in_right(a, b, p):
    """B rolls in from the right edge, spinning, and settles with a soft overshoot."""
    e = ease_out_back(p, 0.9)
    c = new_canvas(a.size)
    paste_center(c, transform(a, brightness=1 - 0.55 * p, scale=1 - 0.06 * p))
    paste_center(c, transform(b, scale=0.55 + 0.45 * clamp01(e), angle=360 * (1 - clamp01(e))),
                 dx=a.width * 1.3 * (1 - e))
    return c


def fx_punch_in(a, b, p):
    """B slams in from oversized to full frame with an elastic pulse; A blows out."""
    e = ease_out_elastic(clamp01(p * 1.15))
    c = new_canvas(a.size)
    paste_center(c, transform(a, scale=1 + 0.25 * p, blur=18 * p, alpha=1 - ease_in_cubic(p)))
    paste_center(c, transform(b, scale=1.75 - 0.75 * e, alpha=min(1.0, p * 3)))
    return c


def fx_flip_h(a, b, p):
    """Card flip around the vertical axis: A squeezes to a line, B unfolds."""
    c = new_canvas(a.size)
    if p < 0.5:
        q = ease_in_cubic(p * 2)
        paste_center(c, transform(a, xscale=max(0.02, math.cos(q * math.pi / 2)),
                                  brightness=1 - 0.5 * q))
    else:
        q = ease_out_cubic((p - 0.5) * 2)
        paste_center(c, transform(b, xscale=max(0.02, math.sin(q * math.pi / 2)),
                                  brightness=0.5 + 0.5 * q))
    return c


def fx_shrink_spin_out(a, b, p):
    """A spins and shrinks into the centre and vanishes; B waits behind it."""
    e = ease_in_cubic(p) * 0.7 + p * 0.3
    c = new_canvas(a.size)
    paste_center(c, transform(b, scale=1.08 - 0.08 * ease_out_cubic(p),
                              brightness=0.6 + 0.4 * ease_out_cubic(p)))
    paste_center(c, transform(a, scale=max(0.02, 1 - e), angle=540 * e, alpha=1 - e ** 3))
    return c


def fx_drop_bounce(a, b, p):
    """B drops from the top and bounces into place over a dimming A."""
    e = ease_out_bounce(p)
    c = new_canvas(a.size)
    paste_center(c, transform(a, brightness=1 - 0.6 * p))
    paste_center(c, b, dy=-a.height * (1 - e))
    return c


def fx_whip_left(a, b, p):
    """Whip pan: both frames rush left with motion blur."""
    e = ease_in_out(p)
    speed = math.sin(p * math.pi)
    c = new_canvas(a.size)
    paste_center(c, transform(a, hblur=1 + 40 * speed), dx=-a.width * e)
    paste_center(c, transform(b, hblur=1 + 40 * speed), dx=a.width * (1 - e))
    return c


def fx_zoom_blur_cross(a, b, p):
    """A rushes toward the lens and dissolves in blur; B lands from a blurred zoom."""
    e = ease_in_out(p)
    c = new_canvas(a.size)
    paste_center(c, transform(b, scale=1.45 - 0.45 * ease_out_cubic(p), blur=24 * (1 - e)))
    paste_center(c, transform(a, scale=1 + 0.7 * ease_in_cubic(p), blur=28 * e, alpha=1 - e))
    return c


def fx_pinwheel(a, b, p):
    """A spins away clockwise and shrinks, B spins in counter-clockwise and grows."""
    ea, eb = ease_in_cubic(p), ease_out_cubic(p)
    c = new_canvas(a.size)
    paste_center(c, transform(a, scale=max(0.03, 1 - ea), angle=-300 * ea, alpha=1 - ea))
    paste_center(c, transform(b, scale=max(0.03, eb), angle=300 * (1 - eb), alpha=min(1.0, p * 3)))
    return c


def fx_rise_tilt(a, b, p):
    """B rises from below, slightly tilted, and straightens with a soft overshoot."""
    e = ease_out_back(p, 1.0)
    c = new_canvas(a.size)
    paste_center(c, transform(a, brightness=1 - 0.5 * p, scale=1 - 0.05 * p))
    paste_center(c, transform(b, scale=0.85 + 0.15 * clamp01(e), angle=-14 * (1 - clamp01(e))),
                 dy=a.height * 1.2 * (1 - e))
    return c


def fx_split_reveal(a, b, p):
    """A tears into top/bottom halves that slide apart, revealing B."""
    e = ease_in_cubic(p) * 0.5 + ease_in_out(p) * 0.5
    c = new_canvas(a.size)
    paste_center(c, transform(b, scale=1.10 - 0.10 * ease_out_cubic(p),
                              brightness=0.6 + 0.4 * ease_out_cubic(p)))
    half = a.height // 2
    top = a.crop((0, 0, a.width, half))
    bottom = a.crop((0, half, a.width, a.height))
    c.paste(top, (int(-a.width * e), 0), top)
    c.paste(bottom, (int(a.width * e), half), bottom)
    return c


def fx_rotate_zoom_in(a, b, p):
    """B grows from 0.3x while un-tilting from -25 degrees, with a soft overshoot."""
    e = ease_out_back(p, 1.1)
    c = new_canvas(a.size)
    paste_center(c, transform(a, scale=1 + 0.08 * p, brightness=1 - 0.6 * p, blur=10 * p))
    paste_center(c, transform(b, scale=0.3 + 0.7 * clamp01(e), angle=-25 * (1 - clamp01(e)),
                              alpha=min(1.0, p * 3)))
    return c


def fx_cube_left(a, b, p):
    """Pseudo-3D cube turn: A squeezes out to the left while B unfolds from the right."""
    e = ease_in_out(p)
    c = new_canvas(a.size)
    wa = max(2, int(a.width * (1 - e)))
    wb = max(2, int(b.width * e))
    ia = transform(a, brightness=1 - 0.5 * e).resize((wa, a.height), Image.BILINEAR)
    ib = transform(b, brightness=0.5 + 0.5 * e).resize((wb, b.height), Image.BILINEAR)
    c.paste(ia, (0, 0), ia)
    c.paste(ib, (wa, 0), ib)
    return c


def fx_spin_drop_out(a, b, p):
    """A tumbles down out of frame, spinning, and B is waiting behind it."""
    e = ease_in_cubic(p)
    c = new_canvas(a.size)
    paste_center(c, transform(b, scale=1.06 - 0.06 * ease_out_cubic(p),
                              brightness=0.65 + 0.35 * ease_out_cubic(p)))
    paste_center(c, transform(a, scale=1 - 0.25 * e, angle=-200 * e), dy=a.height * 1.4 * e)
    return c


def fx_iris_open(a, b, p):
    """B is revealed through a growing circle while gently straightening from a tilt."""
    e = ease_out_cubic(p)
    c = new_canvas(a.size)
    paste_center(c, transform(a, brightness=1 - 0.5 * p))
    layer = new_canvas(a.size, (0, 0, 0, 0))
    paste_center(layer, transform(b, scale=1.05 - 0.05 * e, angle=-8 * (1 - e)))
    radius = int(math.hypot(a.width, a.height) / 2 * e) + 1
    mask = Image.new("L", a.size, 0)
    cx, cy = a.width // 2, a.height // 2
    ImageDrawModule.Draw(mask).ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(6))
    c.paste(layer, (0, 0), mask)
    return c


def fx_fadeblack(a, b, p):
    """Classic dip to black."""
    c = new_canvas(a.size)
    if p < 0.5:
        paste_center(c, transform(a, alpha=1 - p * 2))
    else:
        paste_center(c, transform(b, alpha=(p - 0.5) * 2))
    return c


# ---------------------------------------------------------------- fast effects
# Built for fast-paced cuts (0.3-0.4s transitions, 2026-09-23): translation and
# light-based effects that still read at 9-12 frames, where rotations flicker.
SLICES = 8


def fx_whip_right(a, b, p):
    """Whip pan to the right with horizontal motion blur."""
    e = ease_in_out(p)
    speed = math.sin(p * math.pi)
    c = new_canvas(a.size)
    paste_center(c, transform(a, hblur=1 + 40 * speed), dx=a.width * e)
    paste_center(c, transform(b, hblur=1 + 40 * speed), dx=-a.width * (1 - e))
    return c


def fx_whip_up(a, b, p):
    """Whip tilt upward: both frames rush up with vertical motion blur."""
    e = ease_in_out(p)
    speed = math.sin(p * math.pi)
    c = new_canvas(a.size)
    paste_center(c, transform(a, vblur=1 + 40 * speed), dy=-a.height * e)
    paste_center(c, transform(b, vblur=1 + 40 * speed), dy=a.height * (1 - e))
    return c


def fx_push_up(a, b, p):
    """Clean push: B pushes A up and out of frame."""
    e = ease_out_cubic(p)
    c = new_canvas(a.size)
    paste_center(c, a, dy=-a.height * e)
    paste_center(c, b, dy=a.height * (1 - e))
    return c


def fx_push_right(a, b, p):
    """Clean push: B pushes A out to the right."""
    e = ease_out_cubic(p)
    c = new_canvas(a.size)
    paste_center(c, a, dx=a.width * e)
    paste_center(c, b, dx=-a.width * (1 - e))
    return c


def fx_slide_over_down(a, b, p):
    """B slides down over A, which dims underneath."""
    e = ease_out_cubic(p)
    c = new_canvas(a.size)
    paste_center(c, transform(a, brightness=1 - 0.5 * p))
    paste_center(c, b, dy=-a.height * (1 - e))
    return c


def fx_zoom_through(a, b, p):
    """A rushes into the lens and burns out; B settles from a slight zoom."""
    c = new_canvas(a.size)
    paste_center(c, transform(b, scale=1.25 - 0.25 * ease_out_cubic(p)))
    paste_center(c, transform(a, scale=1 + 1.2 * ease_in_cubic(p), blur=18 * p,
                              brightness=1 + 0.8 * p, alpha=1 - ease_in_cubic(p)))
    return c


def fx_flash_white(a, b, p):
    """Camera flash: A blows out to white, B emerges from the white."""
    c = new_canvas(a.size)
    if p < 0.5:
        paste_center(c, transform(a, brightness=1 + 3 * (p * 2)))
    else:
        paste_center(c, transform(b, brightness=1 + 3 * (1 - (p - 0.5) * 2)))
    return c


def fx_slice_in(a, b, p):
    """B arrives in horizontal slices sliding in from alternating sides."""
    c = new_canvas(a.size)
    paste_center(c, transform(a, brightness=1 - 0.4 * p))
    h = a.height // SLICES
    for k in range(SLICES):
        delay = 0.35 * k / (SLICES - 1)
        e = ease_out_cubic(clamp01((p - delay) / (1 - 0.35)))
        side = -1 if k % 2 else 1
        top = k * h
        bottom = a.height if k == SLICES - 1 else top + h
        strip = b.crop((0, top, b.width, bottom))
        c.paste(strip, (int(side * a.width * (1 - e)), top), strip)
    return c


EFFECTS = {
    "spin_in": fx_spin_in,
    "roll_out_left": fx_roll_out_left,
    "roll_in_right": fx_roll_in_right,
    "punch_in": fx_punch_in,
    "flip_h": fx_flip_h,
    "shrink_spin_out": fx_shrink_spin_out,
    "drop_bounce": fx_drop_bounce,
    "whip_left": fx_whip_left,
    "zoom_blur_cross": fx_zoom_blur_cross,
    "pinwheel": fx_pinwheel,
    "rise_tilt": fx_rise_tilt,
    "split_reveal": fx_split_reveal,
    "rotate_zoom_in": fx_rotate_zoom_in,
    "cube_left": fx_cube_left,
    "spin_drop_out": fx_spin_drop_out,
    "iris_open": fx_iris_open,
    "fadeblack": fx_fadeblack,
    "whip_right": fx_whip_right,
    "whip_up": fx_whip_up,
    "push_up": fx_push_up,
    "push_right": fx_push_right,
    "slide_over_down": fx_slide_over_down,
    "zoom_through": fx_zoom_through,
    "flash_white": fx_flash_white,
    "slice_in": fx_slice_in,
}


# ---------------------------------------------------------------- driver
def load_frames(folder):
    return sorted(Path(folder).glob("*.png"))


def render_transition(name, a_dir, b_dir, out_dir):
    """Composite A's tail frames with B's head frames; writes out_dir/NNN.png."""
    fx = EFFECTS[name]
    a_frames, b_frames = load_frames(a_dir), load_frames(b_dir)
    n = min(len(a_frames), len(b_frames))
    if n < 2:
        raise ValueError(f"transition {name}: need >=2 frames, got {n}")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for k in range(n):
        p = k / (n - 1)
        a = Image.open(a_frames[k]).convert("RGBA")
        b = Image.open(b_frames[k]).convert("RGBA")
        fx(a, b, p).convert("RGB").save(out / f"{k:03d}.png", compress_level=1)
    return n
