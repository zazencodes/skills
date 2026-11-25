#!/usr/bin/env python3
"""Check that the accent colours of one diagram can be told apart and seen.

Usage:
    python3 check_palette.py --bg "#1b2023" --surface "#262c2f" "#C6AEFF" "#FFA557"

Each accent must:
  - reach WCAG contrast >= 3:1 against the page and the box surface
    (WCAG 1.4.11, non-text graphics), and
  - have OKLCH chroma >= 0.10, so it reads as a colour and not as grey.
Every pair of accents must:
  - differ by OKLab delta E (x100) >= 15 under normal vision, and
  - differ by >= 8 under simulated protanopia and deuteranopia
    (Machado, Oliveira & Fernandes 2009, severity 1.0). 6 to 8 is a WARN,
    acceptable only because every diagram element carries a text label.
Tritanopia is reported for information.

Exits 1 if any check FAILs.
"""

import argparse
import itertools
import math
import re
import sys

CONTRAST_MIN = 3.0
CHROMA_MIN = 0.10
NORMAL_MIN = 15.0
CVD_TARGET = 8.0
CVD_FLOOR = 6.0

# Machado, Oliveira & Fernandes (2009), severity 1.0, applied in linear sRGB.
CVD = {
    "protan": ((0.152286, 1.052583, -0.204868),
               (0.114503, 0.786281, 0.099216),
               (-0.003882, -0.048116, 1.051998)),
    "deutan": ((0.367322, 0.860646, -0.227968),
               (0.280085, 0.672501, 0.047413),
               (-0.011820, 0.042940, 0.968881)),
    "tritan": ((1.255528, -0.076749, -0.178779),
               (-0.078411, 0.930809, 0.147602),
               (0.004733, 0.691367, 0.303900)),
}


def parse_hex(value):
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
        sys.exit(f"Not a #rrggbb colour: {value}")
    return value.upper()


def linear_rgb(hex_colour):
    channels = [int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]


def luminance(hex_colour):
    r, g, b = linear_rgb(hex_colour)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def oklab(rgb):
    # Björn Ottosson's OKLab, from linear sRGB.
    r, g, b = (min(1.0, max(0.0, c)) for c in rgb)
    l = math.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b)
    m = math.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b)
    s = math.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b)
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)


def simulate(rgb, kind):
    return [sum(row[i] * rgb[i] for i in range(3)) for row in CVD[kind]]


def delta_e(a, b, kind=None):
    ra, rb = linear_rgb(a), linear_rgb(b)
    if kind:
        ra, rb = simulate(ra, kind), simulate(rb, kind)
    return 100 * math.dist(oklab(ra), oklab(rb))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--bg", required=True, help="page background, #rrggbb")
    parser.add_argument("--surface", required=True, help="box surface, #rrggbb")
    parser.add_argument("accents", nargs="+", help="accent colours used in the diagram, #rrggbb")
    args = parser.parse_args()

    bg, surface = parse_hex(args.bg), parse_hex(args.surface)
    accents = [parse_hex(a) for a in args.accents]
    failed = False

    print("Accent     vs bg   vs surface  chroma  result")
    for a in accents:
        c_bg, c_surface = contrast(a, bg), contrast(a, surface)
        _, oa, ob = oklab(linear_rgb(a))
        chroma = math.hypot(oa, ob)
        ok = min(c_bg, c_surface) >= CONTRAST_MIN and chroma >= CHROMA_MIN
        failed |= not ok
        print(f"{a}  {c_bg:5.2f}:1  {c_surface:7.2f}:1  {chroma:6.3f}  {'PASS' if ok else 'FAIL'}")

    if len(accents) > 1:
        print("\nPair                normal  protan  deutan  tritan  result")
        for a, b in itertools.combinations(accents, 2):
            normal = delta_e(a, b)
            protan, deutan, tritan = (delta_e(a, b, k) for k in ("protan", "deutan", "tritan"))
            cvd = min(protan, deutan)
            if normal < NORMAL_MIN or cvd < CVD_FLOOR:
                result = "FAIL"
                failed = True
            elif cvd < CVD_TARGET:
                result = "WARN (label every accent)"
            else:
                result = "PASS"
            print(f"{a}+{b}  {normal:6.1f}  {protan:6.1f}  {deutan:6.1f}  {tritan:6.1f}  {result}")

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
