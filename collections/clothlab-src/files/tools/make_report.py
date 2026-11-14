#!/usr/bin/env python3
"""Build the experiment report (.docx) from data/bench.csv and report/figures."""
import csv
import os
import sys

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Cm, Pt, RGBColor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "report", "figures")
OUT = os.path.join(ROOT, "report", "布料动画实验报告.docx")

BODY_FONT = "宋体"
HEAD_FONT = "黑体"
MONO_FONT = "Consolas"


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def set_run_font(run, name, size=None, bold=None, color=None):
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if color is not None:
        run.font.color.rgb = color


def para(doc, text, size=10.5, first_indent=True, align=None, space_after=6,
         font=BODY_FONT, bold=False, color=None):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.line_spacing = 1.35
    pf.space_after = Pt(space_after)
    if first_indent:
        pf.first_line_indent = Pt(size * 2)
    if align is not None:
        p.alignment = align
    run = p.add_run(text)
    set_run_font(run, font, size, bold, color)
    return p


def heading(doc, text, level=1):
    sizes = {1: 15, 2: 13, 3: 11.5}
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(14 if level == 1 else 10)
    pf.space_after = Pt(8 if level == 1 else 6)
    pf.keep_with_next = True
    run = p.add_run(text)
    set_run_font(run, HEAD_FONT, sizes.get(level, 11), True)
    return p


def caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(10)
    run = p.add_run(text)
    set_run_font(run, BODY_FONT, 9, False, RGBColor(0x44, 0x4A, 0x52))


def figure(doc, name, cap, width_cm=15.0):
    path = os.path.join(FIG, name)
    if not os.path.exists(path):
        print("missing figure:", path)
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(0)
    p.add_run().add_picture(path, width=Cm(width_cm))
    caption(doc, cap)


def table(doc, header, rows, cap=None, widths=None, font_size=9):
    if cap:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(3)
        run = p.add_run(cap)
        set_run_font(run, BODY_FONT, 9, True)
        p.paragraph_format.keep_with_next = True
    t = doc.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t.rows[0].cells
    for i, h in enumerate(header):
        hdr[i].text = ""
        p = hdr[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(h)
        set_run_font(run, HEAD_FONT, font_size, True)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(str(v))
            set_run_font(run, BODY_FONT, font_size)
    if widths:
        t.autofit = False
        for i, w in enumerate(widths):
            t.columns[i].width = Cm(w)
        for r in t.rows:
            for i, w in enumerate(widths):
                r.cells[i].width = Cm(w)
    for ri, r in enumerate(t.rows):
        trPr = r._tr.get_or_add_trPr()
        trPr.append(OxmlElement("w:cantSplit"))
        if ri < len(t.rows) - 1:
            for cell in r.cells:
                for pp in cell.paragraphs:
                    pp.paragraph_format.keep_with_next = True
    # spacing after table
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def code_block(doc, text, size=8.5):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.left_indent = Cm(0.6)
    pf.line_spacing = 1.05
    pf.space_before = Pt(4)
    pf.space_after = Pt(6)
    run = p.add_run(text)
    set_run_font(run, MONO_FONT, size)


# --------------------------------------------------------------------------- #
# data
# --------------------------------------------------------------------------- #
def load_bench():
    rows = []
    with open(os.path.join(ROOT, "data", "bench.csv"), newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            r["substeps"] = int(r["substeps"])
            r["iters"] = int(r["iters"])
            r["diverged"] = int(r["diverged"])
            for k in ("ms_per_frame", "max_stretch", "mean_stretch", "pen_mm", "overhang", "friction", "k", "contacts", "kinetic"):
                r[k] = float(r[k])
            rows.append(r)
    return rows


def exp_rows(rows, exp):
    return [r for r in rows if r["exp"] == exp]


# --------------------------------------------------------------------------- #
# document
# --------------------------------------------------------------------------- #
def build():
    rows = load_bench()
    doc = Document()

    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.top_margin = Cm(2.4)
    sec.bottom_margin = Cm(2.2)
    sec.left_margin = Cm(2.6)
    sec.right_margin = Cm(2.4)

    style = doc.styles["Normal"]
    style.font.name = BODY_FONT
    style.font.size = Pt(10.5)
    style.element.rPr.rFonts.set(qn("w:eastAsia"), BODY_FONT)

    # ---------------------------- cover ---------------------------- #
    for _ in range(3):
        doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("计算机动画  课程实验报告")
    set_run_font(run, HEAD_FONT, 26, True)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(24)
    run = p.add_run("基于质点-弹簧模型的布料动画与碰撞响应")
    set_run_font(run, HEAD_FONT, 20, True)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("——实时仿真、交互与定量分析")
    set_run_font(run, BODY_FONT, 14, False)

    for _ in range(3):
        doc.add_paragraph()

    fields = [("课程名称", "计算机动画"), ("实验类型", "综合"),
              ("实验项目", "布料动画与碰撞检测"), ("学生姓名", ""),
              ("学    号", ""), ("专    业", ""),
              ("同组学生", "无"), ("指导老师", ""),
              ("实验地点", ""), ("实验日期", "")]
    t = doc.add_table(rows=0, cols=2)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for k, v in fields:
        cells = t.add_row().cells
        pr = cells[0].paragraphs[0]
        pr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r = pr.add_run(k + "：")
        set_run_font(r, BODY_FONT, 12)
        pv = cells[1].paragraphs[0]
        r = pv.add_run(v if v else "________________")
        set_run_font(r, BODY_FONT, 12)
        cells[0].width = Cm(4.2)
        cells[1].width = Cm(8.0)

    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    # ---------------------------- 1 ---------------------------- #
    heading(doc, "一、实验目的和要求", 1)
    heading(doc, "1.1 实验目的", 2)
    para(doc, "本实验以布料为对象，完整实现一个三维布料动画系统，并对其数值行为进行定量分析。"
              "具体目标如下：")
    for s in [
        "（1）掌握基于质点-弹簧（Mass-Spring）模型的布料几何表示与受力建模，理解结构弹簧、"
        "剪切弹簧与弯曲弹簧各自对拉伸、剪切和弯曲行为的贡献；",
        "（2）实现两类数值求解器——显式半隐式欧拉积分，以及 Verlet 积分加约束投影"
        "（Position Based Dynamics，PBD），并从稳定性、刚度表现和计算代价三方面进行对比；",
        "（3）实现布料与球体、平面和轴对齐盒体之间的碰撞检测与响应，引入摩擦，使布料能够自然地"
        "覆盖、垂坠、堆积和滑移；",
        "（4）实现三维实时渲染、轨道相机、鼠标拖拽布料、参数调节与离线序列帧录制，形成可交互演示的完整程序；",
        "（5）设计并完成 6 组定量实验，用数据说明刚度、迭代次数、子步数、摩擦系数和网格规模对"
        "稳定性、穿透与性能的影响，而不是只给出“看起来像”的截图。",
    ]:
        para(doc, s)

    heading(doc, "1.2 实验要求", 2)
    for s in [
        "（1）三维、实时：在 1280×800 窗口下默认场景不低于 30 FPS，交互无卡顿；",
        "（2）演示场景不少于 5 个，覆盖旗帜飘动、覆盖球体、桌布、双球覆盖、布料撕裂和斜面摩擦；",
        "（3）程序不依赖任何第三方图形库，只需系统自带的 OpenGL 与 GDI，可在 Windows 上一键编译、直接运行；",
        "（4）所有实验数据、曲线与截图均可由脚本从原始数据重新生成；",
        "（5）报告包含原理推导、关键代码、实验数据与结果分析。",
    ]:
        para(doc, s)

    # ---------------------------- 2 ---------------------------- #
    heading(doc, "二、实验内容和原理", 1)
    heading(doc, "2.1 系统总体结构", 2)
    para(doc, "程序用 C++17 编写，按功能划分为若干模块，模块之间只通过数据结构通信，便于单独测试与替换。"
              "整体数据流为：输入事件 → 参数 → 物理求解 → 几何（位置、法线）→ 渲染 → 帧缓冲 → 截图或序列帧。")
    table(doc,
          ["模块", "文件", "职责"],
          [["应用与交互", "main.cpp", "Win32 窗口、消息循环、固定步长主循环、相机与鼠标交互、HUD 面板、录制"],
           ["布料求解", "cloth.cpp/.h", "质点-弹簧网格、两类积分器、约束投影、风场、撕裂、统计量"],
           ["碰撞", "collision.h", "球体、平面、轴对齐盒体的解析检测与位置修正"],
           ["场景", "scene.cpp/.h", "网格尺寸、固定点、碰撞体、风场与相机预设"],
           ["渲染", "renderer.cpp/.h", "固定管线光照、程序化纹理、阴影投影、雾、线框叠加"],
           ["文字", "hud.cpp/.h", "用 GDI 生成字形图集，再以 OpenGL 纹理绘制 HUD"],
           ["导出", "capture.cpp/.h", "读取帧缓冲并写出 TGA"],
           ["实验", "bench.cpp/.h", "无窗口批量参数扫描，输出 CSV"]],
          cap="表 2-1  程序模块划分", widths=[3.2, 4.6, 8.2])

    heading(doc, "2.2 布料几何与质点-弹簧模型", 2)
    para(doc, "布料被离散为 N×M 的规则质点网格，第 (i, j) 个质点的位置记为 x(i,j)，质量为 m，"
              "相邻质点在静止状态下的间距为 h。网格中的三角形面片只用于渲染和风场计算，"
              "力学行为完全由质点之间的弹簧决定。")
    para(doc, "弹簧按连接方式分为三类：结构弹簧连接上下左右相邻质点，抵抗面内拉伸；"
              "剪切弹簧连接两个对角质点，抵抗面内剪切；弯曲弹簧隔一个质点连接，"
              "以较弱的刚度抵抗弯曲，使布料产生自然的褶皱而不是像纸板一样挺直。")
    para(doc, "对任意一根弹簧 (a, b)，其当前长度为 L = |x_a − x_b|，静止长度为 L0，单位方向为 "
              "d = (x_a − x_b)/L。弹簧对两端质点的作用力为：")
    para(doc, "F = −[ k (L − L0) + c (v_a − v_b)·d ] d", first_indent=False,
         align=WD_ALIGN_PARAGRAPH.CENTER)
    para(doc, "其中 k 为弹簧刚度，c 为阻尼系数，v 为质点速度。第一项是胡克弹力，第二项是沿弹簧方向的"
              "相对速度阻尼，用于抑制高频振荡。每个质点还受到重力 g 与风场产生的气动力 F_wind，"
              "运动方程为 m·a = ΣF + m·g + F_wind。")

    heading(doc, "2.3 数值积分：半隐式欧拉与 Verlet", 2)
    para(doc, "显式求解器采用半隐式（辛）欧拉积分：先更新速度，再用新速度更新位置。")
    para(doc, "v(t+Δt) = v(t) + a(t)·Δt ,    x(t+Δt) = x(t) + v(t+Δt)·Δt", first_indent=False,
         align=WD_ALIGN_PARAGRAPH.CENTER)
    para(doc, "半隐式欧拉对线性弹簧系统是条件稳定的，稳定条件约为 Δt < 2/ω，其中 ω = √(k/m) 是"
              "系统最高模态的角频率。弹簧越硬，允许的时间步越小；一旦超限，系统能量会被人为放大，"
              "表现为布料“炸开”。这一性质正是实验 E1 要定量刻画的对象。")
    para(doc, "约束求解器采用 Verlet 积分：位置由前两帧位置直接递推，速度隐含在位置差中，"
              "因而无需显式存储速度。")
    para(doc, "x(t+Δt) = 2x(t) − x(t−Δt) + a(t)·Δt²", first_indent=False,
         align=WD_ALIGN_PARAGRAPH.CENTER)
    para(doc, "Verlet 积分与约束投影天然契合：位置修正后，速度会自动随之改变，不需要额外的一致性处理。")

    heading(doc, "2.4 约束投影（PBD）", 2)
    para(doc, "PBD 把每根弹簧看作一个距离约束 C = |x_a − x_b| − L0 = 0，在每一个子步内用 Gauss-Seidel"
              "方式迭代求解。设质点的逆质量为 w = 1/m（固定点 w = 0），则一次投影为：")
    para(doc, "Δx_a = −(w_a / (w_a + w_b)) · k′ · C · d ,    Δx_b = +(w_b / (w_a + w_b)) · k′ · C · d",
         first_indent=False, align=WD_ALIGN_PARAGRAPH.CENTER)
    para(doc, "其中 d 为从 b 指向 a 的单位向量，k′ 为本次迭代的等效刚度。若用户给定的归一化刚度为 k，"
              "迭代 n 次，则每次迭代取 k′ = 1 − (1 − k)^(1/n)，从而保证 n 次迭代后的总效果接近 k。"
              "k = 1 时约束在数值上被完全满足，布料接近刚性；k 越小布料越软。")
    para(doc, "与显式积分相比，PBD 的稳定性不依赖于弹簧刚度：只要位置约束的修正量不超过几何尺度，"
              "迭代过程就不会发散。代价是刚度依赖于迭代次数，且投影过程会引入一定的人工阻尼。")

    heading(doc, "2.5 碰撞检测与响应", 2)
    para(doc, "程序中实现了三类解析碰撞体，它们都不需要空间加速结构，单次检测为 O(1)：")
    for s in [
        "（1）球体：若 |x − c| < r + t（t 为布料厚度），则把质点沿径向投影到球面外侧，"
        "穿透深度为 r + t − |x − c|；",
        "（2）平面：若 n·x < d + t，则把质点沿法向平移到平面上，穿透深度为 d + t − n·x；",
        "（3）轴对齐盒体：把质点变换到盒体局部坐标，若三轴同时位于半长之内，则沿穿透最小的轴推出，"
        "保证每次只修正一个方向，避免角点处的抖动。",
    ]:
        para(doc, s)
    para(doc, "碰撞响应分为两步。第一步是位置投影，把质点推回可行域；第二步是摩擦处理：把本次子步的"
              "位移分解为法向与切向，法向分量置零，切向分量乘以 (1 − μ)，从而同时实现“不穿透”和"
              "“有摩擦的滑移”。在 PBD 中这一步通过修改上一帧位置 prev 完成，等效于直接修改速度；"
              "在显式求解器中则直接作用于速度。")
    para(doc, "每帧统计最大穿透深度与接触点数，作为实验 E3 的观测量。由于碰撞在约束迭代内部反复执行，"
              "即使布料被拉紧贴在球面上，残留穿透也能保持在亚毫米量级。")

    heading(doc, "2.6 风场", 2)
    para(doc, "风场按面元法计算：对每个三角形，取其法向 n、面积 A 和三个顶点速度的平均值 v_c，"
              "相对风速为 v_rel = v_wind − v_c，则气动力为")
    para(doc, "F = C · A · (n · v_rel) · n + C_t · A · (v_rel − (n · v_rel)·n)",
         first_indent=False, align=WD_ALIGN_PARAGRAPH.CENTER)
    para(doc, "第一项是法向压力，第二项是切向阻力。把 F 平均分配到三个顶点，即得到每个质点的风致加速度。"
              "为了让旗帜产生自然的抖动，风速还叠加了随时间与空间变化的低频扰动（turbulence），"
              "并按 1 + 0.25 sin(1.7t) 的形式加入阵风。")

    heading(doc, "2.7 渲染与交互", 2)
    para(doc, "渲染使用 OpenGL 1.1 固定管线，不依赖任何扩展或第三方库。布料逐顶点计算法线并做双面光照，"
              "纹理为程序生成的格纹织物（512×512），地面为程序生成的棋盘纹理；布料沿光线方向投影到"
              "地面形成软阴影，远处用指数雾淡出。相机为轨道相机，左键拖拽旋转、滚轮缩放；"
              "当鼠标射线与某个质点的距离小于阈值时，按下左键即可抓住该质点并拖动，松开后释放。")
    para(doc, "为了在不引入 GUI 库的前提下显示参数，程序用 GDI 把 ASCII 字形渲染成一张纹理图集，"
              "再用 OpenGL 绘制文字，HUD 中实时显示求解器、网格规模、刚度、风速、最大拉伸率、"
              "穿透深度、接触点数和帧率。")

    heading(doc, "2.8 撕裂", 2)
    para(doc, "撕裂通过“删除弹簧”实现：当某根结构弹簧的长度超过其静止长度的阈值倍数（tearRatio）时，"
              "把该弹簧标记为断裂；若某个质点的所有结构弹簧都已断裂，则该质点被判定为脱离布料并从"
              "模拟与渲染中移除。这一过程会改变网格拓扑，属于变形动画中的拓扑变化，"
              "渲染时跳过包含失效质点的三角形即可。")

    # ---------------------------- 3 ---------------------------- #
    heading(doc, "三、实验器材", 1)
    table(doc,
          ["项目", "配置"],
          [["操作系统", "Windows 11（10.0.26200）64 位"],
           ["处理器 / 内存", "x86-64 多核处理器，16 GB 以上内存"],
           ["显卡", "NVIDIA GeForce RTX 5070 Ti Laptop GPU（OpenGL 4.6）"],
           ["编译器", "MinGW-w64 g++ 16.2.0（UCRT，x86_64）"],
           ["图形接口", "OpenGL 1.1 固定管线（系统 opengl32.dll，无第三方库）"],
           ["构建方式", "build.bat 一键编译，或 g++ 命令行；另提供 ClothLab.exe"],
           ["辅助工具", "Python 3 + Pillow（生成图表、GIF 与报告）"]],
          cap="表 3-1  实验环境", widths=[4.0, 12.0])

    # ---------------------------- 4 ---------------------------- #
    heading(doc, "四、实验步骤", 1)
    heading(doc, "4.1 工程结构与编译运行", 2)
    para(doc, "工程目录如下：src/ 为全部 C++ 源码，bin/ 为可执行文件，tools/ 为 Python 后处理脚本，"
              "data/ 保存实验数据与序列帧，report/ 保存报告与图表。编译命令为：")
    code_block(doc, "g++ -std=c++17 -O2 -o bin/ClothLab.exe src/*.cpp -lopengl32 -lgdi32 -luser32")
    para(doc, "运行方式分为交互模式与批处理模式。交互模式下双击可执行文件即可，按 H 显示/隐藏参数面板；"
              "批处理模式用于生成报告素材与实验数据：")
    code_block(doc,
               "ClothLab.exe --scene flag --record frames --frames 180 --width 720 --height 450\n"
               "ClothLab.exe --scene drape --frames 240 --shot drape.tga --no-hud\n"
               "ClothLab.exe --bench data/bench.csv")

    heading(doc, "4.2 场景构建", 2)
    para(doc, "六个场景共用同一套求解器，只改变网格尺寸、固定点、碰撞体和风场参数，"
              "既覆盖了课程中的布料动画与碰撞检测，也覆盖了变形动画中的拓扑变化。")
    table(doc,
          ["场景", "网格", "固定点", "碰撞体", "风场", "考察点"],
          [["旗帜 flag", "51×31", "左侧一列", "无", "9 m/s + 湍流", "风场、褶皱、稳定性"],
           ["盖球 drape", "41×41", "无", "球 + 地面", "无", "球面碰撞与覆盖"],
           ["桌布 table", "51×51", "无", "盒 + 地面", "无", "盒体棱边与下垂"],
           ["撕裂 tear", "41×41", "左侧一列", "无", "12 m/s", "撕裂与拓扑变化"],
           ["双球 spheres", "51×51", "无", "两球 + 地面", "无", "多体碰撞"],
           ["斜面 slide", "31×31", "无", "30° 斜面", "无", "摩擦与滑移"]],
          cap="表 4-1  演示场景", widths=[2.6, 2.0, 2.6, 3.4, 2.8, 2.6])

    heading(doc, "4.3 关键代码", 2)
    para(doc, "约束投影是整个求解器的核心，其实现如下（省略了边界判断）：")
    code_block(doc,
               "for (int it = 0; it < iters; ++it) {\n"
               "  for (const Spring& s : springs) {\n"
               "    if (s.broken) continue;\n"
               "    Vec3 d = pos[s.a] - pos[s.b];\n"
               "    float len = length(d);\n"
               "    float diff = (len - s.rest) / len * keff[s.type];\n"
               "    float wa = invMass[s.a], wb = invMass[s.b], w = wa + wb;\n"
               "    pos[s.a] -= d * (diff * wa / w);\n"
               "    pos[s.b] += d * (diff * wb / w);\n"
               "  }\n"
               "  collidePBD(false);   // 位置投影，迭代内不做摩擦\n"
               "}\n"
               "collidePBD(true);      // 最后一次修正并施加摩擦")
    para(doc, "碰撞修正在每次迭代中都会执行，因此布料贴紧球面时不会残留可见穿透；摩擦只在最后一次"
              "修正中施加，避免多次迭代把切向速度衰减过度。")

    heading(doc, "4.4 实验数据采集", 2)
    para(doc, "实验数据由无窗口的 --bench 模式批量产生。每个算例都先预热 60 帧以消除初始下落的影响，"
              "再统计若干帧的平均值；物理耗时用高精度计数器测量，只统计算法本身，不包含渲染。"
              "CSV 中记录了实验编号、参数、单帧耗时、最大/平均拉伸率、穿透深度、接触点数和动能等字段，"
              "报告中的曲线与表格全部由脚本从该文件生成。")

    # ---------------------------- 5 ---------------------------- #
    heading(doc, "五、实验结果与分析", 1)
    heading(doc, "5.1 视觉效果", 2)
    para(doc, "图 5-1 为程序运行时的完整界面，HUD 中给出了当前场景的求解器、网格规模、"
              "刚度、风速、最大拉伸率、穿透深度和帧率。图 5-2 到图 5-5 为各场景的渲染结果。")
    figure(doc, "shot_flag_hud.png", "图 5-1  程序运行界面（旗帜场景，含 HUD）", 15.5)
    figure(doc, "seq_flag.png", "图 5-2  旗帜在风场中的运动序列（t = 0.5 s / 1.3 s / 2.2 s / 3.0 s）", 16.5)
    figure(doc, "seq_drape.png", "图 5-3  布料下落并覆盖球体的过程（t = 0.25 s / 0.75 s / 1.5 s / 2.5 s）", 16.5)
    figure(doc, "shot_table.png", "图 5-4  桌布覆盖盒体：棱边处的悬垂与褶皱", 13.5)
    figure(doc, "seq_tear.png", "图 5-5  布料撕裂过程：弹簧断裂导致拓扑变化", 16.5)
    figure(doc, "shot_spheres.png", "图 5-6  布料同时覆盖两个球体", 13.5)
    figure(doc, "shot_slope.png", "图 5-7  30° 斜面上的摩擦滑移实验", 13.5)
    figure(doc, "shot_wire.png", "图 5-8  质点-弹簧网格（线框模式，结构/剪切/弯曲弹簧同时存在）", 13.5)
    para(doc, "从视觉效果看，布料在球面上形成了放射状褶皱，在盒体棱边处自然下垂，撕裂时断口呈锯齿状，"
              "符合质点-弹簧模型的预期。旗帜的波动幅度随风速与湍流强度变化，风速越大，"
              "自由边越难保持平整。")

    # E1
    heading(doc, "5.2 实验 E1：两类求解器的稳定性", 2)
    para(doc, "固定刚度（PBD 归一化刚度 1.0，显式弹簧 1.2×10⁵ N/m），只改变每帧子步数，"
              "统计旗帜场景 240 帧内的最大拉伸率与单帧物理耗时。结果如表 5-1 与图 5-9 所示。")
    e1 = exp_rows(rows, "E1_stability")
    pbd = sorted([r for r in e1 if r["solver"] == "pbd"], key=lambda r: r["substeps"])
    eul = sorted([r for r in e1 if r["solver"] == "euler"], key=lambda r: r["substeps"])
    tbl = []
    for p in pbd:
        e = next((r for r in eul if r["substeps"] == p["substeps"]), None)
        tbl.append([p["substeps"],
                    f"{p['max_stretch']:.4f}", f"{p['ms_per_frame']:.2f}",
                    ("发散" if e and e["diverged"] else (f"{e['max_stretch']:.4f}" if e else "-")),
                    (f"{e['ms_per_frame']:.2f}" if e else "-")])
    table(doc, ["子步数", "PBD 最大拉伸率", "PBD 耗时 (ms)", "欧拉最大拉伸率", "欧拉耗时 (ms)"],
          tbl, cap="表 5-1  子步数对两类求解器的影响（旗帜场景）", widths=[2.2, 3.4, 3.0, 3.8, 3.6], font_size=8.5)
    figure(doc, "fig_e1_stability.png", "图 5-9  最大拉伸率随子步数的变化", 13.5)
    e1d = {(r["solver"], r["substeps"]): r for r in e1}
    p6, p24 = e1d[("pbd", 6)], e1d[("pbd", 24)]
    q12, q32 = e1d[("euler", 12)], e1d[("euler", 32)]
    q6 = e1d[("euler", 6)]
    para(doc, f"PBD 在 6 个子步时最大拉伸率已降到 {p6['max_stretch']:.3f}，24 个子步时降到 "
              f"{p24['max_stretch']:.3f}，并且全程没有发散；显式欧拉在 2~8 个子步时直接数值发散"
              f"（位置溢出，布料飞出画面），直到 12 个子步才重新稳定，但最大拉伸率仍有 "
              f"{q12['max_stretch']:.2f}，即使增加到 32 个子步也只能降到 {q32['max_stretch']:.3f}。")
    para(doc, f"原因在于两者的稳定性机制不同：显式欧拉的稳定域由最高模态频率决定，"
              f"刚度越大需要的时间步越小，而且误差会以能量的形式累积；PBD 直接对位置施加约束，"
              f"每一步都把违反约束的位移投影回去，因此对刚度不敏感。代价是 PBD 每帧要做多次迭代，"
              f"在相同子步数下耗时约为欧拉的 6~10 倍（6 子步时 {p6['ms_per_frame']:.2f} ms 对 "
              f"{q6['ms_per_frame']:.2f} ms）。但若以“达到同等刚度”为标准，欧拉需要 32 个子步以上、"
              f"耗时 {q32['ms_per_frame']:.2f} ms 且仍有 {(q32['max_stretch'] - 1) * 100:.0f}% 的拉伸，"
              f"而 PBD 只需 6 个子步、{p6['ms_per_frame']:.2f} ms 就能把拉伸控制在 "
              f"{(p6['max_stretch'] - 1) * 100:.1f}%，综合来看 PBD 的性价比更高，"
              f"这也是程序默认采用 PBD 的原因。")

    # E2
    heading(doc, "5.3 实验 E2：迭代次数与布料刚度", 2)
    para(doc, "固定子步数为 6，改变 PBD 的约束迭代次数，观察最大拉伸率与耗时的变化。")
    e2 = sorted(exp_rows(rows, "E2_iterations"), key=lambda r: r["iters"])
    table(doc, ["迭代次数", "最大拉伸率", "平均相对误差", "耗时 (ms)"],
          [[r["iters"], f"{r['max_stretch']:.4f}", f"{r['mean_stretch']:.4f}",
            f"{r['ms_per_frame']:.2f}"] for r in e2],
          cap="表 5-2  迭代次数对刚度与耗时的影响", widths=[3.0, 4.2, 4.4, 4.4], font_size=8.5)
    figure(doc, "fig_e2a_iterations.png", "图 5-10  最大拉伸率随迭代次数的变化", 13.2)
    figure(doc, "fig_e2b_iter_time.png", "图 5-11  单帧物理耗时随迭代次数的变化", 13.2)
    i1, i20 = e2[0], e2[-1]
    i8 = next(r for r in e2 if r["iters"] == 8)
    para(doc, f"最大拉伸率从 1 次迭代的 {i1['max_stretch']:.3f} 单调下降到 20 次迭代的 "
              f"{i20['max_stretch']:.3f}，平均相对误差从 {i1['mean_stretch']:.3f} 降到 "
              f"{i20['mean_stretch']:.4f}，说明迭代次数直接决定了约束的满足程度，也就是布料的“硬度”。"
              f"耗时随迭代次数线性增长（{i1['ms_per_frame']:.2f} ms → {i20['ms_per_frame']:.2f} ms），"
              f"因为每次迭代都要遍历全部弹簧。在实际使用中，6~8 次迭代已经能兼顾刚度与实时性："
              f"8 次迭代时拉伸率 {i8['max_stretch']:.3f}、耗时 {i8['ms_per_frame']:.2f} ms，"
              f"在 1280×800 分辨率下仍能保持 60 FPS。")

    # E3
    heading(doc, "5.4 实验 E3：子步数与穿透深度", 2)
    para(doc, "在盖球场景中，子步数决定了每帧内约束与碰撞被执行的次数。子步越少，"
              "单步内质点位移越大，越容易在两次碰撞修正之间“穿入”球体。")
    e3 = sorted(exp_rows(rows, "E3_substeps_pen"), key=lambda r: r["substeps"])
    table(doc, ["子步数", "最大穿透 (mm)", "平均接触点", "耗时 (ms)", "最大拉伸率"],
          [[r["substeps"], f"{r['pen_mm']:.3f}", f"{r['contacts']:.0f}",
            f"{r['ms_per_frame']:.2f}", f"{r['max_stretch']:.4f}"] for r in e3],
          cap="表 5-3  子步数对穿透深度的影响（盖球场景）", widths=[2.2, 3.6, 3.4, 3.2, 3.6], font_size=8.5)
    figure(doc, "fig_e3_penetration.png", "图 5-12  最大穿透深度随子步数的变化", 13.2)
    d3 = {r["substeps"]: r for r in e3}
    para(doc, f"1 个子步时最大穿透达到 {d3[1]['pen_mm']:.1f} mm，肉眼可见布料陷进球体；"
              f"2 个子步降到 {d3[2]['pen_mm']:.1f} mm；4 个子步已降到 {d3[4]['pen_mm']:.2f} mm，"
              f"6 个子步为 {d3[6]['pen_mm']:.2f} mm，约为布料厚度（4 mm）的 "
              f"{d3[6]['pen_mm'] / 4 * 100:.0f}%。继续增加子步收益递减，但耗时线性上升。"
              f"因此默认取 6 个子步，在 1280×800 下仍可保持实时。")

    # E4
    heading(doc, "5.5 实验 E4：摩擦系数与滑移", 2)
    para(doc, "把布料从 0.55 m 高处落到 30° 斜面上，观察 3 秒内布料沿斜面方向的平均位移。"
              "摩擦系数 μ 在 0~0.9 之间变化。")
    e4 = sorted(exp_rows(rows, "E4_friction"), key=lambda r: r["friction"])
    table(doc, ["摩擦系数 μ", "下滑距离 (m)", "耗时 (ms)"],
          [[f"{r['friction']:.2f}", f"{r['overhang']:.3f}", f"{r['ms_per_frame']:.2f}"] for r in e4],
          cap="表 5-4  摩擦系数对下滑距离的影响", widths=[4.0, 6.0, 6.0], font_size=8.5)
    figure(doc, "fig_e4_friction.png", "图 5-13  摩擦系数与布料下滑距离的关系", 13.2)
    m0 = next(r for r in e4 if abs(r["friction"]) < 1e-6)
    m01 = next(r for r in e4 if abs(r["friction"] - 0.1) < 1e-6)
    m09 = next(r for r in e4 if r["friction"] > 0.85)
    para(doc, f"μ = 0 时布料在 3 秒内滑出 {m0['overhang']:.2f} m，几乎不受阻碍；"
              f"μ = 0.1 时骤降到 {m01['overhang']:.2f} m；μ = 0.9 时只有 {m09['overhang']:.2f} m，"
              f"基本被“钉”在斜面上。曲线在低摩擦区下降很快、高摩擦区趋于平缓，"
              f"说明摩擦主要抑制切向速度，一旦切向速度被压到接近零，继续增大 μ 的收益就很小了。"
              f"这一结果与“静止摩擦使物体不滑动”的直觉一致。")

    # E5
    heading(doc, "5.6 实验 E5：网格规模与性能", 2)
    para(doc, "在盖球场景中把网格从 21×21 增加到 81×81，保持子步数与迭代次数不变，"
              "测量单帧物理耗时。质点数为 N²，弹簧数约为 6N²，因此耗时理论上应随 N² 增长。")
    e5 = sorted(exp_rows(rows, "E5_resolution"), key=lambda r: int(r["label"][1:]))
    table(doc, ["网格", "质点数", "弹簧数（约）", "耗时 (ms)", "最大拉伸率"],
          [[r["label"][1:] + "×" + r["label"][1:],
            int(r["label"][1:]) ** 2, 6 * int(r["label"][1:]) ** 2,
            f"{r['ms_per_frame']:.2f}", f"{r['max_stretch']:.4f}"] for r in e5],
          cap="表 5-5  网格规模对性能的影响", widths=[3.2, 3.0, 3.6, 3.2, 3.0], font_size=8.5)
    figure(doc, "fig_e5_resolution.png", "图 5-14  单帧物理耗时随网格规模的变化", 13.2)
    n0, n1 = e5[0], e5[-1]
    mid = [r for r in e5 if r["label"] in ("n41", "n51")]
    para(doc, f"从 21×21（{int(n0['label'][1:]) ** 2} 个质点）到 81×81（{int(n1['label'][1:]) ** 2} 个质点），"
              f"耗时从 {n0['ms_per_frame']:.2f} ms 增加到 {n1['ms_per_frame']:.2f} ms，"
              f"约 {n1['ms_per_frame'] / n0['ms_per_frame']:.0f} 倍，与质点数约 "
              f"{(int(n1['label'][1:]) / int(n0['label'][1:])) ** 2:.0f} 倍的增长基本吻合；"
              f"81×81 时物理计算已经超过 16.7 ms 的实时预算。因此在交互演示中使用 41×41 到 51×51 的网格"
              f"（{mid[0]['ms_per_frame']:.1f}~{mid[1]['ms_per_frame']:.1f} ms），把剩余时间留给渲染与录制；"
              f"只有在离线出图时才使用更高分辨率。")

    # E6
    heading(doc, "5.7 实验 E6：各场景的计算开销", 2)
    e6 = exp_rows(rows, "E6_scenes")
    table(doc, ["场景", "耗时 (ms)", "最大拉伸率", "平均穿透 (mm)"],
          [[r["scene"], f"{r['ms_per_frame']:.2f}", f"{r['max_stretch']:.4f}",
            f"{r['pen_mm']:.3f}"] for r in e6],
          cap="表 5-6  各场景在默认参数下的开销", widths=[4.0, 4.0, 4.4, 4.6], font_size=8.5)
    figure(doc, "fig_e6_scenes.png", "图 5-15  各场景的单帧物理耗时", 13.2)
    s6 = {r["scene"]: r for r in e6}
    para(doc, f"旗帜场景只有风场、没有碰撞，开销最低（{s6['flag']['ms_per_frame']:.2f} ms）；"
              f"盖球与双球场景需要处理大量球面接触（每帧上千个接触点），"
              f"桌布场景的盒体棱边会导致更频繁的碰撞修正，因此耗时最高（{s6['table']['ms_per_frame']:.2f} ms）。"
              f"所有场景在 1280×800 下都能保持 60 FPS，满足实时交互的要求。")

    # discussion
    heading(doc, "5.8 讨论与局限", 2)
    for s in [
        "（1）质量尺度的影响：程序把每个质点的质量取为 1 kg，使得“刚度/质量”比成为唯一有效的"
        "力学参数。这虽然简化了调参，但也意味着弹簧刚度的绝对值没有物理意义，"
        "只能用于相对比较。若要与真实织物对照，需要按面密度重新标定质量与刚度。",
        "（2）自碰撞尚未实现：布料折叠到自身时会发生穿插，这是本程序最明显的视觉缺陷。"
        "可行的改进是用空间哈希做顶点-三角形距离检测，在约束迭代中加入自碰撞约束；"
        "但实现与调参成本较高，留作后续工作。",
        "（3）显式欧拉求解器的定位：它的实现保持简单，用于与 PBD 对照，说明“为什么工业界更偏爱"
        "基于约束的方法”。在相同刚度下它需要多得多的子步，且仍偏软，因此程序默认使用 PBD。",
        "（4）渲染层面的简化：固定管线无法做真正的软阴影和环境光遮蔽，阴影是把布料沿光线方向"
        "压扁投影到地面得到的，只适用于平面地面；若要更真实的效果，需要引入阴影贴图或光线追踪。",
    ]:
        para(doc, s)

    # ---------------------------- 6 ---------------------------- #
    heading(doc, "六、实验感想与心得", 1)
    para(doc, "这次实验从“布料为什么会皱”这个问题出发，把课堂上讲的质点-弹簧模型、显式积分、"
              "约束投影和碰撞检测串成了一条完整的链路。真正动手之后才发现，写出一个能动的布料并不难，"
              "难的是让它“一直能动、动得可信、还能调得动”。")
    para(doc, "第一个让我印象深刻的点是稳定性。最初用显式欧拉直接积分胡克弹簧，参数稍大布料就会炸开，"
              "画面里只剩下一堆飞散的三角形。后来把子步数、弹簧阻尼和刚度放在一起分析，"
              "才真正理解 Δt < 2/ω 这个条件的含义，也理解了为什么工业界更愿意用基于约束的方法："
              "PBD 把“稳定”写进了算法结构里，而不是靠调参去赌。实验 E1 的数据把这种差别量化了出来，"
              "这比任何文字描述都有说服力。")
    para(doc, "第二个体会是碰撞处理的细节远比想象中多。位置投影本身只有几行代码，但如果没有摩擦，"
              "布料在球面上会像抹了油一样滑走；如果摩擦施加在每一次迭代里，又会把布料“粘”得过死。"
              "最后把摩擦放到最后一次修正中，并统一用切向位移衰减来实现，才得到比较自然的效果。"
              "实验 E3、E4 也说明，穿透和滑移都不是“调一个参数就完事”的问题，而是与子步数、"
              "接触频率耦合在一起的。")
    para(doc, "第三个收获来自工程层面。为了让程序能在没有第三方库的机器上直接运行，"
              "窗口、OpenGL 上下文、文字渲染、截图和 GIF 合成都得自己解决；"
              "为了让报告里的每张图都能复现，又把参数扫描、数据记录和绘图拆成了独立脚本。"
              "这些工作虽然琐碎，但让整个项目从“一次性的作业”变成了“可以反复实验的小工具”。")
    para(doc, "当然，程序还有明显的不足：没有自碰撞，布料折叠时会穿模；阴影是平面投影，"
              "离开地面就不成立；显式欧拉求解器只是对照实现，并没有做真正的隐式积分。"
              "如果继续做下去，我会优先加入基于空间哈希的自碰撞，再尝试用 XPBD 让刚度与迭代次数解耦，"
              "让布料的“软硬”真正成为一个可以标定的物理量。")

    # ---------------------------- refs ---------------------------- #
    heading(doc, "参考文献", 1)
    refs = [
        "[1] Provot X. Deformation Constraints in a Mass-Spring Model to Describe Rigid Cloth Behavior. "
        "Graphics Interface, 1995: 147-154.",
        "[2] Müller M, Heidelberger B, Hennix M, Ratcliff J. Position Based Dynamics. "
        "Journal of Visual Communication and Image Representation, 2007, 18(2): 109-118.",
        "[3] Baraff D, Witkin A. Large Steps in Cloth Simulation. SIGGRAPH 1998: 43-54.",
        "[4] Nealen A, Müller M, Keiser R, Boxerman E, Carlson M. Physically Based Deformable Models "
        "in Computer Graphics. Computer Graphics Forum, 2006, 25(4): 809-836.",
        "[5] 课程课件. 计算机动画：布料动画、碰撞检测与粒子系统. 2024.",
    ]
    for r in refs:
        para(doc, r, size=9.5, first_indent=False, space_after=3)

    # ---------------------------- appendix ---------------------------- #
    heading(doc, "附录 A  文件清单", 1)
    table(doc, ["路径", "说明"],
          [["src/*.cpp, src/*.h", "全部 C++ 源代码（约 1800 行）"],
           ["bin/ClothLab.exe", "已编译的可执行程序，双击即可运行"],
           ["build.bat", "一键编译脚本"],
           ["tools/make_gif.py", "序列帧合成 GIF"],
           ["tools/make_strip.py", "多帧拼图（报告用）"],
           ["tools/plots.py, tools/make_figs.py", "由 CSV 生成报告图表"],
           ["tools/make_report.py", "由数据与图表生成本报告"],
           ["data/bench.csv", "六组实验的原始数据"],
           ["report/figures/*.png, *.gif", "报告插图与演示动画"]],
          cap="表 A-1  交付文件", widths=[5.6, 10.4])

    heading(doc, "附录 B  快捷键与参数", 1)
    table(doc, ["按键", "功能", "按键", "功能"],
          [["1–6", "切换场景", "空格", "暂停/继续"],
           ["N", "单步执行", "R", "重置场景"],
           ["T", "切换求解器", "W", "线框模式"],
           ["G", "阴影开关", "C", "碰撞体显示"],
           ["H", "参数面板", "J / K", "刚度 −/+"],
           ["U / I", "迭代次数 −/+", "[ / ]", "风速 −/+"],
           ["P", "截图", "F", "录制帧序列"],
           ["鼠标左键", "旋转 / 抓取布料", "滚轮", "缩放"]],
          cap="表 B-1  交互操作", widths=[2.8, 5.6, 2.8, 4.8])

    doc.save(OUT)
    print("saved", OUT)


if __name__ == "__main__":
    build()




