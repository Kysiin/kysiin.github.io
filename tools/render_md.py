# -*- coding: utf-8 -*-
"""Render every Markdown file in the repo into a readable page (MathJax pre-rendered to SVG)."""
import os, io, re, time, html, shutil, hashlib, json, subprocess, itertools
from urllib.parse import quote

import markdown
import publish
from markdown.extensions.toc import slugify_unicode

CJK = re.compile(r"[\u4e00-\u9fff]")
WORD = re.compile(r"[A-Za-z0-9]+")
BUILD_DATE = time.strftime("%Y.%m.%d")

HERE = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.dirname(HERE)
NODE = shutil.which("node") or r"C:\Users\***\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin\node.exe"
MATHJAX_ROOT = os.path.join(WORKSPACE, "vendor", "node_modules", "mathjax-full")
MATH_SCRIPT = os.path.join(HERE, "render_math.mjs")
# 与 build_site.py 用同一个时间戳粒度；搜索脚本靠它刷新浏览器缓存
BUILD_VER = time.strftime("%Y%m%d%H%M")


def rel(target, start):
    return os.path.relpath(target, start).replace("\\", "/")


SECTIONS_PATH = os.path.join(HERE, "sections.json")


def load_sections():
    """读 sections.json，返回 (分区顺序, section_of(slug, rel_path))。

    一门课内的文章按 章节 / 专题 / 实验 分区；每篇的分区在 sections.json 的
    ``articles`` 里登记，没登记的按 ``fallback`` 规则猜（新文件不必先登记）。
    """
    default_order = ["章节", "专题", "实验"]
    try:
        data = json.load(io.open(SECTIONS_PATH, encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print("  ! sections.json 缺失或损坏，全部归入章节：%s" % exc)
        data = {}
    order = list(data.get("sections") or default_order)
    rules = [(re.compile(pat, re.I), name) for pat, name in (data.get("fallback") or [])]
    table = data.get("articles") or {}

    def section_of(slug, rel_path):
        got = (table.get(slug) or {}).get(rel_path)
        if got:
            return got
        for rx, name in rules:
            if rx.search(rel_path):
                return name
        return order[0] if order else "章节"

    return order, section_of


def strip_frontmatter(text):
    if text.startswith("---"):
        m = re.match(r"^---\s*\n.*?\n---\s*\n", text, flags=re.S)
        if m:
            return text[m.end():]
    return text


# ----------------------------------------------------------------- math
MATH_RE = re.compile(
    r"\$\$([\s\S]+?)\$\$"          # $$ ... $$
    r"|\\\[([\s\S]+?)\\\]"        # \[ ... \]
    r"|(?<!\$)\$(?!\$)([^\n$]+?)\$(?!\$)"   # $ ... $
    r"|\\\(([\s\S]+?)\\\)"       # \( ... \)
)
CODE_RE = re.compile(r"(```[\s\S]*?```|~~~[\s\S]*?~~~|`[^`\n]+`)")


def extract_math(text, counter):
    """Replace math with tokens; return (text, [(token, tex, display)])."""
    parts = CODE_RE.split(text)
    items = []
    out = []
    for i, part in enumerate(parts):
        if i % 2 == 1:  # code span/block: leave untouched
            out.append(part)
            continue

        def repl(m):
            if m.group(1) is not None:
                tex, display = m.group(1), True
            elif m.group(2) is not None:
                tex, display = m.group(2), True
            elif m.group(3) is not None:
                tex, display = m.group(3), False
            else:
                tex, display = m.group(4), False
            tex = tex.strip()
            if not tex:
                return m.group(0)
            tid = "EFMATH%05d" % next(counter)
            items.append((tid, tex, display))
            return "@@%s@@" % tid

        out.append(MATH_RE.sub(repl, part))
    return "".join(out), items


def render_math(items):
    """One Node call for the whole build."""
    if not items or not os.path.isfile(MATH_SCRIPT) or not os.path.isdir(MATHJAX_ROOT):
        return {}, ""
    payload = {"items": [{"id": t, "tex": tex, "display": d} for t, tex, d in items]}
    env = dict(os.environ, MATHJAX_ROOT=MATHJAX_ROOT)
    try:
        proc = subprocess.run([NODE, MATH_SCRIPT], input=json.dumps(payload).encode("utf-8"),
                              capture_output=True, env=env, timeout=600)
    except Exception as e:
        print("  ! mathjax failed:", e)
        return {}, ""
    if proc.returncode != 0:
        print("  ! mathjax exit", proc.returncode, proc.stderr.decode("utf-8", "replace")[:300])
        return {}, ""
    try:
        data = json.loads(proc.stdout.decode("utf-8"))
    except Exception as e:
        print("  ! mathjax output unreadable:", e)
        return {}, ""
    css = data.pop("__css__", "")
    return data, css


def substitute_math(html_text, rendered, display_map):
    for tid, svg in rendered.items():
        if display_map.get(tid):
            block = '<div class="eq">%s</div>' % svg
            html_text = html_text.replace("<p>@@%s@@</p>" % tid, block)
        html_text = html_text.replace("@@%s@@" % tid, svg)
    return html_text


def tex_plain(text, tex_map):
    """Replace math tokens with their TeX source — for places that must stay text.

    The right-hand table of contents, page titles and sidebar labels are escaped
    text, so they cannot hold an <mjx-container>; without this they would print
    the raw ``@@EFMATH00001@@`` token.
    """
    for tid, tex in (tex_map or {}).items():
        text = text.replace("@@%s@@" % tid, tex)
    return text


def demote_headings(text):
    """Turn ``#`` headings left in the body into ``##``.

    The first H1 becomes the page title, so any further H1 would give the page
    two top-level headings and keep those sections out of the TOC (depth 2-3).
    Code blocks are left alone.
    """
    parts = CODE_RE.split(text)
    for i in range(0, len(parts), 2):
        parts[i] = re.sub(r"^#(?=\s)", "##", parts[i], flags=re.M)
    return "".join(parts)


# ----------------------------------------------------------------- obsidian syntax
def preprocess(text, base_dir, repo, index):
    out = []
    lines = text.split("\n")
    i = 0
    in_callout = False
    while i < len(lines):
        ln = lines[i]
        m = re.match(r"^:::\s*(\w+)?\s*(.*)$", ln.strip())
        if m:
            label = (m.group(2) or m.group(1) or "").strip()
            if m.group(1) in ("details", "tip", "warning", "danger", "info"):
                out.append("")
                out.append(f"> **{label}**" if label else "")
                in_callout = True
                i += 1
                continue
            if ln.strip() == ":::":
                in_callout = False
                out.append("")
                i += 1
                continue
        if in_callout and ln.strip():
            out.append("> " + ln)
            i += 1
            continue
        out.append(ln)
        i += 1

    text = "\n".join(out)
    text = re.sub(r"%%.*?%%", "", text, flags=re.S)

    def embed(m):
        target = m.group(1).split("|")[0].strip()
        if re.search(r"\.(png|jpe?g|gif|svg|webp)$", target, re.I):
            hit = index.resolve(target, base_dir, repo)
            return f"![]({hit})" if hit else f"`{target}`"
        hit = index.resolve(target, base_dir, repo)
        if hit:
            return f"[{os.path.splitext(os.path.basename(target))[0]}]({hit})"
        return f"`{target}`"
    text = re.sub(r"!\[\[([^\]]+)\]\]", embed, text)

    def wikilink(m):
        raw = m.group(1)
        target, _, alias = raw.partition("|")
        target = target.strip()
        if target.startswith("#"):
            # Obsidian 的「本页标题」链接：[[#任务 1]] → 页内锚点。
            # 不能只丢掉 #，否则 "##任务 1" 会被当成标题吃掉这一段。
            head = target[1:].strip()
            if not head:
                return ""
            label = (alias or head).strip()
            return "[%s](#%s)" % (label, slugify_unicode(head, "-"))
        label = (alias or os.path.splitext(os.path.basename(target))[0]).strip()
        hit = index.resolve(target, base_dir, repo)
        if not hit:
            return label
        if hit.lower().endswith(".md"):
            return f"[{label}]({os.path.splitext(hit)[0]}.html)"
        return f"[{label}]({hit})"
    text = re.sub(r"\[\[([^\]]+)\]\]", wikilink, text)
    return text


ASSET_DIR = "_assets"


def localize_image(value, page_dir, repo, slug, index=None):
    v = value.strip().strip('"').strip("'")
    if v.startswith("file://"):
        v = v[7:]
    is_abs = bool(re.match(r"^[A-Za-z]:[\\/]", v)) or v.startswith("\\\\")
    if not is_abs:
        return v
    if not os.path.isfile(v):
        # 另一台机器上的绝对路径：先看同目录有没有同名文件，再按文件名在仓库里找
        base = os.path.basename(v.replace("\\", "/"))
        same = os.path.join(page_dir, base)
        if os.path.isfile(same):
            return rel(same, page_dir)
        if index is not None:
            hit = index.resolve(base, page_dir, repo)
            if hit:
                return rel(os.path.join(repo, hit), page_dir)
        return None
    base = os.path.basename(v).replace("\\", "_")
    tag = hashlib.sha1(v.encode("utf-8")).hexdigest()[:8]
    dest_dir = os.path.join(repo, "collections", slug, "files", ASSET_DIR)
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, "%s-%s" % (tag, base))
    if not os.path.exists(dest):
        try:
            shutil.copy2(v, dest)
            os.chmod(dest, 0o666)
        except OSError:
            return None
    return rel(dest, page_dir)


def localize_images(text, page_dir, repo, slug, index=None):
    def md_img(m):
        alt, src = m.group(1), m.group(2).strip()
        new = localize_image(src, page_dir, repo, slug, index)
        if new is None:
            return "**［图片缺失］**"
        return "![%s](%s)" % (alt, new)

    def html_img(m):
        whole, src = m.group(0), m.group(1)
        new = localize_image(src, page_dir, repo, slug, index)
        if new is None:
            return '<span class="ef-field">［图片缺失］</span>'
        return whole.replace(src, new)

    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", md_img, text)
    text = re.sub(r'<img[^>]+src="([^"]+)"[^>]*>', html_img, text)
    missing = text.count("［图片缺失］")
    return text, missing


class Index:
    """Resolve wikilink targets: same folder, then anywhere in the repo."""

    def __init__(self, repo):
        self.repo = repo
        self.by_name = {}
        self.by_rel = {}
        for dirpath, dirnames, filenames in os.walk(repo):
            dirnames[:] = [d for d in dirnames if d not in {"assets", "tools", ".git"}]
            for fn in filenames:
                p = os.path.join(dirpath, fn)
                r = rel(p, repo)
                self.by_rel[r.lower()] = r
                self.by_name.setdefault(fn.lower(), []).append(r)

    def resolve(self, target, base_dir, repo):
        t = target.replace("\\", "/").strip()
        cand = os.path.normpath(os.path.join(base_dir, t))
        if os.path.isfile(cand):
            return rel(cand, repo)
        if t.lower() in self.by_rel:
            return self.by_rel[t.lower()]
        name = os.path.basename(t).lower()
        for ext in ("", ".md"):
            if name + ext in self.by_name:
                return self.by_name[name + ext][0]
        return None


ARTICLE_CSS = """
  .title { margin:1.5rem 0 1rem; font-size:clamp(var(--ef-t-title),5vw,var(--ef-t-h1));
    font-weight:700; line-height:1.3; }
  .ef-prose { margin-top:1.75rem; }
  .ef-prose img { max-width:100%; height:auto; border:1px solid var(--ef-rule); background:#fff; }
  .ef-prose table { width:100%; border-collapse:collapse; font-size:.9rem; }
  .ef-prose th, .ef-prose td { border-bottom:1px solid var(--ef-rule); padding:.45rem .6rem; text-align:left; }
  .ef-prose th { font-family:var(--ef-font-ui); font-stretch:var(--ef-wide); font-size:.8rem; }
  /* 代码块：整块一个背景；块内的 code 不再带行内边框/内边距 */
  .ef-prose pre { overflow:auto; margin:1rem 0; padding:.9rem 1rem;
    background:var(--ef-chip); border-left:3px solid var(--ef-rule);
    font-size:.85rem; line-height:1.6; tab-size:4; }
  .ef-prose pre code { display:block; padding:0; border:0; background:none;
    font-family:var(--ef-font-mono); font-size:.85rem; line-height:1.6; white-space:pre; }
  .ef-prose :not(pre) > code { font-family:var(--ef-font-mono); font-size:.88em;
    padding:.1em .35em; border:1px solid var(--ef-rule); background:var(--ef-paper); }
  .ef-prose blockquote { border-left:3px solid var(--ef-ink); margin:1rem 0; padding:.25rem 0 .25rem 1rem;
    color:var(--ef-ink-2); }

  /* —— 公式：绝不超出正文栏；行间公式可横向滚动 —— */
  .ef-prose mjx-container { max-width:100%; }
  .ef-prose mjx-container[display="true"] { display:block; text-align:center; margin:1.1em 0;
    max-width:100%; overflow-x:auto; overflow-y:hidden; padding:2px 0; }
  .ef-prose mjx-container[jax="CHTML"] { font-size:1.02em; }
  .eq { overflow-x:auto; overflow-y:hidden; max-width:100%; padding:2px 0; }
  .eq mjx-container[display="true"] { margin:.35em 0; }

  .toc ol { margin:0; padding:0; list-style:none; border-left:1px solid var(--ef-rule); }
  .toc a { display:block; margin-left:-1px; padding:.22rem 0 .22rem .7rem;
    border-left:3px solid transparent; color:var(--ef-ink-2); font-size:.85rem;
    overflow-wrap:anywhere; }
  .toc a:hover { color:var(--ef-ink); border-left-color:var(--ef-trace); }
  .toc .lvl3 { padding-left:1.3rem; font-size:.8rem; }
  .back { margin:2rem 0 0; display:flex; flex-wrap:wrap; gap:.75rem; }

  /* —— 三栏铺满：两侧栏贴边，中间正文吃掉所有剩余宽度 —— */
  .ef-spread { max-width: none; margin: 0; }

  @media (min-width: 1180px) {
    .ef-spread.has-rail {
      grid-template-columns: clamp(11rem, 12vw, 14rem) minmax(0, 1fr) clamp(13rem, 14vw, 17rem);
      column-gap: clamp(.75rem, 1vw, 1.25rem);
    }
  }
  @media (min-width: 960px) and (max-width: 1179px) {
    .ef-spread.has-rail {
      grid-template-columns: clamp(10rem, 12vw, 12rem) minmax(0, 1fr);
      column-gap: clamp(.75rem, 1vw, 1.25rem);
    }
    .ef-spread.has-rail > .toc-aside { display: none; }
  }
  @media (min-width: 960px) {
    .ef-spread > .ef-margin {
      position: sticky;
      top: calc(var(--tri-h) + var(--topbar-h));
      align-self: start;
      max-height: calc(100vh - var(--tri-h) - var(--topbar-h));
      overflow-y: auto;
      scrollbar-width: thin;
      padding: clamp(1.5rem, 3vw, 2.5rem) 1rem;
    }
    /* 两侧栏往屏幕边缘靠，别在页边留空 */
    .ef-spread > .rail-aside { padding-left: .75rem; padding-right: 1.25rem; }
    .ef-spread > .toc-aside { padding-left: 1.25rem; padding-right: .75rem; }
    /* 正文左右留呼吸，但不限制宽度 */
    .ef-spread > .ef-sheet { padding-left: clamp(2rem, 3.5vw, 4rem); padding-right: clamp(2rem, 3.5vw, 4rem); }
    /* 套件把正文限制在 40rem；中间栏变宽后这里放开，让文字铺满 */
    .ef-sheet .ef-prose,
    .ef-sheet .ef-lede,
    .ef-sheet .title,
    .ef-sheet .ef-read,
    .ef-sheet .ef-facts,
    .ef-sheet .ef-empty,
    .ef-sheet .ef-notice { max-width: none; }
  }
  .ef-margin .toc a { font-size: .74rem; line-height: 1.5; }
  .toc a[aria-current] { color: var(--ef-ink); border-left-color: var(--ef-trace); font-weight: 600; }
  .rail-head { display: block; margin: 0 0 .5rem; padding-bottom: .35rem;
    border-bottom: 1px solid var(--ef-rule); font-size: .68rem; line-height: 1.5; }
  .rail-head span { display: inline; }
  .rail-head span + span { display: block; color: var(--ef-ink-2); }
  .rail-aside .toc a { padding-top: .3rem; padding-bottom: .3rem; }
  .rail-tree { list-style:none; margin:0; padding:0; }
  .rail-tree .tree-name { display:block; padding:.35rem .2rem .35rem .6rem;
    border-left:3px solid transparent; font-size:.76rem; font-weight:600; color:var(--ef-ink); }
  .rail-tree .tree-label { display:inline; }
  .rail-tree .tree-name .ef-field { font-size:.68rem; color:var(--ef-ink-2); margin-left:.35rem;
    white-space:nowrap; }
  .rail-tree .tree-group.is-open > .tree-name { border-left-color:var(--ef-trace); }
  .rail-tree .tree-items { list-style:none; margin:.1rem 0 .5rem; padding:0 0 0 .6rem;
    border-left:1px solid var(--ef-rule); }
  .rail-tree .tree-items a { padding-left:.6rem; font-size:.72rem; line-height:1.45; }
  .tree-row { display:flex; align-items:stretch; gap:.15rem; }
  .tree-row .tree-name { flex:1 1 auto; min-width:0; }
  .tree-toggle { flex:none; width:1.55rem; min-height:1.9rem; display:grid; place-items:center;
    padding:0; border:1px solid var(--ef-rule); background:var(--ef-panel); color:var(--ef-ink-2);
    cursor:pointer; transition:color .12s var(--ef-ease), border-color .12s var(--ef-ease), background .12s var(--ef-ease); }
  .tree-toggle:hover { color:var(--ef-ink); border-color:var(--ef-ink); background:var(--ef-chip); }
  .tree-toggle svg { width:.7rem; height:.7rem; transition:transform .15s var(--ef-ease); }
  .tree-toggle[aria-expanded="true"] svg { transform:rotate(90deg); }
  .rail-tree .tree-items[hidden] { display:none; }
  /* 滚动条统一样式在 assets/local-fonts.css 里定义（页面/侧栏/搜索共用） */

  /* 窄屏：正文优先，两侧栏排到后面 */
  @media (max-width: 959px) {
    .ef-spread.has-rail > .ef-sheet { order: 1; }
    .ef-spread.has-rail > .rail-aside { order: 2; border-top: 1px solid var(--ef-rule); }
    .ef-spread.has-rail > .toc-aside { order: 3; }
  }

  /* —— 复习笔记：PDF 下载 —— */
  .pdf-dl { display:flex; flex-wrap:wrap; align-items:center; gap:.75rem; margin:1.1rem 0 0; }
  .pdf-dl .ef-btn { border-color:var(--ef-ink); }

  /* —— 打印 / 导出 PDF：只留正文 —— */
  @page { size:A4; margin:16mm 14mm 18mm; }
  @media print {
    html, body { background:#fff !important; }
    .topbar, .foot, .ef-tri, .rail-aside, .toc-aside, .back, .pdf-dl,
    .ef-crumb, .ef-eyebrow, .ef-facts, .ef-notice { display:none !important; }
    .ef-spread, .ef-spread.has-rail { display:block !important; max-width:none !important; }
    .ef-sheet { border:0 !important; padding:0 !important; background:#fff !important; }
    .ef-sheet .ef-prose, .ef-sheet .ef-lede, .ef-sheet .title { max-width:none !important; }
    .title { margin:0 0 1rem; }
    /* 打印用系统字体：体积小、离线打开不依赖自托管字体 */
    body, .ef-prose, .title, .ef-lede, .ef-facts,
    h1, h2, h3, h4, h5, h6 { font-family:"Microsoft YaHei UI","Microsoft YaHei","PingFang SC",sans-serif !important; }
    .ef-prose pre, .ef-prose code { font-family:Consolas,"Cascadia Mono",monospace !important; }
    .ef-prose { margin-top:1rem; }
    .ef-prose pre { white-space:pre-wrap; word-break:break-word; }
    .ef-prose pre code { white-space:pre-wrap; }
    .ef-prose img, .ef-prose svg, mjx-container { max-width:100% !important; }
    a { color:inherit !important; text-decoration:none !important; }
    .ef-prose h2, .ef-prose h3 { break-after:avoid; }
    .ef-prose pre, .ef-prose table, .eq { break-inside:avoid; }
  }
"""

HEAD = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{title} · KYSIIN.ARCHIVE</title>
<script src="{up}assets/variant.js"></script>
<link rel="stylesheet" href="{up}assets/local-fonts.css" />
<link rel="stylesheet" href="{up}assets/endfield.css" />
{math_link}
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
  .topbar nav a {{ text-decoration:none; color:var(--ef-ink-2); }}
  .foot {{ display:flex; flex-wrap:wrap; align-items:baseline; justify-content:space-between;
    gap:1rem; padding:1.5rem var(--ef-pad) 2.5rem; border-top:1px solid var(--ef-rule);
    color:var(--ef-ink-2); font-size:.875rem; }}
  @media (max-width: 959px) {{ .ef-spread {{ grid-template-columns:minmax(0,1fr); }}
    .ef-sheet {{ border-right:0; border-bottom:1px solid var(--ef-rule); }} }}
  @media (max-width:760px) {{ .topbar {{ flex-wrap:wrap; gap:.75rem; }}
    .topbar nav {{ order:3; width:100%; margin-left:0; }} }}
{extra_css}
</style>
</head>
<body class="ef ef-contours">
<div class="ef-tri" aria-hidden="true"><i></i><i></i><i></i></div>
<header class="topbar">
  <a class="brand" href="{home}">KYSIIN.ARCHIVE</a>
  <nav class="ef-field" aria-label="主导航">
    <a href="{home}">首页</a>
    <a href="{coll_idx}" aria-current="page">{coll_name}</a>
  </nav>
  <span data-search-slot></span>
  <button class="ef-btn small" type="button" data-theme-toggle>切换深浅</button>
</header>
"""

FOOT = """
<footer class="foot">
  <span class="ef-field">KYSIIN.ARCHIVE · {date} · 由 Markdown 渲染</span>
  <span>用 endfield-ui 渲染 · Saira（SIL OFL）自托管</span>
</footer>
<script type="module">
  import {{ wireTheme }} from '{up}assets/fx.js'
  wireTheme()
</script>
<script defer src="{up}assets/search.js?v={ver}"></script>
<script>
  /* 左栏：每个分组可独立展开/收起 */
  (function () {{
    document.querySelectorAll('.tree-toggle').forEach(function (btn) {{
      btn.addEventListener('click', function (e) {{
        e.preventDefault();
        e.stopPropagation();
        var li = btn.closest('.tree-group');
        var list = li ? li.querySelector('.tree-items') : null;
        var open = btn.getAttribute('aria-expanded') === 'true';
        btn.setAttribute('aria-expanded', String(!open));
        if (list) list.hidden = open;
        if (li) li.classList.toggle('is-open', !open);
      }});
    }});
  }})();
</script>
<script>
  /* 右栏目录跟随滚动：读到哪一节就把那一行标出来 */
  (function () {{
    var links = [].slice.call(document.querySelectorAll('.toc-aside a[href^="#"]'));
    if (!links.length) return;
    var items = links.map(function (a) {{
      var el = document.getElementById(a.getAttribute('href').slice(1));
      return el ? {{ a: a, el: el }} : null;
    }}).filter(Boolean);
    if (!items.length) return;
    var ticking = false;
    function spy() {{
      ticking = false;
      var line = window.scrollY + 140;
      var best = null;
      for (var i = 0; i < items.length; i++) {{
        if (items[i].el.getBoundingClientRect().top + window.scrollY <= line) best = items[i];
      }}
      links.forEach(function (a) {{ a.removeAttribute('aria-current'); }});
      if (best) best.a.setAttribute('aria-current', 'true');
    }}
    window.addEventListener('scroll', function () {{
      if (!ticking) {{ ticking = true; requestAnimationFrame(spy); }}
    }}, {{ passive: true }});
    spy();
  }})();
</script>
</body>
</html>
"""


def render_one(repo, md_path, coll, course, siblings, sections, section,
               prepared, rendered, display_map, math_link="", pdf_rel=None,
               show_pdf=False, tex_map=None):
    """prepared: markdown source with math tokens; rendered: token → svg; display_map: token → bool.

    coll: 文章所属的资料分组（决定 files/ 与 PDF 路径）。
    course: 这门课（slug / name / area），页面上的面包屑与「返回索引」用它。
    siblings: 全课程的文章（上下篇按这个顺序走）。
    sections: [(分区名, [文章…])]，左栏按它分组。
    section: 本文属于哪个分区。
    pdf_rel: published PDF for this article, relative to the collection's files/ root.
    show_pdf: add the download button (review notes only).
    tex_map: token → TeX source, for text-only slots (TOC labels, page title).
    """
    page_dir = os.path.dirname(md_path)
    body_src = prepared

    m = re.search(r"^#\s+(.+)$", body_src, flags=re.M)
    title = re.sub(r"\*\*|__", "", m.group(1)).strip() if m else os.path.splitext(os.path.basename(md_path))[0]
    title = tex_plain(title, tex_map)
    if m:
        body_src = body_src[:m.start()] + body_src[m.end():]
    body_src = demote_headings(body_src)

    index = render_one.index
    body_src = preprocess(body_src, page_dir, repo, index)
    body_src, missing_imgs = localize_images(body_src, page_dir, repo, coll["slug"], index)

    md = markdown.Markdown(extensions=["tables", "fenced_code", "toc", "sane_lists", "attr_list"],
                           extension_configs={"toc": {"permalink": False, "toc_depth": "2-3",
                                                      "slugify": slugify_unicode}})
    body_html = md.convert(body_src)

    def fix_link(mm):
        href = mm.group(1)
        if href.lower().endswith(".md") and not href.startswith(("http://", "https://", "/")):
            return 'href="%s.html"' % href[:-3]
        return 'href="%s"' % href
    body_html = re.sub(r'href="([^"]+)"', fix_link, body_html)

    def fix_asset(mm):
        attr, val = mm.group(1), mm.group(2)
        if val.startswith(("http://", "https://", "data:", "#", "/")) or val.endswith(".html"):
            return mm.group(0)
        if val.startswith("@@"):
            return mm.group(0)
        if os.path.exists(os.path.join(page_dir, val)):
            return mm.group(0)
        hit = index.resolve(val, page_dir, repo)
        if hit:
            return '%s="%s"' % (attr, rel(os.path.join(repo, hit), page_dir))
        return mm.group(0)
    body_html = re.sub(r'(src|href)="([^"]+)"', fix_asset, body_html)
    body_html = substitute_math(body_html, rendered, display_map)

    toc = []

    def walk(tokens, level=2):
        for t in tokens:
            if t["level"] in (2, 3):
                toc.append((t["level"], t["name"], t["id"]))
            walk(t.get("children", []), level + 1)
    walk(md.toc_tokens)

    page_path = os.path.splitext(md_path)[0] + ".html"
    up = rel(repo, page_dir) + "/"
    home = rel(os.path.join(repo, "index.html"), page_dir)
    # 课程页（不是资料分组的索引页）：成员分组的文章都挂到所属课程上
    course_idx = rel(os.path.join(repo, "collections", course["slug"], "index.html"), page_dir)
    folder = rel(page_dir, os.path.join(repo, "collections", coll["slug"], "files"))
    if folder == ".":          # 文章就在 files/ 根目录（relpath 会给出 "."）
        folder = ""

    prev_a = next_a = None
    for k, a in enumerate(siblings):
        if a["path"] == md_path:
            prev_a = siblings[k - 1] if k > 0 else None
            next_a = siblings[k + 1] if k + 1 < len(siblings) else None
            break
    nav = []
    if prev_a:
        nav.append('<a class="ef-btn" href="%s">← %s</a>'
                   % (rel(prev_a["html"], page_dir), html.escape(prev_a["title"])[:24]))
    if next_a:
        nav.append('<a class="ef-btn" href="%s">%s →</a>'
                   % (rel(next_a["html"], page_dir), html.escape(next_a["title"])[:24]))

    def toc_label(name):
        """目录里的小标题：``name`` 已是转义过的 HTML，只把公式 token 换回渲染结果。"""
        out = name
        for tid in set(re.findall(r"@@(EFMATH\d+)@@", name)):
            svg = rendered.get(tid)
            out = out.replace("@@%s@@" % tid,
                              svg if svg else html.escape(tex_map.get(tid, "")))
        return out

    toc_html = "\n".join(
        '      <li><a class="lvl%d" href="#%s">%s</a></li>'
        % (lvl, tid, toc_label(name))
        for lvl, name, tid in toc[:60]) or '      <li><span class="ef-field">本页没有小标题</span></li>'

    parts = []
    for sec_name, items in sections:
        cur_sec = (sec_name == section)
        parts.append('        <li class="tree-group%s">' % (" is-open" if cur_sec else ""))
        parts.append('          <div class="tree-row">')
        parts.append('            <a class="tree-name" href="%s"><span class="tree-label">%s</span>'
                     '<span class="ef-field">%d</span></a>'
                     % ("%s#%s" % (course_idx, quote("sec-" + sec_name)),
                        html.escape(sec_name), len(items)))
        parts.append('            <button class="tree-toggle" type="button" aria-expanded="%s"'
                     ' aria-label="%s %s"><svg viewBox="0 0 12 12" aria-hidden="true">'
                     '<path d="M4 2 L9 6 L4 10" fill="none" stroke="currentColor" stroke-width="1.6"/>'
                     '</svg></button>'
                     % ("true" if cur_sec else "false",
                        "收起" if cur_sec else "展开", html.escape(sec_name)))
        parts.append('          </div>')
        parts.append('          <ol class="tree-items"%s>' % ("" if cur_sec else " hidden"))
        for a in items:
            parts.append('            <li><a href="%s"%s>%s</a></li>' % (
                rel(a["html"], page_dir),
                ' aria-current="page"' if a["path"] == md_path else "",
                html.escape(a["title"])))
        parts.append("          </ol>")
        parts.append("        </li>")
    rail_html = "\n".join(parts) or "\n".join(
        '        <li><a href="%s"%s>%s</a></li>' % (
            rel(a["html"], page_dir),
            ' aria-current="page"' if a["path"] == md_path else "",
            html.escape(a["title"]))
        for a in siblings)

    plain = re.sub(r"<[^>]+>", "", body_html)
    chars = len(CJK.findall(plain)) + len(WORD.findall(plain))
    date = time.strftime("%Y.%m.%d", time.localtime(os.path.getmtime(md_path)))

    pdf_path = None
    if pdf_rel:
        pdf_path = os.path.join(repo, "collections", coll["slug"], "files", pdf_rel)

    pdf_btn = ""
    if pdf_path and show_pdf:
        href = quote(rel(pdf_path, page_dir))
        pdf_btn = ('<p class="ef-actions pdf-dl"><a class="ef-btn" href="%s" download>下载 PDF</a>'
                   '<span class="ef-field">离线 / 打印版</span></p>' % href)

    pdf_note = ""
    if missing_imgs:
        if pdf_path and os.path.isfile(pdf_path):
            pdf_note = ('<p class="ef-notice" data-flag="pdf-fallback">本页引用的 %d 张图片没有随文件复制过来，'
                        '完整版见同目录 PDF：<a href="%s">%s</a></p>'
                        % (missing_imgs, quote(rel(pdf_path, page_dir)),
                           html.escape(os.path.basename(pdf_path))))
        else:
            pdf_note = ('<p class="ef-notice" data-flag="pdf-fallback">本页引用的 %d 张图片未能找到，'
                        '其余文字内容完整。</p>' % missing_imgs)
    page = HEAD.format(title=html.escape(title), up=up, home=home, coll_idx=course_idx,
                       coll_name=html.escape(course["name"]),
                       extra_css=ARTICLE_CSS, math_link=math_link) + f"""
<article class="ef-spread has-rail">
  <aside class="ef-margin rail-aside" aria-label="本课程分区">
    <div class="toc">
      <p class="rail-head ef-field"><span>{html.escape(course["name"])}</span><span>{len(sections)} 区</span></p>
      <ol class="rail-tree">
{rail_html}
      </ol>
      <p class="ef-actions" style="margin:.9rem 0 0">
        <a class="ef-btn small" href="{course_idx}">返回课程</a>
      </p>
    </div>
  </aside>
  <div class="ef-sheet">
    <p class="ef-eyebrow slash">Course / Article</p>
    <p class="ef-crumb ef-field"><a href="{home}">首页</a><a href="{course_idx}">{html.escape(course['name'])}</a><span>{html.escape(section)}</span><span>{html.escape(folder) or '根目录'}</span></p>
    <ul class="ef-facts ef-field">
      <li>{html.escape(section)}</li>
      <li>{chars:,} 字</li>
      <li>{date}</li>
      <li>{len(toc)} 个小节</li>
    </ul>
    <h1 class="title ef-read">{html.escape(title)}</h1>
    <div class="ef-tri" aria-hidden="true"><i></i><i></i><i></i></div>
    {pdf_btn}
    {pdf_note}
    <div class="ef-prose">
{body_html}
    </div>
    <p class="back">{" ".join(nav)} <a class="ef-btn" href="{course_idx}">返回本课</a></p>
  </div>
  <aside class="ef-margin toc-aside" aria-label="本页目录">
    <div class="toc">
      <p class="rail-head ef-field"><span>本页目录</span><span>{len(toc)} 节</span></p>
      <ol>
{toc_html}
      </ol>
    </div>
  </aside>
</article>
""" + FOOT.format(date=BUILD_DATE, up=up, ver=BUILD_VER)

    io.open(page_path, "w", encoding="utf-8", newline="\n").write(page)
    return dict(path=md_path, html=page_path, title=title, chars=chars,
                date=date, toc=len(toc), section=section,
                coll=coll["slug"], label=coll.get("label", ""))


def render_all(repo, collections):
    """Two passes: collect math → render with MathJax → write pages."""
    render_one.index = Index(repo)
    counter = itertools.count(1)
    order, section_of = load_sections()

    courses = {}       # 课程 slug → {slug, name, area, stubs}
    jobs = []          # (coll, course, stub, prepared_src, pdf_rel, generated, show_pdf)
    all_math = []
    for coll in collections:
        key = coll.get("course") or coll["slug"]
        co = courses.get(key)
        if co is None:
            co = courses[key] = dict(slug=key, name=coll["name"],
                                     area=coll.get("area", ""), stubs=[])
        base = os.path.join(repo, "collections", coll["slug"], "files")
        mds = []
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            for fn in filenames:
                if fn.lower().endswith(".md"):
                    mds.append(os.path.join(dirpath, fn))
        mds.sort()

        review = coll.get("review", set())
        md_pdf = coll.get("md_pdf", {})
        pfx = publish.prefix_for(coll["slug"])
        for p in mds:
            rel_md = rel(p, base)
            try:
                head = io.open(p, encoding="utf-8-sig", errors="replace").read(4000)
                m = re.search(r"^#\s+(.+)$", head, flags=re.M)
                title = m.group(1).strip() if m else os.path.splitext(os.path.basename(p))[0]
            except OSError:
                title = os.path.basename(p)
            stub = dict(path=p, html=os.path.splitext(p)[0] + ".html", title=title,
                        section=section_of(coll["slug"], rel_md))
            co["stubs"].append(stub)

            pdf_rel = md_pdf.get(rel_md)
            generated = False
            if not pdf_rel and rel_md in review:
                stem = publish.safe_filename(title)
                if pfx and pfx not in stem:
                    stem = pfx + "-" + stem
                folder = os.path.dirname(rel_md)
                pdf_rel = (folder + "/" if folder else "") + stem + ".pdf"
                n = 2
                while os.path.isfile(os.path.join(base, pdf_rel)):
                    pdf_rel = ((folder + "/" if folder else "")
                               + stem + " (%d).pdf" % n)
                    n += 1
                generated = True
            raw = io.open(p, encoding="utf-8-sig", errors="replace").read()
            src = strip_frontmatter(raw)
            src, math_items = extract_math(src, counter)
            all_math.extend(math_items)
            jobs.append((coll, co, stub, src, pdf_rel, generated, rel_md in review))

    # 每门课：文章按 章节 → 专题 → 实验 排，同区内按路径；左栏与上下篇都用这个顺序
    for co in courses.values():
        co["stubs"].sort(key=lambda a: (order.index(a["section"]) if a["section"] in order
                                        else len(order), a["path"].lower()))
        co["sections"] = [(s, [a for a in co["stubs"] if a["section"] == s]) for s in order]
        co["sections"] = [(s, items) for s, items in co["sections"] if items]

    rendered, math_css = render_math(all_math)
    display_map = {t: d for t, _tex, d in all_math}
    tex_map = {t: tex for t, tex, _d in all_math}
    print("  math: %d formulas, %d rendered, css %d bytes" % (len(all_math), len(rendered), len(math_css)))
    if math_css:
        md_dir = os.path.join(repo, "assets", "mathjax")
        os.makedirs(md_dir, exist_ok=True)
        io.open(os.path.join(md_dir, "mathjax.css"), "w", encoding="utf-8", newline="\n").write(math_css)

    result = {}
    for coll, co, stub, src, pdf_rel, generated, show in jobs:
        try:
            p = stub["path"]
            has_math = "@@EFMATH" in src
            up = rel(repo, os.path.dirname(p)) + "/"
            link = ('<link rel="stylesheet" href="%sassets/mathjax/mathjax.css" />' % up) if has_math else ""
            art = render_one(repo, p, coll, co, co["stubs"], co["sections"], stub["section"],
                             src, rendered, display_map, link, pdf_rel, show, tex_map)
            art["pdf"] = pdf_rel
            art["pdf_generated"] = generated
            result.setdefault(coll["slug"], []).append(art)
        except Exception as e:
            import traceback
            print("  ! render failed:", stub["path"], e)
            traceback.print_exc()
    return result
