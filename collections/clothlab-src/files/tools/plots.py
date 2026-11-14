#!/usr/bin/env python3
"""Tiny Pillow based plotting helpers (no matplotlib needed).

Only what the report needs: multi-series line charts and bar charts with
Chinese labels, grid, ticks and a legend.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

FONT_PATH = r"C:\Windows\Fonts\msyh.ttc"
W, H = 1240, 760
ML, MR, MT, MB = 110, 40, 72, 96

BG = (255, 255, 255)
GRID = (226, 230, 236)
AXIS = (70, 78, 90)
TEXT = (30, 34, 40)
PALETTE = [(214, 69, 65), (46, 110, 180), (60, 150, 90), (200, 140, 40),
           (130, 80, 170), (30, 150, 160)]


def _font(size):
    return ImageFont.truetype(FONT_PATH, size)


def _nice_step(span, target=6):
    if span <= 0:
        return 1.0
    raw = span / target
    mag = 10 ** math.floor(math.log10(raw))
    for m in (1, 2, 2.5, 5, 10):
        if raw <= m * mag:
            return m * mag
    return 10 * mag


def _ticks(lo, hi, target=6):
    step = _nice_step(hi - lo, target)
    start = math.floor(lo / step) * step
    vals = []
    v = start
    while v <= hi + 1e-9:
        if v >= lo - 1e-9:
            vals.append(round(v, 10))
        v += step
    return vals


def _fmt(v, step):
    if abs(v) >= 1000:
        return f"{v:,.0f}"
    if step >= 1:
        return f"{v:.0f}"
    if step >= 0.1:
        return f"{v:.1f}"
    if step >= 0.01:
        return f"{v:.2f}"
    return f"{v:.3f}"


class Chart:
    def __init__(self, title="", xlabel="", ylabel="", logx=False, logy=False):
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.logx = logx
        self.logy = logy
        self.series = []
        self.notes = []
        self.caption_text = ""
        self.xmin = self.xmax = self.ymin = self.ymax = None

    def add(self, label, xs, ys, color=None, marker="o", dashed=False, width=3):
        self.series.append(dict(label=label, xs=list(xs), ys=list(ys),
                                color=color if color else PALETTE[len(self.series) % len(PALETTE)],
                                marker=marker, dashed=dashed, width=width))
        return self

    def note(self, text, x=0.02, y=0.95):
        self.notes.append((text, x, y))

    def caption(self, text):
        self.caption_text = text
        return self

    def limits(self, xmin=None, xmax=None, ymin=None, ymax=None):
        self.xmin, self.xmax, self.ymin, self.ymax = xmin, xmax, ymin, ymax
        return self

    def save(self, path):
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        f_title = _font(30)
        f_lab = _font(21)
        f_tick = _font(18)
        f_leg = _font(19)

        pw, ph = W - ML - MR, H - MT - MB
        xs = [x for s in self.series for x in s["xs"]]
        ys = [y for s in self.series for y in s["ys"] if y is not None]
        xmin = self.xmin if self.xmin is not None else min(xs)
        xmax = self.xmax if self.xmax is not None else max(xs)
        ymin = self.ymin if self.ymin is not None else min(ys)
        ymax = self.ymax if self.ymax is not None else max(ys)
        if ymin == ymax:
            ymin, ymax = ymin - 1, ymax + 1
        pad = (ymax - ymin) * 0.08
        ymin -= pad
        ymax += pad
        if ymin > 0 and ymin < (ymax - ymin):
            ymin = 0 if self.ymin is None else ymin

        def X(v):
            if self.logx:
                a, b = math.log10(xmin), math.log10(xmax)
                return ML + (math.log10(v) - a) / (b - a) * pw
            return ML + (v - xmin) / (xmax - xmin) * pw

        def Y(v):
            if self.logy:
                a, b = math.log10(ymin), math.log10(ymax)
                return MT + ph - (math.log10(v) - a) / (b - a) * ph
            return MT + ph - (v - ymin) / (ymax - ymin) * ph

        # grid + ticks
        if self.logx:
            xt = [10 ** e for e in range(int(math.floor(math.log10(xmin))),
                                         int(math.ceil(math.log10(xmax))) + 1)]
            xstep = 1
        else:
            xt = _ticks(xmin, xmax, 7)
            xstep = xt[1] - xt[0] if len(xt) > 1 else 1
        yt = _ticks(ymin, ymax, 7)
        ystep = yt[1] - yt[0] if len(yt) > 1 else 1

        for v in yt:
            y = Y(v)
            d.line([(ML, y), (ML + pw, y)], fill=GRID, width=1)
            s = _fmt(v, ystep)
            tw = d.textlength(s, font=f_tick)
            d.text((ML - 12 - tw, y - 10), s, font=f_tick, fill=TEXT)
        for v in xt:
            x = X(v)
            d.line([(x, MT), (x, MT + ph)], fill=GRID, width=1)
            s = _fmt(v, xstep)
            tw = d.textlength(s, font=f_tick)
            d.text((x - tw / 2, MT + ph + 10), s, font=f_tick, fill=TEXT)

        # frame
        d.rectangle([ML, MT, ML + pw, MT + ph], outline=AXIS, width=2)

        # series
        for s in self.series:
            pts = [(X(x), Y(y)) for x, y in zip(s["xs"], s["ys"]) if y is not None]
            for i in range(len(pts) - 1):
                if s["dashed"]:
                    x0, y0 = pts[i]
                    x1, y1 = pts[i + 1]
                    n = max(1, int(math.hypot(x1 - x0, y1 - y0) / 9))
                    for k in range(n):
                        if k % 2:
                            continue
                        a = k / n
                        b = (k + 1) / n
                        d.line([(x0 + (x1 - x0) * a, y0 + (y1 - y0) * a),
                                (x0 + (x1 - x0) * b, y0 + (y1 - y0) * b)],
                               fill=s["color"], width=s["width"])
                else:
                    d.line([pts[i], pts[i + 1]], fill=s["color"], width=s["width"])
            for (x, y) in pts:
                r = 5
                if s["marker"] == "x":
                    d.line([(x - r, y - r), (x + r, y + r)], fill=s["color"], width=3)
                    d.line([(x - r, y + r), (x + r, y - r)], fill=s["color"], width=3)
                else:
                    d.ellipse([x - r, y - r, x + r, y + r], fill=s["color"],
                              outline=(255, 255, 255), width=1)

        # title / labels
        tw = d.textlength(self.title, font=f_title)
        d.text(((W - tw) / 2, 20), self.title, font=f_title, fill=TEXT)
        tw = d.textlength(self.xlabel, font=f_lab)
        d.text((ML + pw / 2 - tw / 2, H - 46), self.xlabel, font=f_lab, fill=TEXT)
        if self.ylabel:
            tmp = Image.new("RGBA", (400, 40), (0, 0, 0, 0))
            td = ImageDraw.Draw(tmp)
            td.text((0, 0), self.ylabel, font=f_lab, fill=TEXT)
            rot = tmp.crop((0, 0, int(td.textlength(self.ylabel, font=f_lab)) + 6, 34)).rotate(90, expand=True)
            img.paste(rot, (14, MT + ph // 2 - rot.height // 2), rot)

        # legend
        lx, ly = ML + 18, MT + 14
        for s in self.series:
            d.line([(lx, ly + 10), (lx + 34, ly + 10)], fill=s["color"], width=3)
            d.ellipse([lx + 13, ly + 5, lx + 23, ly + 15], fill=s["color"])
            d.text((lx + 44, ly), s["label"], font=f_leg, fill=TEXT)
            ly += 28

        if self.caption_text:
            d.text((ML, H - 24), self.caption_text, font=_font(17), fill=(110, 116, 126))

        for (t, rx, ry) in self.notes:
            d.text((ML + pw * rx, MT + ph * ry), t, font=f_leg, fill=(120, 60, 60))

        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        img.save(path)
        print("wrote", path)


def bar_chart(path, title, ylabel, categories, values, colors=None, fmt="{:.1f}"):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    f_title, f_lab, f_tick = _font(30), _font(21), _font(18)
    pw, ph = W - ML - MR, H - MT - MB
    ymax = max(values) * 1.15 if max(values) > 0 else 1
    yt = _ticks(0, ymax, 6)
    ystep = yt[1] - yt[0] if len(yt) > 1 else 1

    def Y(v):
        return MT + ph - v / ymax * ph

    for v in yt:
        y = Y(v)
        d.line([(ML, y), (ML + pw, y)], fill=GRID, width=1)
        s = _fmt(v, ystep)
        tw = d.textlength(s, font=f_tick)
        d.text((ML - 12 - tw, y - 10), s, font=f_tick, fill=TEXT)
    d.rectangle([ML, MT, ML + pw, MT + ph], outline=AXIS, width=2)

    n = len(categories)
    slot = pw / max(1, n)
    for i, (c, v) in enumerate(zip(categories, values)):
        x0 = ML + slot * i + slot * 0.22
        x1 = ML + slot * (i + 1) - slot * 0.22
        col = (colors[i] if colors else PALETTE[i % len(PALETTE)])
        d.rectangle([x0, Y(v), x1, MT + ph], fill=col)
        s = fmt.format(v)
        tw = d.textlength(s, font=f_tick)
        d.text(((x0 + x1) / 2 - tw / 2, Y(v) - 26), s, font=f_tick, fill=TEXT)
        tw = d.textlength(c, font=f_tick)
        d.text(((x0 + x1) / 2 - tw / 2, MT + ph + 12), c, font=f_tick, fill=TEXT)

    tw = d.textlength(title, font=f_title)
    d.text(((W - tw) / 2, 20), title, font=f_title, fill=TEXT)
    tmp = Image.new("RGBA", (400, 40), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    td.text((0, 0), ylabel, font=f_lab, fill=TEXT)
    rot = tmp.crop((0, 0, int(td.textlength(ylabel, font=f_lab)) + 6, 34)).rotate(90, expand=True)
    img.paste(rot, (14, MT + ph // 2 - rot.height // 2), rot)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    img.save(path)
    print("wrote", path)


