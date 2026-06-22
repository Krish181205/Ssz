#!/usr/bin/env python3
"""Generate app icons for the Pharma-Tech Founder Mentor PWA.

On-theme mark: a two-tone pharmaceutical capsule (teal + violet) on the app's
dark navy background, matching the in-app palette
(#0B1220 / #34E0B8 / #9B8CFF).
"""
import os
import math
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(__file__), "..", "icons")
os.makedirs(OUT, exist_ok=True)

SS = 4  # supersample factor for crisp anti-aliased edges

NAVY_TOP = (11, 18, 32)      # #0B1220
NAVY_BOT = (22, 31, 54)      # slightly lifted navy
TEAL = (52, 224, 184)        # #34E0B8
VIOLET = (155, 140, 255)     # #9B8CFF


def gradient_bg(S):
    img = Image.new("RGBA", (S, S), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)
    for y in range(S):
        t = y / (S - 1)
        r = round(NAVY_TOP[0] + (NAVY_BOT[0] - NAVY_TOP[0]) * t)
        g = round(NAVY_TOP[1] + (NAVY_BOT[1] - NAVY_TOP[1]) * t)
        b = round(NAVY_TOP[2] + (NAVY_BOT[2] - NAVY_TOP[2]) * t)
        d.line([(0, y), (S, y)], fill=(r, g, b, 255))
    # soft diagonal glow behind the capsule
    glow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([S * 0.10, S * 0.18, S * 0.62, S * 0.70],
               fill=(TEAL[0], TEAL[1], TEAL[2], 70))
    gd.ellipse([S * 0.40, S * 0.32, S * 0.92, S * 0.84],
               fill=(VIOLET[0], VIOLET[1], VIOLET[2], 70))
    glow = glow.filter(ImageFilter.GaussianBlur(S * 0.10))
    img.alpha_composite(glow)
    return img


def capsule(S):
    """Build a horizontal two-tone capsule on its own transparent layer."""
    cw, ch = int(S * 0.66), int(S * 0.30)
    rad = ch // 2
    mask = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, cw - 1, ch - 1], radius=rad, fill=255)

    comp = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    half = cw // 2
    comp.paste(TEAL + (255,), (0, 0, half, ch))
    comp.paste(VIOLET + (255,), (half, 0, cw, ch))
    comp.putalpha(mask)

    cd = ImageDraw.Draw(comp)
    # dark seam between the two halves
    seam = max(2, S // 150)
    cd.rectangle([half - seam, 0, half + seam, ch], fill=(11, 18, 32, 235))

    # glossy highlight along the top, clipped to the capsule shape
    hi = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ImageDraw.Draw(hi).rounded_rectangle(
        [int(cw * 0.05), int(ch * 0.14), int(cw * 0.95), int(ch * 0.44)],
        radius=ch // 4, fill=(255, 255, 255, 55))
    hi.putalpha(Image.composite(hi.getchannel("A"), Image.new("L", (cw, ch), 0), mask))
    comp = Image.alpha_composite(comp, hi)

    return comp.rotate(38, expand=True, resample=Image.BICUBIC)


def build(size, squircle=False):
    S = size * SS
    img = gradient_bg(S)
    cap = capsule(S)
    img.alpha_composite(cap, ((S - cap.width) // 2, (S - cap.height) // 2))
    if squircle:
        mask = Image.new("L", (S, S), 0)
        ImageDraw.Draw(mask).rounded_rectangle(
            [0, 0, S - 1, S - 1], radius=int(S * 0.225), fill=255)
        img.putalpha(mask)
    return img.resize((size, size), Image.LANCZOS)


def main():
    # maskable + apple icons are full-bleed (launcher / iOS apply their own mask)
    build(512, squircle=False).save(os.path.join(OUT, "icon-512-maskable.png"))
    build(180, squircle=False).save(os.path.join(OUT, "apple-touch-icon.png"))
    # "any" purpose icons get a rounded squircle with transparent corners
    build(512, squircle=True).save(os.path.join(OUT, "icon-512.png"))
    build(192, squircle=True).save(os.path.join(OUT, "icon-192.png"))
    print("icons written to", os.path.abspath(OUT))


if __name__ == "__main__":
    main()
