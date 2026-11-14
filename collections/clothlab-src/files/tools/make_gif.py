#!/usr/bin/env python3
"""Assemble recorded TGA frames (ClothLab --record) into a GIF.

Usage:
    python tools/make_gif.py data/frames_flag report/figures/flag.gif --width 640 --fps 30
"""
import argparse
import glob
import os
import sys

from PIL import Image


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", help="directory containing frame_XXXXX.tga")
    ap.add_argument("out", help="output .gif")
    ap.add_argument("--width", type=int, default=640)
    ap.add_argument("--fps", type=float, default=30.0)
    ap.add_argument("--step", type=int, default=1, help="keep every Nth frame")
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--end", type=int, default=-1)
    ap.add_argument("--keyframes", default="", help="comma separated frame indices to save as PNG")
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(args.src, "frame_*.tga")))
    if not files:
        print("no frames found in", args.src)
        return 1
    if args.end < 0:
        args.end = len(files)

    frames = []
    for idx in range(args.start, min(args.end, len(files)), args.step):
        im = Image.open(files[idx]).convert("RGB")
        if im.width != args.width:
            h = max(1, round(im.height * args.width / im.width))
            im = im.resize((args.width, h), Image.LANCZOS)
        frames.append(im.convert("P", palette=Image.ADAPTIVE, colors=192))

    dur = int(1000.0 * args.step / args.fps)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    frames[0].save(args.out, save_all=True, append_images=frames[1:],
                   duration=dur, loop=0, optimize=True, disposal=2)
    print(f"wrote {args.out}  ({len(frames)} frames, {dur} ms/frame)")

    for kf in [k for k in args.keyframes.split(",") if k.strip()]:
        i = int(kf)
        if 0 <= i < len(files):
            p = os.path.splitext(args.out)[0] + f"_f{i:05d}.png"
            Image.open(files[i]).convert("RGB").save(p)
            print("keyframe", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
