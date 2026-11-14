#!/usr/bin/env python3
"""Compose several frames into one labelled horizontal strip (for the report)."""
import argparse
import os

from PIL import Image, ImageDraw, ImageFont

FONT = r"C:\Windows\Fonts\msyh.ttc"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--labels", default="")
    ap.add_argument("--width", type=int, default=420)
    ap.add_argument("--gap", type=int, default=10)
    ap.add_argument("--crop", type=float, default=1.0, help="centered crop fraction")
    ap.add_argument("images", nargs="+")
    args = ap.parse_args()

    labels = args.labels.split("|") if args.labels else ["" for _ in args.images]
    thumbs = []
    for p in args.images:
        im = Image.open(p).convert("RGB")
        if args.crop < 1.0:
            cw = int(im.width * args.crop)
            ch = int(im.height * args.crop)
            x0 = (im.width - cw) // 2
            y0 = (im.height - ch) // 2
            im = im.crop((x0, y0, x0 + cw, y0 + ch))
        h = round(im.height * args.width / im.width)
        thumbs.append(im.resize((args.width, h), Image.LANCZOS))
    h = thumbs[0].height
    band = 34 if any(labels) else 0
    W = len(thumbs) * args.width + (len(thumbs) - 1) * args.gap
    H = h + band
    canvas = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(canvas)
    f = ImageFont.truetype(FONT, 22)
    x = 0
    for im, lab in zip(thumbs, labels):
        canvas.paste(im, (x, band))
        if lab:
            tw = d.textlength(lab, font=f)
            d.text((x + (args.width - tw) / 2, 4), lab, font=f, fill=(30, 34, 40))
        x += args.width + args.gap
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    canvas.save(args.out)
    print("wrote", args.out, canvas.size)


if __name__ == "__main__":
    main()

