#!/usr/bin/env python3
"""Build the report figures from data/bench.csv (pure Pillow, no matplotlib)."""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plots import Chart, bar_chart

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(ROOT, "data", "bench.csv")
OUT = os.path.join(ROOT, "report", "figures")


def load():
    rows = []
    with open(CSV, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            for k in ("substeps", "iters", "frames", "diverged"):
                r[k] = int(r[k])
            for k in ("k", "friction", "ms_per_frame", "max_stretch", "mean_stretch",
                      "pen_mm", "contacts", "kinetic", "overhang"):
                r[k] = float(r[k])
            rows.append(r)
    return rows


def by_exp(rows, exp):
    return [r for r in rows if r["exp"] == exp]


def fig_e1(rows):
    d = by_exp(rows, "E1_stability")
    pbd = sorted([r for r in d if r["solver"] == "pbd"], key=lambda r: r["substeps"])
    eul = sorted([r for r in d if r["solver"] == "euler"], key=lambda r: r["substeps"])
    c = Chart("最大拉伸率随子步数的变化（旗帜场景）", "每帧子步数", "最大边长拉伸率  max(|L|/L0)")
    c.add("PBD (6 次迭代)", [r["substeps"] for r in pbd], [r["max_stretch"] for r in pbd])
    stable = [r for r in eul if not r["diverged"]]
    c.add("显式欧拉", [r["substeps"] for r in stable], [r["max_stretch"] for r in stable])
    c.caption("注：显式欧拉在 2~8 子步时数值发散，图中未画出；PBD 在 6 子步时已接近刚性。")
    c.save(os.path.join(OUT, "fig_e1_stability.png"))


def fig_e2(rows):
    d = sorted(by_exp(rows, "E2_iterations"), key=lambda r: r["iters"])
    c = Chart("约束迭代次数对布料刚度的影响", "PBD 迭代次数", "最大边长拉伸率")
    c.add("最大拉伸率", [r["iters"] for r in d], [r["max_stretch"] for r in d])
    c.save(os.path.join(OUT, "fig_e2a_iterations.png"))

    c = Chart("约束迭代次数与单帧物理耗时", "PBD 迭代次数", "物理耗时 (ms/帧)")
    c.add("耗时", [r["iters"] for r in d], [r["ms_per_frame"] for r in d])
    c.save(os.path.join(OUT, "fig_e2b_iter_time.png"))


def fig_e3(rows):
    d = sorted(by_exp(rows, "E3_substeps_pen"), key=lambda r: r["substeps"])
    c = Chart("子步数与最大穿透深度（球体覆盖场景）", "每帧子步数", "最大穿透深度 (mm)")
    c.add("最大穿透", [r["substeps"] for r in d], [r["pen_mm"] for r in d])
    c.save(os.path.join(OUT, "fig_e3_penetration.png"))


def fig_e4(rows):
    d = sorted(by_exp(rows, "E4_friction"), key=lambda r: r["friction"])
    c = Chart("摩擦系数与布料下滑距离（30° 斜面）", "摩擦系数 μ", "3 秒内沿斜面平均位移 (m)")
    c.add("下滑距离", [r["friction"] for r in d], [r["overhang"] for r in d])
    c.save(os.path.join(OUT, "fig_e4_friction.png"))


def fig_e5(rows):
    d = sorted(by_exp(rows, "E5_resolution"), key=lambda r: r["label"])
    n = [int(r["label"][1:]) for r in d]
    c = Chart("网格分辨率与单帧物理耗时", "网格边长（N×N）", "物理耗时 (ms/帧)", logx=False)
    c.add("耗时", n, [r["ms_per_frame"] for r in d])
    c.save(os.path.join(OUT, "fig_e5_resolution.png"))


def fig_e6(rows):
    d = by_exp(rows, "E6_scenes")
    names = {"flag": "旗帜", "drape": "盖球", "table": "桌布", "spheres": "双球", "tear": "撕裂"}
    c = Chart("各场景在默认参数下的单帧物理耗时", "场景", "物理耗时 (ms/帧)")
    c.add("耗时", list(range(len(d))), [r["ms_per_frame"] for r in d])
    c.save(os.path.join(OUT, "fig_e6_scenes.png"))


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = load()
    fig_e1(rows)
    fig_e2(rows)
    fig_e3(rows)
    fig_e4(rows)
    fig_e5(rows)
    fig_e6(rows)


if __name__ == "__main__":
    main()


