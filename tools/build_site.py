# -*- coding: utf-8 -*-
"""Build the KYSIIN.ARCHIVE repo: copy materials, write .gitignore/README, generate pages."""
import os, io, re, json, time, shutil, stat
from urllib.parse import quote
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_md
import publish

HOME = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.dirname(HOME)
REPO = os.path.join(WORKSPACE, "site")
VAULT = r"E:\Proj\Obsidian Vault"
ANIM = r"E:\Proj\Animation"
PHY = r"E:\Proj\PHY"
KIT = r"C:\Users\***\.dsh\skills\endfield-ui\assets"

SKIP_DIRS = {"node_modules", "__pycache__", ".git", ".obsidian", ".pnpm-store",
             ".pnpm-cache", "cache", "dist", ".vitepress", ".piptmp", ".spike", ".tmp",
             "_extract"}          # 解包 Office 文件的中间产物（ppt/slides/*.xml 之类）
SKIP_EXT = {".pyc", ".log", ".tmp", ".DS_Store",
            ".zip"}              # 压缩包一律不进站（里面多是作业源码），也不在页面上列出

# ---- 分组元数据（归属 / 方向 / 学期）----
META = {}
META_AREAS = ["信息安全", "计算机基础", "数理基础", "计算机拓展"]
META_KINDS = ["专题", "课程", "实验"]
META_TERMS = []
try:
    _meta = json.load(io.open(os.path.join(HOME, "collections.json"), encoding="utf-8-sig"))
    META = {c["slug"]: c for c in _meta.get("collections", [])}
    META_AREAS = _meta.get("areas", META_AREAS)
    META_KINDS = _meta.get("kinds", META_KINDS)
    META_TERMS = sorted({c.get("term", "") for c in _meta.get("collections", []) if c.get("term")}, reverse=True)
except Exception as _e:
    print("  ! collections.json:", _e)

STAGE = os.path.join(WORKSPACE, "content")

COLLECTIONS = [
    dict(slug="animation-review", group="专题复习", src="Animation",
         name="计算机动画", tag="PDF", course="animation-review", label="复习资料",
         desc="计算机动画：16 部分期末复习讲义（章节 + 判断题 / 问答 / 附录），以及 ClothLab 布料模拟实验的源码与产出。",
         copies=[(os.path.join(ANIM, "期末复习", "content"), "content"),
                 (os.path.join(ANIM, "期末复习", "figs"), "figs"),
                 (os.path.join(ANIM, "期末复习", "计算机动画期末复习资料.pdf"), ""),
                 (os.path.join(ANIM, "期末复习", "计算机动画期末复习资料.docx"), "")]),
    dict(slug="physics-review", group="专题复习", src="PHY",
         name="大学物理乙2", tag="MD", course="physics-review", label="复习资料",
         desc="大学物理乙2：复习路线、公式速查、通用做题方法、综合自测卷与第 12~14 章笔记，另有一份公式速查笔记。",
         copies=[(PHY, "")],
         exclude={"大学物理乙2复习资料.md", "大学物理乙2复习资料.html"}),
    dict(slug="sfs", group="课程笔记", src="Obsidian Vault", name="软件安全原理与实践", tag="PDF",
         desc="软件安全原理与实践的课程笔记与资料。", copies=[(os.path.join(VAULT, "SFS"), "")]),
    dict(slug="oop", group="课程笔记", src="Obsidian Vault", name="面向对象程序设计（OOP）", tag="PDF",
         desc="面向对象程序设计课程的笔记与实验。",
         copies=[(os.path.join(VAULT, "OOP"), ""), (os.path.join(STAGE, "oop-supplement"), "补充")],
         exclude={"readme.md", "Readme.md", "README.md"},
         # 作业源码不发布：实验代码只留报告/说明，.cpp/.h/.sh 一概不进站
         skip_ext=(".cpp", ".h", ".hpp", ".c", ".sh")),
    dict(slug="netlab", group="课程笔记", src="Obsidian Vault", name="计算机网络", tag="PDF",
         desc="计算机网络的课程笔记与实验记录。",
         copies=[(os.path.join(VAULT, "Netlab"), "")],
         skip_ext=(".cc", ".hh", ".cpp", ".h")),
    dict(slug="sys2", group="课程笔记", src="Obsidian Vault", name="计算机系统Ⅱ", tag="PDF",
         desc="计算机系统Ⅱ的课程笔记与资料。", copies=[(os.path.join(VAULT, "SYS2"), "")]),
    dict(slug="signal", group="课程笔记", src="Obsidian Vault", name="面向信息安全的信号处理", tag="PDF",
         desc="面向信息安全的信号处理课程笔记与资料。", copies=[(os.path.join(VAULT, "Signal"), "")]),
    dict(slug="wireless", group="课程笔记", src="Obsidian Vault", name="无线与物联网安全基础", tag="PDF",
         desc="无线与物联网安全基础的课程资料。", copies=[(os.path.join(VAULT, "Wireless"), "")]),
    dict(slug="phy-notes", group="课程笔记", src="Obsidian Vault", name="物理笔记", tag="MD",
         desc="物理相关笔记。", course="physics-review", label="笔记",
         copies=[(os.path.join(VAULT, "PHY"), "")]),
    dict(slug="clothlab-src", group="代码与实验", src="Animation", name="ClothLab · 源码与构建", tag="SRC",
         desc="布料模拟实验的 C++ 源码、工具脚本、构建脚本与选题规划。",
         course="animation-review", label="ClothLab 源码",
         copies=[(os.path.join(ANIM, "src"), "src"), (os.path.join(ANIM, "tools"), "tools"),
                 (os.path.join(ANIM, "README.md"), ""), (os.path.join(ANIM, "选题与规划.md"), ""),
                 (os.path.join(ANIM, "build.bat"), "")]),
    dict(slug="clothlab-out", group="代码与实验", src="Animation", name="ClothLab · 产出文件", tag="OUT",
         desc="实验的产出文件（渲染结果、报告等），体积较大，暂未收录。",
         course="animation-review", label="ClothLab 产出",
         copies=[],
         external=[(os.path.join(ANIM, "bin"), "bin"), (os.path.join(ANIM, "data"), "data"),
                   (os.path.join(ANIM, "report"), "report"),
                   (os.path.join(ANIM, "ClothLab_提交包.zip"), "ClothLab_提交包.zip"),
                   (os.path.join(ANIM, "sample.doc"), "sample.doc")]),
    dict(slug="db-2026", group="课程笔记", src="待整理", name="数据库系统", tag="MD",
         desc="数据库系统的实验报告、大作业与期末总结。", copies=[(os.path.join(STAGE, "db-2026"), "")]),
    dict(slug="sys1-2024", group="课程笔记", src="待整理", name="计算机系统Ⅰ", tag="MD",
         desc="计算机系统Ⅰ的实验报告与综合项目。", copies=[(os.path.join(STAGE, "sys1-2024"), "")]),
    dict(slug="sysintro-2023", group="课程笔记", src="待整理", name="计算机系统概论", tag="MD",
         desc="计算机系统概论的实验报告与课程记录。", copies=[(os.path.join(STAGE, "sysintro-2023"), "")]),
    dict(slug="netsec-2026", group="课程笔记", src="待整理", name="网络安全原理与实践", tag="MD",
         desc="网络安全原理与实践的实验报告与速记。", copies=[(os.path.join(STAGE, "netsec-2026"), "")]),
    dict(slug="crypto-2026", group="课程笔记", src="待整理", name="密码学", tag="MD",
         desc="密码学的算法笔记与实验解析。", copies=[(os.path.join(STAGE, "crypto-2026"), "")]),
    dict(slug="ads-2024", group="课程笔记", src="待整理", name="高级数据结构与算法分析", tag="MD",
         desc="ADS 的项目报告与实现笔记。", copies=[(os.path.join(STAGE, "ads-2024"), "")]),
    dict(slug="iot-2026", group="课程笔记", src="待整理", name="物联网与信息电子应用导论", tag="MD",
         desc="物联网课程的结课设计报告。", copies=[(os.path.join(STAGE, "iot-2026"), "")]),
    dict(slug="compiler-2026", group="课程笔记", src="待整理", name="编译原理", tag="MD",
         desc="编译原理的实验解答。", copies=[(os.path.join(STAGE, "compiler-2026"), "")]),
]

TYPE_MAP = {".md": "MD", ".pdf": "PDF", ".png": "PNG", ".jpg": "JPG", ".jpeg": "JPG",
            ".gif": "GIF", ".svg": "SVG", ".doc": "DOC", ".docx": "DOCX", ".zip": "ZIP",
            ".cpp": "C++", ".h": "C++", ".hpp": "C++", ".c": "C", ".py": "PY",
            ".js": "JS", ".mjs": "JS", ".json": "JSON", ".html": "HTML", ".css": "CSS",
            ".blend": "BLEND", ".pptx": "PPTX", ".xlsx": "XLSX", ".exe": "EXE",
            ".dll": "DLL", ".bin": "BIN", ".obj": "OBJ", ".mp4": "MP4", ".gifv": "GIF",
            ".ipynb": "IPYNB", ".txt": "TXT", ".yml": "YAML", ".yaml": "YAML"}


def typ(ext):
    return TYPE_MAP.get(ext.lower(), ext.lstrip(".").upper()[:6] or "—")


def human(n):
    if n >= 1048576:
        return f"{n / 1048576:.1f} MB"
    if n >= 1024:
        return f"{n / 1024:.0f} KB"
    return f"{n} B"


def short_date(d):
    """2026.11.15 -> 11.15 in the build year; keep the year for older material."""
    return d[len(BUILD_YEAR) + 1:] if d.startswith(BUILD_YEAR + ".") else d


def copy_tree(src, dst, rel_prefix="", exclude=(), skip_ext=()):
    """Copy one source path into the repo; returns list of copied file stats.

    skip_ext: 该分组额外排除的扩展名（例如课程作业的源码）。
    """
    out = []
    skip = SKIP_EXT | {e.lower() for e in skip_ext}
    if os.path.isfile(src):
        if os.path.splitext(src)[1].lower() in skip:
            return out
        if os.path.isdir(dst):
            dst = os.path.join(dst, os.path.basename(src))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        st = os.stat(dst)
        out.append(dict(path=os.path.relpath(dst, REPO).replace("\\", "/"),
                        size=st.st_size, mtime=st.st_mtime,
                        ext=os.path.splitext(dst)[1].lower()))
        return out
    for dirpath, dirnames, filenames in os.walk(src):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS
                       and not d.startswith(".") and "acl-recovery" not in d]
        rel = os.path.relpath(dirpath, src)
        target_dir = dst if rel == "." else os.path.join(dst, rel)
        os.makedirs(target_dir, exist_ok=True)
        for fn in filenames:
            if os.path.splitext(fn)[1].lower() in skip or fn in exclude:
                continue
            s = os.path.join(dirpath, fn)
            d = os.path.join(target_dir, fn)
            try:
                shutil.copy2(s, d)
                os.chmod(d, stat.S_IWRITE | stat.S_IREAD)
                st = os.stat(d)
            except OSError:
                continue
            out.append(dict(path=os.path.relpath(d, REPO).replace("\\", "/"),
                            size=st.st_size, mtime=st.st_mtime,
                            ext=os.path.splitext(d)[1].lower()))
    return out


def list_external(paths):
    out = []
    for src, label in paths:
        if os.path.isfile(src):
            st = os.stat(src)
            out.append(dict(path=label, size=st.st_size, mtime=st.st_mtime,
                            ext=os.path.splitext(src)[1].lower()))
            continue
        for dirpath, dirnames, filenames in os.walk(src):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS
                           and not d.startswith(".") and "acl-recovery" not in d]
            rel = os.path.relpath(dirpath, src)
            for fn in filenames:
                p = os.path.join(dirpath, fn)
                try:
                    st = os.stat(p)
                except OSError:
                    continue
                name = label if rel == "." else f"{label}/{rel.replace(os.sep, '/')}"
                out.append(dict(path=f"{name}/{fn}", size=st.st_size, mtime=st.st_mtime,
                                ext=os.path.splitext(fn)[1].lower()))
    return out


def force_rmtree(path):
    """Windows: source files may be read-only; clear the attribute then remove."""
    def fix(func, target, exc):
        try:
            os.chmod(target, stat.S_IWRITE)
            func(target)
        except OSError:
            pass
    shutil.rmtree(path, onerror=fix)


# 把元数据（方向/学期）挂到每个分组上，供渲染器使用
for _c in COLLECTIONS:
    _m = META.get(_c["slug"], {})
    _c["kind"] = _m.get("kind", _c["group"].replace("课程笔记", "课程").replace("代码与实验", "实验"))
    _c["area"] = _m.get("area", "")
    _c["term"] = _m.get("term", "")
    # course: 同一门课可以有多份资料（复习资料 / 实验源码 / 补充笔记），
    # 首页与课程页按 course 聚合成一张卡，没写 course 的分组自己就是一门课
    _c["course"] = _c.get("course") or _c["slug"]
    _c["label"] = _c.get("label") or ""

COURSES = []            # 有序课程表，元素在下面逐步补全
COURSE_INDEX = {}
for _c in COLLECTIONS:
    _key = _c["course"]
    _co = COURSE_INDEX.get(_key)
    if _co is None:
        _co = dict(slug=_key, name=_c["name"], desc=_c["desc"], area=_c["area"],
                   term=_c["term"], members=[], articles=[], files=[], external=[])
        COURSE_INDEX[_key] = _co
        COURSES.append(_co)
    _co["members"].append(_c)

# 课程内分区（章节 / 专题 / 实验）：每篇文章的分区登记在 sections.json
SECTION_ORDER, section_of = render_md.load_sections()

# 每次构建换一个资源版本号，避免浏览器继续用缓存里的旧 search.js / search.json
BUILD_VER = time.strftime("%Y%m%d%H%M")
BUILD_DATE = time.strftime("%Y.%m.%d")
BUILD_YEAR = time.strftime("%Y")

# ------------------------------------------------------------------ copy
if os.path.isdir(REPO):
    force_rmtree(REPO)
os.makedirs(REPO)
shutil.copytree(KIT, os.path.join(REPO, "assets"))
shutil.copy2(os.path.join(HOME, "search.js"), os.path.join(REPO, "assets", "search.js"))
# 自托管 Saira：可变字体 + 本地 @font-face（模板自带的那份）
os.makedirs(os.path.join(REPO, "assets", "fonts"), exist_ok=True)
for fn in ("Saira.ttf", "Saira-OFL.txt"):
    shutil.copy2(os.path.join(KIT, "..", "templates", "flutter", "fonts", fn),
                 os.path.join(REPO, "assets", "fonts", fn))
fonts_src = os.path.join(WORKSPACE, "vendor", "node_modules", "mathjax-full", "es5", "output", "chtml", "fonts", "woff-v2")
if os.path.isdir(fonts_src):
    dst = os.path.join(REPO, "assets", "mathjax", "fonts")
    os.makedirs(dst, exist_ok=True)
    for fn in os.listdir(fonts_src):
        if fn.endswith(".woff"):
            shutil.copy2(os.path.join(fonts_src, fn), os.path.join(dst, fn))
io.open(os.path.join(REPO, "assets", "local-fonts.css"), "w", encoding="utf-8", newline="\n").write(
    "@font-face{font-family:'Saira';src:url('./fonts/Saira.ttf') format('truetype');"
    "font-weight:100 900;font-stretch:50% 125%;font-style:normal;font-display:swap}\n")

SCROLLBAR_CSS = """
/* 滚动条：页面、左右侧栏、搜索面板、代码块共用一套（细、方角、透明轨道） */
:root { --scroll-color: rgba(0,0,0,.28); --scroll-thumb: rgba(0,0,0,.22); --scroll-thumb-hover: rgba(0,0,0,.38); }
:root[data-theme='dark'] { --scroll-color: rgba(255,255,255,.32); --scroll-thumb: rgba(255,255,255,.26); --scroll-thumb-hover: rgba(255,255,255,.45); }
@media (prefers-color-scheme: dark) {
  :root:not([data-theme]) { --scroll-color: rgba(255,255,255,.32); --scroll-thumb: rgba(255,255,255,.26); --scroll-thumb-hover: rgba(255,255,255,.45); }
}
html, .ef-margin, .efs ul, .ef-prose pre, .eq { scrollbar-width: thin; scrollbar-color: var(--scroll-color) transparent; }
html::-webkit-scrollbar, .ef-margin::-webkit-scrollbar, .efs ul::-webkit-scrollbar,
.ef-prose pre::-webkit-scrollbar, .eq::-webkit-scrollbar { width: 7px; height: 7px; }
html::-webkit-scrollbar-track, .ef-margin::-webkit-scrollbar-track, .efs ul::-webkit-scrollbar-track,
.ef-prose pre::-webkit-scrollbar-track, .eq::-webkit-scrollbar-track { background: transparent; }
html::-webkit-scrollbar-thumb, .ef-margin::-webkit-scrollbar-thumb, .efs ul::-webkit-scrollbar-thumb,
.ef-prose pre::-webkit-scrollbar-thumb, .eq::-webkit-scrollbar-thumb { background: var(--scroll-thumb); border-radius: 0; }
.ef-margin:hover::-webkit-scrollbar-thumb, .efs ul:hover::-webkit-scrollbar-thumb,
.ef-prose pre:hover::-webkit-scrollbar-thumb, .eq:hover::-webkit-scrollbar-thumb { background: var(--scroll-thumb-hover); }
"""

io.open(os.path.join(REPO, "assets", "local-fonts.css"), "a", encoding="utf-8", newline="\n").write(SCROLLBAR_CSS)

for c in COLLECTIONS:
    dest_root = os.path.join(REPO, "collections", c["slug"], "files")
    files = []
    for src, sub in c.get("copies", []):
        dst = os.path.join(dest_root, sub) if sub else dest_root
        files += copy_tree(src, dst, exclude=c.get("exclude", ()),
                           skip_ext=c.get("skip_ext", ()))
    c["files"] = files
    publish.process_collection(c, REPO)
    c["_external_src"] = [p for p, _ in c.get("external", [])]
    c["external"] = list_external(c.get("external", []))

# downloads (动画 PDF/DOCX 也放一份到 files/，便于首页直接下)
os.makedirs(os.path.join(REPO, "files"), exist_ok=True)
for src, name in ((os.path.join(ANIM, "期末复习", "计算机动画期末复习资料.pdf"), "计算机动画-期末复习资料.pdf"),
                  (os.path.join(ANIM, "期末复习", "计算机动画期末复习资料.docx"), "计算机动画-期末复习资料.docx")):
    if os.path.isfile(src):
        dst = os.path.join(REPO, "files", name)
        shutil.copy2(src, dst)
        if name.lower().endswith(".pdf"):
            publish.clear_meta_of(dst, title=os.path.splitext(name)[0])

# ------------------------------------------------------------------ render md
articles = render_md.render_all(REPO, COLLECTIONS)
for c in COLLECTIONS:
    c["articles"] = articles.get(c["slug"], [])
    print(f'  rendered {c["slug"]}: {len(c["articles"])} articles')

# ------------------------------------------------------------------ review-note PDFs
# 复习笔记页面上的「下载 PDF」：有现成 PDF 的上面已经挂好，没有的从页面现场生成。
pending = []
for c in COLLECTIONS:
    for a in c.get("articles", []):
        if not a.get("pdf_generated"):
            continue
        out = os.path.join(REPO, "collections", c["slug"], "files", a["pdf"])
        if not os.path.isfile(out):
            pending.append((c, a, out))
if pending:
    print("  review-note PDFs to generate: %d" % len(pending))
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=3) as pool:
    futures = [(c, a, out, pool.submit(publish.html_to_pdf, a["html"], out))
               for c, a, out in pending]
    for c, a, out, fut in futures:
        if fut.result():
            st = os.stat(out)
            c["files"].append(dict(path=os.path.relpath(out, REPO).replace("\\", "/"),
                                   size=st.st_size, mtime=st.st_mtime, ext=".pdf"))
        else:
            print("  ! missing review PDF:", a["pdf"])

# ------------------------------------------------------------------ stats
def agg(files):
    return dict(n=len(files), mb=sum(f["size"] for f in files) / 1048576.0,
                latest=time.strftime("%Y.%m.%d", time.localtime(max([f["mtime"] for f in files], default=0))) if files else "—")


for c in COLLECTIONS:
    c.update({k: v for k, v in agg(c["files"]).items()})
    c["out"] = agg(c["external"])

# 课程聚合：成员分组的文章 / 文件 / 统计并到一门课里
for co in COURSES:
    co["articles"] = [a for m in co["members"] for a in m.get("articles", [])]
    co["articles"].sort(key=lambda a: (SECTION_ORDER.index(a["section"])
                                       if a.get("section") in SECTION_ORDER else len(SECTION_ORDER),
                                       a["path"].lower()))
    co["files"] = [f for m in co["members"] for f in m["files"]]
    co["external"] = [f for m in co["members"] for f in m["external"]]
    co["n_files"] = sum(m["n"] for m in co["members"])
    co["mb"] = sum(m["mb"] for m in co["members"])
    co["out"] = agg(co["external"])
    co["latest"] = max([m["latest"] for m in co["members"] if m["latest"] != "—"], default="—")
    co["sections"] = [(s, [a for a in co["articles"] if a.get("section") == s])
                      for s in SECTION_ORDER]
    co["sections"] = [(s, items) for s, items in co["sections"] if items]
    # 只有登记、没有入库文件的分组（例如 ClothLab 产出）
    co["external_only"] = not co["n_files"] and bool(co["external"])

total_articles = sum(len(co["articles"]) for co in COURSES)
in_files = sum(co["n_files"] for co in COURSES)
in_mb = sum(co["mb"] for co in COURSES)
out_files = sum(co["out"]["n"] for co in COURSES)
out_mb = sum(co["out"]["mb"] for co in COURSES)
latest = max([co["latest"] for co in COURSES if co["latest"] != "—"], default="—")
section_totals = {s: sum(len(items) for co in COURSES
                         for name, items in co["sections"] if name == s)
                  for s in SECTION_ORDER}

# ------------------------------------------------------------------ page chrome
HEAD = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{title}</title>
<meta name="description" content="{desc}" />
<script src="{up}assets/variant.js"></script>
<link rel="stylesheet" href="{up}assets/local-fonts.css" />
<link rel="stylesheet" href="{up}assets/endfield.css" />
<style>
  body {{ --tri-h: 3px; --topbar-h: 3.1rem; }}
  body > .ef-tri {{ position: sticky; top: 0; z-index: 61; }}
  .topbar {{ position:sticky; top:var(--tri-h); z-index:60;
    display:flex; align-items:center; gap:1.5rem; padding:.85rem var(--ef-pad);
    border-bottom:1px solid var(--ef-rule); background:var(--ef-panel); }}
  .topbar .brand {{ margin:0; font-family:var(--ef-font-ui); font-size:.95rem;
    font-stretch:var(--ef-wider); font-weight:800; letter-spacing:.08em;
    text-decoration:none; color:var(--ef-ink); }}
  .topbar nav {{ display:flex; align-items:center; gap:1.25rem; margin-left:auto; }}
  .topbar nav a {{ text-decoration:none; color:var(--ef-ink-2);
    padding-bottom:2px; border-bottom:2px solid transparent; }}
  .topbar nav a[aria-current='page'] {{ color:var(--ef-ink); border-bottom-color:var(--ef-trace); }}
  /* 点顶栏跳分区时，别让粘性顶栏盖住那一段的标题 */
  #all, #stats {{ scroll-margin-top: calc(var(--tri-h) + var(--topbar-h) + .6rem); }}
  .title {{ margin:1.5rem 0 1rem; font-size:clamp(var(--ef-t-title),5.5vw,var(--ef-t-h1));
    font-weight:700; line-height:1.25; }}
  .ids {{ display:flex; flex-wrap:wrap; align-items:center; gap:.5rem; margin:0 0 .75rem; }}
  .foot {{ display:flex; flex-wrap:wrap; align-items:baseline; justify-content:space-between;
    gap:1rem; padding:1.5rem var(--ef-pad) 2.5rem; border-top:1px solid var(--ef-rule);
    color:var(--ef-ink-2); font-size:.875rem; }}
  .back {{ margin:1.5rem 0 0; }}
  @media (min-width: 960px) {{
    .ef-spread > .ef-margin {{
      position: sticky; top: calc(var(--tri-h) + var(--topbar-h)); align-self: start;
      max-height: calc(100vh - var(--tri-h) - var(--topbar-h)); overflow-y: auto; scrollbar-width: thin;
    }}
  }}

  /* 铺满：正文吃掉剩余宽度，右栏贴边 */
  @media (min-width: 960px) {{
    .ef-spread {{
      grid-template-columns: minmax(0, 1fr) clamp(14rem, 16vw, 19rem);
      column-gap: clamp(.75rem, 1vw, 1.25rem);
      max-width: none;
      margin: 0;
    }}
    .ef-spread > .ef-margin {{
      padding: clamp(1.5rem, 3vw, 2.5rem) .75rem clamp(1.5rem, 3vw, 2.5rem) 1.25rem;
    }}
    .ef-spread > .ef-sheet {{
      padding-left: clamp(2rem, 3.5vw, 4rem);
      padding-right: clamp(2rem, 3.5vw, 4rem);
    }}
    /* 正文不再被 40rem 卡住 */
    .ef-sheet .ef-prose,
    .ef-sheet .ef-lede,
    .ef-sheet .ef-read,
    .ef-sheet .ef-facts,
    .ef-sheet .ef-empty,
    .ef-sheet .ef-notice {{ max-width: none; }}
  }}
  .ef-margin .ef-ledger li,
  .ef-margin .toc a {{ font-size: .82rem; }}

  /* 滚动条统一样式在 assets/local-fonts.css 里定义（页面/侧栏/搜索共用） */


  .band {{ display:flex; flex-wrap:wrap; align-items:flex-end; justify-content:space-between;
    gap:1.5rem; padding:clamp(1.5rem,3vw,2.5rem) var(--ef-pad) clamp(1.25rem,2.5vw,2rem);
    border-bottom:1px solid var(--ef-rule); background:var(--ef-panel); }}
  .band-title {{ margin:.2rem 0 .8rem; font-family:var(--ef-font-ui); font-stretch:var(--ef-wider);
    font-weight:800; line-height:.95; letter-spacing:-.01em; font-size:clamp(2rem,4vw,3.4rem); }}
  .band-title .hollow {{ color:transparent; -webkit-text-stroke:1.5px var(--ef-ink); }}
  .band-note {{ max-width:32rem; margin:0; color:var(--ef-ink-2); }}
  .filters {{ padding:1rem var(--ef-pad); border-bottom:1px solid var(--ef-rule); }}
  .chip-row {{ display:flex; flex-wrap:wrap; align-items:center; gap:.4rem; margin-bottom:.5rem; }}
  .chip-row .ef-field {{ width:3rem; flex:none; }}
  .chip {{ font:inherit; font-size:.78rem; line-height:1.6; padding:.15em .7em; cursor:pointer;
    border:1px solid var(--ef-rule); background:var(--ef-panel); color:var(--ef-ink-2); }}
  .chip:hover {{ color:var(--ef-ink); border-color:var(--ef-ink); }}
  .chip.is-on {{ background:var(--ef-signal); border-color:var(--ef-signal); color:var(--ef-on-signal); font-weight:600; }}
  .cols {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(17rem,1fr));
    gap:0; border-top:1px solid var(--ef-rule); }}
  /* 每格自己画右边框：网格的竖线不再依赖"后一张卡片"，末行不满也照常收边，
     筛选隐藏卡片后也不会错位 */
  .col-card {{ display:flex; flex-direction:column; gap:.35rem; padding:1.1rem var(--ef-pad);
    border-right:1px solid var(--ef-rule); border-bottom:1px solid var(--ef-rule);
    text-decoration:none; color:var(--ef-ink);
    transition:background .15s var(--ef-ease); }}
  .col-card:hover {{ background:var(--ef-chip); }}
  .col-card .card-name {{ font-size:1.02rem; font-weight:700; line-height:1.4; }}
  .col-card .card-meta {{ color:var(--ef-ink-2); }}
  .col-card[hidden] {{ display:none; }}
  .recent {{ padding:clamp(1.5rem,3vw,2.5rem) var(--ef-pad) 1rem; }}
  .recent .ef-bar-title {{ margin-bottom:1rem; }}
  .hero {{ --mx:0; --my:0; display:grid;
    grid-template-columns:minmax(0,1fr) minmax(0,40%);
    grid-template-rows:auto 1fr auto auto;
    column-gap:clamp(1.5rem,4vw,3.5rem);
    min-height:min(41rem,calc(100dvh - 3px)); padding-top:1.25rem;
    border-bottom:1px solid var(--ef-rule); overflow:hidden; }}
  .hero > .meta {{ grid-column:1; margin:0; padding-inline:var(--ef-pad); }}
  .hero > .meta > * + *::before {{ content:'/'; margin-inline:.75em; color:var(--ef-rule); }}
  .hero .ef-wordmark {{ grid-column:1; align-self:end; margin-top:2rem; padding-left:var(--ef-pad); }}
  .hero .copy {{ grid-column:1; padding:1.75rem var(--ef-pad) 2.25rem; }}
  .hero .copy p {{ margin:0; }}
  .hero .claim {{ font-size:clamp(1.1rem,2.1vw,1.5rem); }}
  .hero .bio {{ max-width:33rem; margin-top:.9rem !important; color:var(--ef-ink-2); }}
  .hero .ef-actions {{ margin-top:1.5rem; }}
  .hero .ef-frame {{ grid-column:2; grid-row:1 / 4; margin:0 var(--ef-pad) 2.25rem 0; }}
  .hero .ef-frame::before {{ transform:translate(calc(var(--mx) * 12px),calc(var(--my) * 10px)); }}
  .hero .ef-frame svg {{ width:100%; height:100%;
    transform:translate(calc(var(--mx) * -14px),calc(var(--my) * -8px));
    transition:transform .4s var(--ef-ease); }}
  .hero .ef-ticker {{ grid-column:1 / -1; }}
  @media (max-width:899px) {{
    .hero {{ grid-template-columns:minmax(0,1fr); grid-template-rows:none; min-height:0; }}
    .hero .ef-frame {{ grid-column:1; grid-row:auto; height:18rem;
      margin:0 calc(var(--ef-pad) + 1rem) 2.25rem var(--ef-pad); }}
  }}
  @media (max-width:760px) {{ .topbar {{ flex-wrap:wrap; gap:.75rem; }}
    .topbar nav {{ order:3; width:100%; margin-left:0; }} }}
</style>
</head>
<body class="ef ef-contours">
<div class="ef-tri" aria-hidden="true"><i></i><i></i><i></i></div>
<header class="topbar">
  <a class="brand" href="{up}index.html">KYSIIN.ARCHIVE</a>
  <nav class="ef-field" aria-label="主导航">
    <a href="{up}index.html">首页</a>
    <a href="{up}index.html#all" {cur_lib}>资料库</a>
    <a href="{up}index.html#stats">统计</a>
  </nav>
  <span data-search-slot></span>
  <button class="ef-btn small" type="button" data-theme-toggle>切换深浅</button>
</header>
"""

FOOT = """
<footer class="foot">
  <span class="ef-field">KYSIIN.ARCHIVE · {date} · 自动生成</span>
  <span>用 endfield-ui 渲染 · Saira（SIL OFL）自托管</span>
</footer>
<script type="module">
  import {{ wireTheme }} from './{up}assets/fx.js'
  wireTheme()
</script>
<script defer src="{up}assets/search.js?v={ver}"></script>
<script>
  /* 首页筛选：三个维度各自单选，组合生效 */
  (function () {{
    var state = {{ area: '', term: '' }};
    var cards = [].slice.call(document.querySelectorAll('.col-card'));
    var count = document.getElementById('filter-count');
    function apply() {{
      var shown = 0;
      cards.forEach(function (c) {{
        var ok = (!state.area || c.dataset.area === state.area)
              && (!state.term || c.dataset.term === state.term);
        c.hidden = !ok;
        if (ok) shown++;
      }});
      if (count) count.textContent = shown + ' 门课';
    }}
    document.querySelectorAll('.chip').forEach(function (b) {{
      b.addEventListener('click', function () {{
        var dim = b.dataset.dim;
        state[dim] = b.dataset.val;
        document.querySelectorAll('.chip[data-dim="' + dim + '"]').forEach(function (x) {{
          x.classList.toggle('is-on', x === b);
        }});
        apply();
      }});
    }});
  }})();
</script>
<script>
  /* 顶栏高亮：首页有「资料库 / 统计」两个锚点分区，滚到哪一块就点亮哪一项。
     课程页 / 文章页没有这些锚点，保持静态的「资料库」不变。 */
  (function () {{
    var nav = document.querySelector('.topbar nav');
    if (!nav) return;
    var links = [].slice.call(nav.querySelectorAll('a'));
    function target(a) {{
      var h = a.getAttribute('href') || '';
      var i = h.indexOf('#');
      return i < 0 ? null : document.getElementById(h.slice(i + 1));
    }}
    var items = links.map(function (a) {{ return {{ a: a, el: target(a) }}; }});
    if (!items.some(function (t) {{ return t.el; }})) return;
    var home = items.filter(function (t) {{ return !t.el; }})[0];
    function setActive(a) {{
      links.forEach(function (x) {{ x.removeAttribute('aria-current'); }});
      if (a) a.setAttribute('aria-current', 'page');
    }}
    var ticking = false;
    function spy() {{
      ticking = false;
      var line = window.scrollY + 140;
      var current = home ? home.a : null;
      items.forEach(function (t) {{
        if (t.el && t.el.getBoundingClientRect().top + window.scrollY <= line) current = t.a;
      }});
      /* 页面滚到底时最后一块到不了阈值（它下面没有内容了），直接点亮最后一项；
         但整页本来就装得下时不算"滚到底"，仍按位置判断 */
      var doc = document.documentElement;
      if (window.innerHeight + window.scrollY >= doc.scrollHeight - 4
          && doc.scrollHeight > window.innerHeight + 40) {{
        current = items[items.length - 1].a;
      }}
      setActive(current);
    }}
    window.addEventListener('scroll', function () {{
      if (!ticking) {{ ticking = true; requestAnimationFrame(spy); }}
    }}, {{ passive: true }});
    window.addEventListener('resize', spy);
    /* 点了某个分区（页面装得下、不发生滚动的情况）：立刻点亮被点的那一项 */
    window.addEventListener('hashchange', function () {{
      var h = location.hash.slice(1);
      var hit = items.filter(function (t) {{ return t.el && t.el.id === h; }})[0];
      if (hit) setActive(hit.a); else spy();
    }});
    spy();
  }})();
</script>
</body>
</html>
"""

# ------------------------------------------------------------------ course pages
def course_files(co):
    """一门课的全部文件（跨成员分组），返回 (行 HTML, 文件数, 是否有未收录)。"""
    multi = len(co["members"]) > 1
    page_dir = os.path.join(REPO, "collections", co["slug"])
    items = []
    for m in co["members"]:
        for f in m["files"]:
            if f["path"].lower().endswith(".md"):
                continue
            items.append((f, m))
    items.sort(key=lambda pair: pair[0]["path"].lower())

    rows = []
    for i, (f, m) in enumerate(items, 1):
        abs_path = os.path.join(REPO, f["path"])
        href = quote(os.path.relpath(abs_path, page_dir).replace("\\", "/"))
        folder = os.path.dirname(f["path"].split("/", 3)[-1])
        bits = [m["label"], folder] if multi else [folder]
        sub = " / ".join(b for b in bits if b)
        rows.append(
            f'<tr><td class="num">{i}</td><td><a href="{href}">{os.path.basename(f["path"])}</a>'
            f'{" <span class=\"ef-field\">%s</span>" % sub if sub else ""}</td>'
            f'<td>{typ(f["ext"])}</td><td class="num">{human(f["size"])}</td>'
            f'<td class="num">{time.strftime("%Y.%m.%d", time.localtime(f["mtime"]))}</td></tr>')

    if co["external"]:
        for i, f in enumerate(sorted(co["external"], key=lambda f: f["path"].lower()),
                              len(rows) + 1):
            rows.append(
                f'<tr><td class="num">{i}</td><td>{f["path"]}'
                f' <span class="ef-field">未入库</span></td>'
                f'<td>{typ(f["ext"])}</td><td class="num">{human(f["size"])}</td>'
                f'<td class="num">—</td></tr>')
    return "\n".join(rows), len(items)


for idx, co in enumerate(COURSES):
    rows, n_files = course_files(co)
    total_rows = n_files + len(co["external"])
    if total_rows:
        files_block = (
            '<h2 class="ef-group-head ef-read"><span>其他文件</span>'
            '<span class="ef-field">%d 项</span></h2>\n'
            '    <div class="ef-table-wrap">\n      <table class="ef-table">\n'
            '        <thead><tr><th class="num">#</th><th>文件</th><th>类型</th>'
            '<th class="num">大小</th><th class="num">修改</th></tr></thead>\n'
            '        <tbody>\n%s\n        </tbody>\n      </table>\n    </div>'
            % (total_rows, rows))
    else:
        files_block = ""

    # 三门课内分区：章节 / 专题 / 实验
    section_html = []
    for s_name, items in co["sections"]:
        art_rows = []
        for a in items:
            href = os.path.relpath(a["html"], os.path.join(REPO, "collections", co["slug"]))
            href = quote(href.replace("\\", "/"))
            meta = [f'{a["chars"]:,} 字']
            if len(co["members"]) > 1 and a.get("label"):
                meta.insert(0, a["label"])
            art_rows.append(
                f'          <li><a class="ef-record" href="{href}">'
                f'<span class="ef-tag">MD</span>'
                f'<span class="ef-field">{" · ".join(meta)}</span>'
                f'<span class="name ef-read">{a["title"]}</span>'
                f'<span class="ef-field">{a["date"]}</span></a></li>')
        section_html.append(
            f'    <h2 class="ef-group-head ef-read" id="sec-{s_name}"><span>{s_name}</span>'
            f'<span class="ef-field">{len(items)} 篇</span></h2>\n'
            '      <ol class="ef-records">\n' + "\n".join(art_rows) + '\n      </ol>')

    if not section_html:
        section_html.append('    <p class="ef-empty">这门课还没有可阅读的文章，先看下面的文件表。</p>')
    arts_html = "\n".join(section_html)

    # 侧栏：分区 → 文件类型
    sec_ledger = "\n".join(
        f'        <li><span>{s}</span><span class="ef-field">{len(items)} 篇</span></li>'
        for s, items in co["sections"]) or '        <li><span class="ef-field">暂无文章</span></li>'
    counts = {}
    for f in (co["files"] or co["external"]):
        counts[typ(f["ext"])] = counts.get(typ(f["ext"]), 0) + 1
    type_ledger = "\n".join(f'        <li><span>{k}</span><span class="ef-field">{v}</span></li>'
                            for k, v in sorted(counts.items(), key=lambda kv: -kv[1]))

    up = "../../"
    prev_c = COURSES[idx - 1] if idx > 0 else None
    next_c = COURSES[idx + 1] if idx + 1 < len(COURSES) else None
    nav = []
    if prev_c:
        nav.append(f'<a class="ef-btn" href="../{prev_c["slug"]}/index.html">← {prev_c["name"]}</a>')
    if next_c:
        nav.append(f'<a class="ef-btn" href="../{next_c["slug"]}/index.html">{next_c["name"]} →</a>')
    notice = ""
    if co["external"]:
        notice = ('<p class="ef-notice" data-flag="未收录">有 %d 个产出文件体积较大，暂未放入仓库，'
                  '只在文件表里登记；需要时另行提供。</p>' % len(co["external"]))
    body = HEAD.format(title=f'{co["name"]} · KYSIIN.ARCHIVE', desc=co["desc"], up=up,
                       cur_lib='aria-current="page"') + f"""
<article class="ef-spread">
  <div class="ef-sheet">
    <p class="ef-eyebrow slash">Course / Index</p>
    <p class="ef-crumb ef-field"><a href="{up}index.html">首页</a><span>{co['area'] or '课程'}</span><span>{co['name']}</span></p>
    <ul class="ef-facts ef-field">
      <li>{len(co['articles'])} 篇文章</li>
      <li>{co['n_files']} 文件</li>
      <li>{co['mb']:.1f} MB</li>
      <li>最近 {co['latest']}</li>
    </ul>
    <h1 class="title ef-read">{co['name']}</h1>
    <div class="ef-tri" aria-hidden="true"><i></i><i></i><i></i></div>
    <p class="ef-lede ef-read">{co['desc']}</p>
    {notice}
{arts_html}
    {files_block}
    <p class="ef-actions back">{" ".join(nav)} <a class="ef-btn" href="{up}index.html#all">返回资料库</a></p>
  </div>
  <aside class="ef-margin" aria-label="分区与类型">
    <h2 class="ef-field" style="margin:0 0 .75rem">按分区</h2>
    <ul class="ef-ledger">
{sec_ledger}
    </ul>
    <h2 class="ef-field" style="margin:1.25rem 0 .75rem">按类型</h2>
    <ul class="ef-ledger">
{type_ledger}
    </ul>
  </aside>
</article>
""" + FOOT.format(date=BUILD_DATE, up=up, ver=BUILD_VER)
    os.makedirs(os.path.join(REPO, "collections", co["slug"]), exist_ok=True)
    io.open(os.path.join(REPO, "collections", co["slug"], "index.html"), "w",
            encoding="utf-8", newline="\n").write(body)

# 成员分组不再单独出索引页：文件与文章都已经挂到所属课程页上，
# 留着只会出现两份同样的目录（旧的 collections/<成员>/index.html 不再生成）

# ------------------------------------------------------------------ homepage
# ---- 搜索索引 ----
# 匹配优先级（前端 search.js 里按字段加权）：分组（课程/实验）> 实验编号 > 标题 > 正文
LAB_RE = re.compile(r"(?i)\b(lab\s*\d+|实验\s*\d+|project\s*\d+|w\d{1,2}|hw\s*\d+)")


def lab_of(title, rel):
    m = LAB_RE.search(title) or LAB_RE.search(rel)
    if m:
        return re.sub(r"\s+", "", m.group(1)).upper()
    if "实验" in title:
        return "实验"
    return ""


def _plain(path, cap=12000):
    """正文纯文本：去掉 Markdown 标记，供搜索用。"""
    try:
        t = io.open(path, encoding="utf-8-sig", errors="replace").read()
    except OSError:
        return ""
    t = re.sub(r"^---[\s\S]*?---", "", t)
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", t)
    t = re.sub(r"[#>*`|_\[\]()!{}]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t[:cap]


SEARCH = []
for co in COURSES:
    SEARCH.append(dict(k="course", t=co["name"], c=co["area"], g="课程",
                       a=co.get("area", ""), r=co.get("term", ""),
                       n=len(co["articles"]),
                       u="collections/%s/index.html" % co["slug"], x=co.get("desc", "")))
    for a in co["articles"]:
        files_root = os.path.join(REPO, "collections", a["coll"], "files")
        rel_md = os.path.relpath(a["path"], files_root).replace(os.sep, "/")
        SEARCH.append(dict(k="article", t=a["title"], c=co["name"], s=a.get("section", ""),
                           l=lab_of(a["title"], rel_md),
                           u=os.path.relpath(a["html"], REPO).replace(os.sep, "/"),
                           b=_plain(a["path"])))
io.open(os.path.join(REPO, "assets", "search.json"), "w", encoding="utf-8").write(
    json.dumps(SEARCH, ensure_ascii=False))


def card(co):
    """首页卡片：一门课一张，按分区报数量（体积放同一行，日期交给「最近更新」）。"""
    bits = [co.get("area", ""), co.get("term", "")]
    n = len(co["articles"])
    if co.get("external_only"):
        count = f'{co["out"]["n"]} 文件'
        size = "未收录"
    elif n:
        counts = {s: len(items) for s, items in co["sections"]}
        count = " · ".join(f"{counts[s]} {s}" for s in SECTION_ORDER if counts.get(s))
        size = ("%.1f MB" % co["mb"]) if co["mb"] else "—"
    else:
        count = f'{co["n_files"]} 文件'
        size = ("%.1f MB" % co["mb"]) if co["mb"] else "—"
    return (
      '<a class="col-card" href="collections/{slug}/index.html" data-area="{area}" data-term="{term}">'
      '<span class="card-top ef-field">{bits}</span>'
      '<span class="card-name">{name}</span>'
      '<span class="card-meta ef-field">{count} · {size}</span>'
      '</a>'
    ).format(slug=co["slug"], area=co.get("area", ""), term=co.get("term", ""),
             bits=" · ".join([b for b in bits if b]),
             name=co["name"], count=count, size=size)


CARDS = "\n".join(card(co) for co in COURSES)

RECENT = []
_pool = []
for co in COURSES:
    for a in co["articles"]:
        _pool.append((a["date"], co["name"], a["title"], a["html"], a.get("chars", 0)))
_pool.sort(reverse=True)
for date, cname, title, html_path, chars in _pool[:8]:
    rel_href = html_path.replace(os.sep, "/")
    RECENT.append('          <li><a class="ef-record" href="{h}">'
                  '<span class="ef-tag">{d}</span>'
                  '<span class="ef-field">{c}</span>'
                  '<span class="name ef-read">{t}</span>'
                  '<span class="ef-field">{n:,} 字</span></a></li>'
                  .format(h=rel_href, d=short_date(date), c=cname,
                          t=title, n=chars))
RECENT_HTML = "\n".join(RECENT)

CHIPS = ""
for dim, label, values in (("area", "方向", META_AREAS),
                           ("term", "学期", META_TERMS)):
    opts = ['<button type="button" class="chip is-on" data-dim="%s" data-val="">全部</button>' % dim]
    opts += ['<button type="button" class="chip" data-dim="%s" data-val="%s">%s</button>' % (dim, v, v)
             for v in values]
    CHIPS += ('    <div class="chip-row">\n      <span class="ef-field">%s</span>\n      %s\n    </div>\n'
              % (label, "\n      ".join(opts)))


home = HEAD.format(title="KYSIIN.ARCHIVE · 全部资料", desc="个人资料仓库：课程笔记、专题复习、代码实验。",
                   up="", cur_lib="") + f"""
<section class="band">
  <div>
    <p class="ef-eyebrow slash">Archive</p>
    <h1 class="band-title">KYSIIN<span class="hollow">.ARCHIVE</span></h1>
    <ul class="ef-facts ef-field">
      <li>{len(COURSES)} 门课</li>
      <li>{total_articles} 篇文章</li>
      <li>{in_files} 个文件</li>
      <li>{in_mb:.1f} MB</li>
      <li>最近更新 {latest}</li>
    </ul>
  </div>
  <p class="band-note ef-read">一门课一个入口，课内再分章节 / 专题 / 实验。下面可以按方向、学期筛，或者直接搜索。</p>
</section>

<section class="filters" aria-label="筛选">
{CHIPS}    <p class="ef-field" id="filter-count" style="margin:.6rem 0 0">{len(COURSES)} 门课</p>
</section>

<section class="cols" id="all">
{CARDS}
</section>

<section class="recent" id="recent">
  <h2 class="ef-bar-title">最近更新</h2>
  <ol class="ef-records">
{RECENT_HTML}
  </ol>
</section>

<section class="index" id="stats" style="padding:1rem var(--ef-pad) 3rem">
  <h2 class="ef-bar-title">统计</h2>
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr));gap:0 clamp(2rem,5vw,4rem)">
    <div>
      <h2 class="ef-field" style="margin:0 0 .75rem">按分区</h2>
      <ul class="ef-ledger">
        <li><span>章节</span><span class="ef-field">{section_totals["章节"]} 篇</span></li>
        <li><span>专题</span><span class="ef-field">{section_totals["专题"]} 篇</span></li>
        <li><span>实验</span><span class="ef-field">{section_totals["实验"]} 篇</span></li>
      </ul>
    </div>
    <div>
      <h2 class="ef-field" style="margin:0 0 .75rem">体量</h2>
      <ul class="ef-ledger">
        <li><span>入库文件</span><span class="ef-field">{in_files}</span></li>
        <li><span>入库体积</span><span class="ef-field">{in_mb:.1f} MB</span></li>
        <li><span>未收录</span><span class="ef-field">{out_files} 文件 · {out_mb:.0f} MB</span></li>
      </ul>
    </div>
    <div>
      <h2 class="ef-field" style="margin:0 0 .75rem">阅读</h2>
      <ul class="ef-ledger">
        <li><span>课程</span><span class="ef-field">{len(COURSES)} 门</span></li>
        <li><span>文章</span><span class="ef-field">{total_articles} 篇</span></li>
        <li><span>搜索</span><span class="ef-field">⌘K / Ctrl+K</span></li>
      </ul>
    </div>
  </div>
</section>
""" + FOOT.format(date=BUILD_DATE, up="", ver=BUILD_VER)

io.open(os.path.join(REPO, "index.html"), "w", encoding="utf-8", newline="\n").write(home)

# ------------------------------------------------------------------ .gitignore & README
# GitHub Pages 默认会先跑一遍 Jekyll：它会跳过下划线开头的路径，构建也慢。
# 放一个空的 .nojekyll 表示「原样发布」。
io.open(os.path.join(REPO, ".nojekyll"), "w", encoding="utf-8", newline="\n").write("")

io.open(os.path.join(REPO, ".gitignore"), "w", encoding="utf-8", newline="\n").write("""# 兜底：压缩包在构建时就不拷进站（里面多是作业源码），这里再挡一层
*.zip

# 大体积二进制与构建输出（ClothLab 产出只登记、不入库）
bin/
report/
sample.doc

# 来源记录：本地保留，不进公开仓库
tools/sources.local.json

# 系统与工具噪音
.DS_Store
Thumbs.db
node_modules/
__pycache__/
.vitepress/cache/
.vitepress/dist/
*.log
""")

io.open(os.path.join(REPO, "README.md"), "w", encoding="utf-8", newline="\n").write(f"""# KYSIIN.ARCHIVE

个人资料仓库：一门课一个入口，课内再分 **章节 / 专题 / 实验**。首页是课程索引（`index.html`），
每门课有自己的索引页，按分区列出文章，并附完整文件表（名称、类型、体积、修改时间）。

## 结构

```
index.html                 首页（课程索引）
collections/<课程>/index.html   每门课一个索引页（含 章节 / 专题 / 实验 三个分区）
collections/<课程>/files/       这门课的文件与文章
assets/                    endfield-ui 套件与自托管字体
files/                     单独提供的下载件（动画 PDF / DOCX）
```

## 收录范围

课程资料按课程归档在 `collections/` 下；一门课可以由多份来源合成（例如「计算机动画」
= 复习资料 + ClothLab 源码/产出），页面由构建脚本聚合，物理目录保持分开。

**不发布**：课程作业的源码（.cpp / .h / .cc / .hh / .sh）与所有压缩包只在本地保留，
站上只放报告、笔记与 PDF；ClothLab 是自制项目，源码照常发布。

**未收录**（约 {out_mb:.0f} MB）：部分实验产出文件体积较大，未放入仓库，
只在所属课程页的文件表里登记。

## 本地查看

请用一个静态服务器打开，不要直接双击 `index.html`：页面用的是 ES module 与
`fetch('assets/search.json')`，在 `file://` 下会被浏览器拦掉，主题切换和搜索会失效。

```bash
python -m http.server 8000
# 打开 http://127.0.0.1:8000/
```

## 发布到 GitHub Pages

1. 新建仓库，把本目录推上去（`git init && git add . && git commit -m "init"`）；
2. Settings → Pages → Source 选 `Deploy from a branch`，分支 `main`、目录 `/ (root)`；
3. 稍等片刻，访问 `https://<用户名>.github.io/<仓库名>/`。

仓库根的 `.nojekyll` 让 Pages 原样发布，不走 Jekyll（否则下划线开头的路径会被吞掉）。

## 更新索引

本站不是手改的，而是由上一层工作区里的 `tools/build_site.py` 生成的；`tools/` 下这几份
脚本只是随站点一起发布的副本，仅供查看，不要在 `site/` 里运行它们。要更新，回到工作区根目录：

```bash
python tools/build_site.py
```

它会清空并重建整个 `site/`（首页、各课程索引页、文章页都在内），`site/` 里的手工改动不会保留。

统计：{len(COURSES)} 门课 · {in_files} 个文件入库 · {in_mb:.1f} MB · 另有 {out_files} 个文件未入库。
""")

os.makedirs(os.path.join(REPO, "tools"), exist_ok=True)
with io.open(os.path.join(REPO, "tools", "sources.local.json"), "w", encoding="utf-8") as fh:
    fh.write(json.dumps(dict(
        note="本地记录，不进仓库、不显示在网站上",
        generated=time.strftime("%Y-%m-%d %H:%M"),
        collections=[dict(slug=c["slug"], name=c["name"], source=c["src"],
                          paths=[p for p, _ in c.get("copies", [])]) for c in COLLECTIONS],
        uncollected=[dict(slug=c["slug"], source=c["src"],
                          paths=c.get("_external_src", [])) for c in COLLECTIONS],
    ), ensure_ascii=False, indent=2))
shutil.copy2(os.path.abspath(__file__), os.path.join(REPO, "tools", "build_site.py"))
shutil.copy2(os.path.join(HOME, "render_md.py"), os.path.join(REPO, "tools", "render_md.py"))
shutil.copy2(os.path.join(HOME, "publish.py"), os.path.join(REPO, "tools", "publish.py"))
shutil.copy2(os.path.join(HOME, "render_math.mjs"), os.path.join(REPO, "tools", "render_math.mjs"))
# 数据文件一起带上，发布出去的副本才是完整的一套
for _name in ("sections.json", "collections.json"):
    shutil.copy2(os.path.join(HOME, _name), os.path.join(REPO, "tools", _name))
# 发布出去的工具副本里不要留下本机账号路径（必须在拷完之后再洗）
for _fn in ("build_site.py", "render_md.py", "publish.py", "render_math.mjs"):
    publish.scrub_file(os.path.join(REPO, "tools", _fn))

print(json.dumps(dict(repo=REPO, courses=len(COURSES), collections=len(COLLECTIONS),
                      in_files=in_files, in_mb=round(in_mb, 1),
                      out_files=out_files, out_mb=round(out_mb, 1),
                      latest=latest), ensure_ascii=False, indent=2))
for co in COURSES:
    s = " · ".join(f'{name} {len(items)}' for name, items in co["sections"]) or "无文章"
    print(f'{co["name"][:22]:24} 入库 {co["n_files"]:4} / {co["mb"]:7.1f} MB   '
          f'未入库 {co["out"]["n"]:3}   {s}')











