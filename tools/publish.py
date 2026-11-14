# -*- coding: utf-8 -*-
"""Publish-time rules for the public site.

Everything in this module happens while `site/` is being assembled: the copies in
`content/`, the Obsidian vault, `PHY/` and `Animation/` stay untouched, so personal
names, student IDs and account names never reach the published repository.

Three jobs:
  1. rename files that carry an identity (student ID / name) in their name;
  2. scrub identity strings out of every published text file;
  3. redact identity strings inside PDFs (and clean their metadata).

The identity strings and the public PDF names live in ``publish.rules.json`` next
to this file. That file is local-only: it is deliberately not copied into
``site/tools/``, so the published repository never contains the strings we scrub.
"""
import io
import json
import os
import re
import shutil
import subprocess
import tempfile

import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
RULES_PATH = os.path.join(HERE, "publish.rules.json")

_DEFAULT = {"tokens": [], "text_subs": [], "mask": {}, "md": {}, "pdf": {}, "drop": {}}
try:
    RULES = json.load(io.open(RULES_PATH, encoding="utf-8"))
except (OSError, ValueError) as _exc:  # published copy has no rules file
    RULES = dict(_DEFAULT)
    print("  ! publish.rules.json 缺失或损坏，跳过改名与脱敏：%s" % _exc)

ID_TOKENS = list(RULES.get("tokens", []))
TEXT_SUBS = [tuple(x) for x in RULES.get("text_subs", [])]
MASK = dict(RULES.get("mask", {}))
MDMAP = RULES.get("md", {})
PDFMAP = RULES.get("pdf", {})
DROP = {k: set(v) for k, v in RULES.get("drop", {}).items()}

# Windows account names that appear in Typora / terminal absolute paths.
# The "Users" folder is not always directly under the drive root (moved profiles
# live in e.g. ``D:\HuaweiMoveData\Users\<name>``), so allow any leading segments.
USER_PATH = re.compile(r"([A-Za-z]:\\(?:[^\\\s\"'<>|]+\\)*?Users\\)([^\\\s\"'<>|]+)")
WXID = re.compile(r"wxid_[0-9a-z]+", re.I)

# A line that is only a cover-page field: drop it whole.
COVER_LINE = re.compile(
    r"^\s*(?:\*\*)?(本人姓名|姓名|学号|指导教师|学院|系|专业|班级)(?:\*\*)?\s*[:：]")

GROUP_LINE = re.compile(r"^\s*>\s*(Group\s+\d+)\s*:?\s*$")
SID_LINE = re.compile(r"(?<!\d)3\d{9}(?!\d)")

COURSE_PREFIX = {
    "animation-review": "计算机动画",
    "physics-review": "大学物理",
    "phy-notes": "大学物理",
    "sfs": "软件安全",
    "oop": "面向对象",
    "netlab": "计算机网络",
    "sys2": "计算机系统II",
    "signal": "信号处理",
    "wireless": "无线安全",
    "clothlab-src": "ClothLab",
    "clothlab-out": "ClothLab",
    "db-2026": "数据库系统",
    "sys1-2024": "计算机系统I",
    "sysintro-2023": "计算机系统概论",
    "netsec-2026": "网络安全",
    "crypto-2026": "密码学",
    "ads-2024": "ADS",
    "iot-2026": "物联网导论",
    "compiler-2026": "编译原理",
}

# Review notes: their article page gets a PDF download button. Missing PDFs are
# generated from the rendered page.
REVIEW_NOTES = {
    "animation-review": ["content/*.md"],
    "physics-review": ["*.md"],
    "db-2026": ["final/*.md"],
    "netsec-2026": ["ex/*.md"],
}

MSYH = r"C:\Windows\Fonts\msyh.ttc"


# --------------------------------------------------------------------------- helpers
def prefix_for(slug):
    return COURSE_PREFIX.get(slug, "")


def strip_identity(name):
    """Remove student id / name tokens from a single file name."""
    n = name
    for old, new in TEXT_SUBS:
        n = n.replace(old, new)
    for tok in ID_TOKENS:
        n = n.replace(tok, "")
    n = re.sub(r"[ _-]{2,}", " ", n)
    n = n.strip(" _-")
    return n or name


def strip_identity_rel(rel):
    head, _, base = rel.rpartition("/")
    cleaned = strip_identity(base)
    return (head + "/" + cleaned) if head else cleaned


def scrub_text(text):
    """Remove identity strings from a Markdown / HTML / text file."""
    for old, new in TEXT_SUBS:
        text = text.replace(old, new)
    text = "\n".join(ln for ln in text.split("\n")
                     if not (ln.strip().startswith(">") and SID_LINE.search(ln)))
    for old, new in MASK.items():
        text = text.replace(old, new)
    text = USER_PATH.sub(lambda m: m.group(1) + "***", text)
    text = WXID.sub("wxid_***", text)
    for tok in ID_TOKENS:
        text = text.replace(tok, "")

    out = []
    for line in text.split("\n"):
        stripped = line.strip()
        if COVER_LINE.match(stripped):
            continue
        if GROUP_LINE.match(stripped):
            line = "> " + GROUP_LINE.match(stripped).group(1)
        line = re.sub(r"\s+$", "", line)
        line = re.sub(r"^(\s*>\s*)\s+", r"\1", line)
        line = line.replace("：", "：")
        out.append(line)
    return "\n".join(out)


def scrub_file(path):
    try:
        raw = io.open(path, encoding="utf-8-sig", errors="replace").read()
    except OSError:
        return False
    new = scrub_text(raw)
    if new == raw:
        return False
    io.open(path, "w", encoding="utf-8", newline="\n").write(new)
    return True


def safe_filename(stem):
    stem = stem.replace("/", "-").replace("\\", "-")
    stem = re.sub(r'[<>:"|?*]', "", stem)
    stem = stem.replace("\u3000", " ")
    stem = re.sub(r"\s+", " ", stem).strip().rstrip(".")
    return stem


# --------------------------------------------------------------------------- pdf
def _line_boxes(page):
    """All text lines of a page as (text, rect)."""
    out = []
    try:
        blocks = page.get_text("dict")["blocks"]
    except Exception:
        return out
    for b in blocks:
        for line in b.get("lines", []):
            spans = line.get("spans", [])
            txt = "".join(s.get("text", "") for s in spans)
            if not txt.strip():
                continue
            out.append((txt, pymupdf.Rect(line["bbox"])))
    return out


def _meta_is_sensitive(meta, extra=()):
    blob = " ".join(str(v) for v in (meta or {}).values())
    keys = list(ID_TOKENS) + list(extra)
    return any(k and k in blob for k in keys)


def sanitize_pdf(path, title=None, subs=None, clear_meta=(), timeout=180):
    """Redact identity strings and clean metadata. Returns True when re-saved."""
    try:
        doc = pymupdf.open(path)
    except Exception as exc:
        print("  ! pdf unreadable, kept as-is:", os.path.basename(path), exc)
        return False
    changed = False
    for page in doc:
        taken = []

        def take(rect):
            if any(r.intersects(rect) for r in taken):
                return False
            taken.append(rect)
            page.add_redact_annot(rect, fill=None)
            return True

        inserts = []
        for old, new in (subs or {}).items():
            for r in page.search_for(old):
                if take(r):
                    inserts.append((r, new))
                    changed = True
        for txt, rect in _line_boxes(page):
            if COVER_LINE.match(txt.strip()):
                if take(rect):
                    changed = True
            elif SID_LINE.search(txt) and len(txt.strip()) < 40:
                # a short line that still carries the student ID is a cover/footer
                # line: drop it whole instead of leaving a fragment behind
                if take(rect):
                    changed = True
        for tok in ID_TOKENS:
            for r in page.search_for(tok):
                if take(r):
                    changed = True
        if taken:
            page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE,
                                  graphics=pymupdf.PDF_REDACT_LINE_ART_NONE,
                                  text=pymupdf.PDF_REDACT_TEXT_REMOVE)
            for rect, new in inserts:
                try:
                    page.insert_font(fontname="msyh", fontfile=MSYH)
                    page.insert_text((rect.x0, rect.y1 - 1.8), new,
                                     fontname="msyh", fontsize=8.4,
                                     color=(0.11, 0.11, 0.11))
                except Exception as exc:
                    print("  ! pdf insert:", os.path.basename(path), exc)

    meta = doc.metadata or {}
    if not (changed or _meta_is_sensitive(meta, clear_meta)):
        doc.close()
        return False

    new_meta = {
        "title": title or "",
        "author": "",
        "subject": "",
        "keywords": "",
        "creator": "",
        "producer": "KYSIIN.ARCHIVE",
    }
    for key in ("creationDate", "modDate"):
        if meta.get(key):
            new_meta[key] = meta[key]
    doc.set_metadata(new_meta)
    try:
        doc.set_xml_metadata("")
    except Exception:
        pass
    fd, tmp = tempfile.mkstemp(suffix=".pdf", dir=os.path.dirname(path))
    os.close(fd)
    try:
        doc.subset_fonts()   # the inserted CJK font is a whole 15 MB face otherwise
    except Exception:
        pass
    doc.save(tmp, garbage=4, deflate=True, clean=True)
    doc.close()
    os.replace(tmp, path)
    return True


# --------------------------------------------------------------------------- collection pass
def process_collection(c, repo):
    """Rename / scrub / redact one copied collection in place.

    Mutates ``c``: updates ``files`` and adds ``md_pdf`` (article -> pdf, both
    relative to the collection's files/ root) plus ``review`` (set of articles).
    """
    slug = c["slug"]
    prefix = "collections/%s/files/" % slug
    drops = DROP.get(slug, set())
    mdmap = MDMAP.get(slug, {})
    pdfmap = PDFMAP.get(slug, {})

    plan = []
    for f in c["files"]:
        rel = f["path"][len(prefix):]
        if rel in drops:
            try:
                os.remove(os.path.join(repo, f["path"]))
            except OSError:
                pass
            continue
        if rel in mdmap:
            new = mdmap[rel]
        elif rel in pdfmap:
            target = pdfmap[rel]["new"]
            head = os.path.dirname(rel).replace("\\", "/")
            new = (head + "/" + target) if (head and "/" not in target) else target
        else:
            new = strip_identity_rel(rel)
        plan.append((f, rel, new))

    seen = {}
    for f, rel, new in plan:
        if new in seen:
            raise SystemExit("  ! name clash in %s: %r and %r -> %r"
                             % (slug, seen[new], rel, new))
        seen[new] = rel

    md_pdf = {}
    kept = []
    renamed = {rel: new for f, rel, new in plan}
    for f, rel, new in plan:
        abs_old = os.path.join(repo, f["path"])
        ext = os.path.splitext(rel)[1].lower()
        if ext in (".md", ".html", ".txt", ".json", ".css", ".js"):
            scrub_file(abs_old)
        elif ext == ".pdf":
            info = pdfmap.get(rel, {})
            stem = os.path.splitext(os.path.basename(new))[0]
            changed = sanitize_pdf(abs_old, title=stem, subs=info.get("subs"),
                                   clear_meta=info.get("clear_meta", ()))
            if changed:
                print("    redacted %s/%s" % (slug, rel))
        abs_new = os.path.join(repo, prefix + new)
        if new != rel:
            os.makedirs(os.path.dirname(abs_new), exist_ok=True)
            os.replace(abs_old, abs_new)
        st = os.stat(abs_new)
        f["path"] = prefix + new
        f["size"] = st.st_size
        f["mtime"] = st.st_mtime
        f["ext"] = ext
        kept.append(f)
        if ext == ".pdf" and rel in pdfmap and pdfmap[rel].get("md"):
            # the rule names the *source* article; resolve it through the same
            # rename pass the article itself gets, or the mapping never matches
            old_md = pdfmap[rel]["md"]
            new_md = renamed.get(old_md) or strip_identity_rel(old_md)
            md_pdf[new_md] = new

    c["files"] = kept
    c["md_pdf"] = md_pdf

    # review-note articles of this collection
    import fnmatch
    review = set()
    pats = REVIEW_NOTES.get(slug, [])
    for f, rel, new in plan:
        if os.path.splitext(rel)[1].lower() == ".md":
            for pat in pats:
                if fnmatch.fnmatch(new, pat):
                    review.add(new)
                    break
    c["review"] = review
    return c


# --------------------------------------------------------------------------- generated pdfs
def _edge_binary():
    for p in (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"):
        if os.path.isfile(p):
            return p
    return None


def html_to_pdf(html_path, out_pdf, timeout=180):
    edge = _edge_binary()
    if not edge:
        return False
    from pathlib import Path
    uri = Path(html_path).resolve().as_uri()
    profile = tempfile.mkdtemp(prefix="efprint-")
    cmd = [edge, "--headless=new", "--disable-gpu", "--no-first-run",
           "--no-default-browser-check", "--disable-extensions",
           "--hide-scrollbars", "--virtual-time-budget=4000",
           "--user-data-dir=" + profile,
           "--no-pdf-header-footer",
           "--print-to-pdf=" + out_pdf, uri]
    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=timeout)
    except Exception as exc:
        print("  ! pdf print failed:", os.path.basename(html_path), exc)
        shutil.rmtree(profile, ignore_errors=True)
        return False
    shutil.rmtree(profile, ignore_errors=True)
    if proc.returncode != 0 or not os.path.isfile(out_pdf) or os.path.getsize(out_pdf) < 1000:
        print("  ! pdf print failed:", os.path.basename(html_path),
              proc.returncode, proc.stderr.decode("utf-8", "replace")[-300:])
        return False
    return True


def clear_meta_of(path, title=""):
    """Wipe metadata of a copied PDF (used for files outside collections)."""
    try:
        doc = pymupdf.open(path)
    except Exception:
        return
    meta = doc.metadata or {}
    new_meta = {"title": title or meta.get("title", ""), "author": "",
                "subject": "", "keywords": "", "creator": "",
                "producer": "KYSIIN.ARCHIVE"}
    for key in ("creationDate", "modDate"):
        if meta.get(key):
            new_meta[key] = meta[key]
    doc.set_metadata(new_meta)
    try:
        doc.set_xml_metadata("")
    except Exception:
        pass
    fd, tmp = tempfile.mkstemp(suffix=".pdf", dir=os.path.dirname(path))
    os.close(fd)
    doc.save(tmp, garbage=3, deflate=True)
    doc.close()
    os.replace(tmp, path)
