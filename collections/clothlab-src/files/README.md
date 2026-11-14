# ClothLab — 基于质点-弹簧模型的布料动画与碰撞响应

计算机动画课程设计。用 C++17 + OpenGL 1.1 实现的三维布料实时仿真程序：
质点-弹簧布料建模、两套求解器（PBD/Verlet 与显式欧拉）、球体/平面/盒体碰撞与摩擦、
风场、撕裂、实时交互渲染，以及 6 组可复现的定量实验。

**零第三方依赖**：只需要系统自带的 `opengl32.dll` / `gdi32.dll` / `user32.dll`。

---

## 快速开始

```bat
:: 直接运行（已编译好）
bin\ClothLab.exe

:: 从源码编译（需要 MinGW-w64 g++）
build.bat
```

窗口内操作：

| 按键 | 功能 | 按键 | 功能 |
|---|---|---|---|
| `1`–`6` | 切换场景 | `空格` | 暂停 / 继续 |
| `N` | 单步 | `R` | 重置场景 |
| `T` | 切换求解器（PBD / 显式欧拉） | `W` | 线框模式 |
| `G` | 阴影开关 | `C` | 碰撞体显示 |
| `H` | 参数面板 | `J` / `K` | 减小 / 增大刚度 |
| `U` / `I` | 减少 / 增加迭代次数 | `[` / `]` | 减小 / 增大风速 |
| `P` | 截图（TGA） | `F` | 录制序列帧 |
| 鼠标左键 | 拖拽旋转；点中布料可抓取 | 滚轮 | 缩放 |

场景：`1` 旗帜、`2` 盖球、`3` 桌布、`4` 撕裂、`5` 双球、`6` 斜面摩擦。

---

## 命令行

```bat
:: 运行指定场景并截图（--frames 为固定步数，便于复现）
ClothLab.exe --scene drape --frames 240 --shot drape.tga --no-hud

:: 录制序列帧（TGA），再用 tools/make_gif.py 合成 GIF
ClothLab.exe --scene flag --record data/frames --frames 180 --width 720 --height 450

:: 批量参数扫描，输出实验数据 CSV
ClothLab.exe --bench data/bench.csv
```

主要参数：`--scene <flag|drape|table|tear|spheres|slide>`、`--frames N`、`--shot path`、
`--record dir`、`--width`、`--height`、`--solver <pbd|euler>`、`--iter N`、`--substeps N`、
`--k 0..1`、`--wind m/s`、`--wire`、`--no-hud`、`--console`。

---

## 目录结构

```
src/             C++ 源码（约 1800 行）
  main.cpp       Win32 窗口、固定步长主循环、输入、HUD、录制
  cloth.*        质点-弹簧模型、PBD / 欧拉求解器、风场、撕裂、统计量
  collision.h    球体 / 平面 / 盒体碰撞检测与位置修正
  scene.*        6 个场景预设
  renderer.*     OpenGL 固定管线渲染、纹理、阴影、雾
  hud.*          GDI 字形图集 + OpenGL 文字
  capture.*      帧缓冲 → TGA
  bench.*        无窗口实验扫描 → CSV
bin/ClothLab.exe 可执行程序（静态链接，双击即用）
build.bat        一键编译
tools/           Python 后处理脚本（Pillow，无 matplotlib）
  make_gif.py    序列帧 → GIF
  make_strip.py  多帧拼图
  plots.py       极简绘图库（Pillow 实现）
  make_figs.py   bench.csv → 报告图表
  make_report.py 数据 + 图表 → docx 报告
data/bench.csv   6 组实验原始数据
report/          实验报告（docx / pdf）与图表
```

---

## 复现实验与报告

```bat
:: 1. 重新采集数据（约 1 分钟）
bin\ClothLab.exe --bench data\bench.csv

:: 2. 由数据生成图表
python tools\make_figs.py

:: 3. 由数据与图表生成报告
python tools\make_report.py
```

依赖：Python 3 + Pillow（只用于生成图表、GIF 与报告，不影响程序运行）。

---

## 实验内容

| 编号 | 实验 | 变量 | 观测量 |
|---|---|---|---|
| E1 | 两类求解器的稳定性 | 子步数 | 最大拉伸率、是否发散、耗时 |
| E2 | 迭代次数与布料刚度 | PBD 迭代次数 | 拉伸率、误差、耗时 |
| E3 | 子步数与穿透深度 | 子步数 | 最大穿透、接触点、耗时 |
| E4 | 摩擦系数与滑移 | 摩擦系数 μ | 3 s 内沿斜面位移 |
| E5 | 网格规模与性能 | 网格 N×N | 单帧物理耗时 |
| E6 | 各场景开销 | 场景 | 耗时、拉伸率、穿透 |

结论摘要：PBD 在 6 子步时最大拉伸率 1.067 且不发散，显式欧拉在 2–8 子步直接发散、
12 子步仍有 1.41 的拉伸；6 子步下最大穿透 0.29 mm；摩擦系数从 0 增至 0.9 时，
斜面下滑距离由 7.92 m 降到 0.44 m；81×81 网格的物理耗时为 18.6 ms。

---

## 已知限制

- 未实现自碰撞，布料折叠到自身时会穿插；
- 阴影为平面投影，仅适用于平整地面；
- 显式欧拉求解器为对照实现，未做隐式积分；
- 质点质量统一取 1 kg，弹簧刚度只有相对意义。
