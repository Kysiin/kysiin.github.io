// 构建脚本：把 7 个 Markdown 文件合成
//   ① 大学物理乙2复习资料.md   （纯 Markdown 合订本）
//   ② 大学物理乙2复习资料.html （离线自包含，自带 Markdown + LaTeX 渲染，无需联网）
// 用法：node build.mjs
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const ROOT = dirname(fileURLToPath(import.meta.url));
const FILES = [
  '00-复习路线与使用说明.md',
  '01-公式速查表.md',
  '02-通用做题方法与题型套路.md',
  'ch12-静电场.md',
  'ch13-导体与电介质.md',
  'ch14-电流与磁场.md',
  '03-综合自测卷.md'
];

/* ============================ 一、LaTeX 迷你渲染 ============================ */

const SYM = {
  alpha: 'α', beta: 'β', gamma: 'γ', delta: 'δ', epsilon: 'ε', varepsilon: 'ε',
  zeta: 'ζ', eta: 'η', theta: 'θ', vartheta: 'ϑ', iota: 'ι', kappa: 'κ',
  lambda: 'λ', mu: 'μ', nu: 'ν', xi: 'ξ', omicron: 'ο', pi: 'π', varpi: 'ϖ',
  rho: 'ρ', varrho: 'ϱ', sigma: 'σ', varsigma: 'ς', tau: 'τ', upsilon: 'υ',
  phi: 'φ', varphi: 'φ', chi: 'χ', psi: 'ψ', omega: 'ω',
  Gamma: 'Γ', Delta: 'Δ', Theta: 'Θ', Lambda: 'Λ', Xi: 'Ξ', Pi: 'Π',
  Sigma: 'Σ', Upsilon: 'Υ', Phi: 'Φ', Psi: 'Ψ', Omega: 'Ω',
  times: '×', cdot: '·', div: '÷', pm: '±', mp: '∓', ast: '∗', star: '⋆',
  approx: '≈', neq: '≠', ne: '≠', equiv: '≡', sim: '∼', simeq: '≃', cong: '≅',
  le: '≤', leq: '≤', ge: '≥', geq: '≥', ll: '≪', gg: '≫', propto: '∝',
  infty: '∞', partial: '∂', nabla: '∇', prime: '′', degree: '°', circ: '∘',
  int: '∫', iint: '∬', iiint: '∭', oint: '∮', sum: 'Σ', prod: '∏',
  to: '→', rightarrow: '→', leftarrow: '←', Rightarrow: '⇒', Leftarrow: '⇐',
  leftrightarrow: '↔', Leftrightarrow: '⇔', longrightarrow: '⟶', Longrightarrow: '⟹',
  longleftrightarrow: '⟷', implies: '⟹', iff: '⟺', mapsto: '↦', uparrow: '↑', downarrow: '↓',
  ldots: '…', cdots: '⋯', dots: '…', vdots: '⋮', ddots: '⋱',
  in: '∈', notin: '∉', subset: '⊂', subseteq: '⊆', cup: '∪', cap: '∩', emptyset: '∅',
  forall: '∀', exists: '∃', therefore: '∴', because: '∵',
  angle: '∠', perp: '⊥', parallel: '∥', triangle: '△', square: '□',
  lvert: '|', rvert: '|', vert: '|', Vert: '‖', lVert: '‖', rVert: '‖',
  langle: '⟨', rangle: '⟩', lbrace: '{', rbrace: '}', lbrack: '[', rbrack: ']',
  ell: 'ℓ', hbar: 'ℏ', Re: 'ℜ', Im: 'ℑ', aleph: 'ℵ', imath: 'ı', jmath: 'ȷ',
  '%': '%', '&': '&', '#': '#', _: '_', '{': '{', '}': '}', '$': '$'
};
const FN = new Set(['sin', 'cos', 'tan', 'cot', 'sec', 'csc', 'arcsin', 'arccos',
  'arctan', 'sinh', 'cosh', 'tanh', 'ln', 'log', 'lg', 'exp', 'lim', 'max', 'min',
  'det', 'gcd', 'sup', 'inf', 'arg', 'deg', 'dim', 'ker', 'Pr']);

const esc = (t) => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const ESC_SPACE = '<span class="msp"></span>';

export function texToHtml(input) {
  const s = input.replace(/\r/g, '').trim();
  let i = 0;

  function skipBracket() {
    if (s[i] === '[') {
      const j = s.indexOf(']', i);
      if (j > 0) { i = j + 1; }
    }
  }
  function readRawGroup() {
    if (s[i] !== '{') return '';
    let depth = 0, start = i + 1;
    for (let k = i; k < s.length; k++) {
      if (s[k] === '\\') { k++; continue; }
      if (s[k] === '{') depth++;
      else if (s[k] === '}') { depth--; if (depth === 0) { const out = s.slice(start, k); i = k + 1; return out; } }
    }
    i = s.length; return s.slice(start);
  }
  function readAtomHtml() {
    while (s[i] === ' ') i++;
    if (s[i] === '{') { i++; return readSeq({}).html; }
    if (s[i] === '\\') {
      const m = /^\\([a-zA-Z]+)/.exec(s.slice(i));
      if (m) { i += m[0].length; return readCommand(m[1]); }
      const nc = s[i + 1]; i += 2; return esc(SYM[nc] ?? nc);
    }
    if (s[i] === undefined) return '';
    const c = s[i]; i++;
    if (c === '^' || c === '_') return ''; // 避免死循环
    return esc(c);
  }

  const frac = (num, den) =>
    `<span class="fr"><span class="nu">${num}</span><span class="de">${den}</span></span>`;

  function grid(rows, cls) {
    const body = rows
      .map((r) => `<span class="grow">${r.map((c) => `<span class="cell">${c}</span>`).join('')}</span>`)
      .join('');
    return `<span class="grid ${cls || ''}">${body}</span>`;
  }
  function renderEnv(name, rows) {
    if (name === 'cases' || name === 'dcases') {
      return `<span class="env"><span class="brace" style="transform:scale(1.4,${(rows.length * 2.6).toFixed(1)})">{</span>${grid(rows, 'cases')}</span>`;
    }
    if (name === 'vmatrix' || name === 'Vmatrix') {
      return `<span class="env"><span class="dbar">|</span>${grid(rows)}<span class="dbar">|</span></span>`;
    }
    if (name === 'pmatrix') {
      return `<span class="env"><span class="dpar">(</span>${grid(rows)}<span class="dpar">)</span></span>`;
    }
    if (name === 'bmatrix') {
      return `<span class="env"><span class="dpar">[</span>${grid(rows)}<span class="dpar">]</span></span>`;
    }
    // aligned / align / gathered / array / matrix / split
    return `<span class="env">${grid(rows)}</span>`;
  }

  function readCommand(cmd) {
    switch (cmd) {
      case 'frac': case 'dfrac': case 'tfrac': case 'cfrac': {
        while (s[i] === ' ') i++;
        const a = readAtomHtml();
        while (s[i] === ' ') i++;
        const b = readAtomHtml();
        return frac(a, b);
      }
      case 'sqrt': {
        skipBracket();
        const a = readAtomHtml();
        return `<span class="sq">√<span class="rad">${a}</span></span>`;
      }
      case 'text': case 'textrm': case 'mbox': case 'operatorname': case 'textup': {
        const raw = readRawGroup();
        return `<span class="rm">${esc(raw)}</span>`;
      }
      case 'mathrm': case 'rm': case 'mathsf': case 'mathtt': {
        const raw = readRawGroup();
        return `<span class="rm">${texToHtml(raw)}</span>`;
      }
      case 'mathit': return `<span class="it">${texToHtml(readRawGroup())}</span>`;
      case 'mathbf': case 'boldsymbol': case 'bm': case 'vec': case 'hat': {
        const raw = readRawGroup();
        return `<span class="bf">${texToHtml(raw)}</span>`;
      }
      case 'mathcal': return `<span class="cal">${texToHtml(readRawGroup())}</span>`;
      case 'boxed': case 'fbox': return `<span class="boxed">${texToHtml(readRawGroup())}</span>`;
      case 'overline': return `<span class="ovl">${texToHtml(readRawGroup())}</span>`;
      case 'underline': return `<span class="unl">${texToHtml(readRawGroup())}</span>`;
      case 'left': case 'right': {
        while (s[i] === ' ') i++;
        let d = s[i];
        if (d === '\\') {
          const m = /^\\([a-zA-Z]+|.)/.exec(s.slice(i));
          if (m) { i += m[0].length; d = SYM[m[1]] ?? (m[1] === '|' ? '‖' : m[1]); }
        } else { i++; }
        if (d === '.') return '';
        if ('()[]|'.includes(d)) return `<span class="delim">${esc(d)}</span>`;
        return `<span class="delim">${esc(d)}</span>`;
      }
      case 'begin': {
        const env = readRawGroup();
        if (env === 'array' || env === 'tabular') { readRawGroup(); }
        const rows = []; let cells = [];
        for (;;) {
          const r = readSeq({ envEnd: env, cell: true, row: true });
          cells.push(r.html);
          if (r.end === 'cell') continue;
          rows.push(cells); cells = [];
          if (r.end === 'env' || r.end === 'eof') break;
        }
        return renderEnv(env, rows);
      }
      case 'quad': return '<span class="mquad"></span>';
      case 'qquad': return '<span class="mqquad"></span>';
      case 'displaystyle': case 'textstyle': case 'scriptstyle': case 'limits':
      case 'nolimits': case 'nonumber': case 'notag': case 'mathstrut':
        return '';
      case 'phantom': readRawGroup(); return '';
      case 'color': readRawGroup(); return '';
      default:
        if (FN.has(cmd)) return `<span class="fn">${cmd}</span>`;
        if (SYM[cmd] !== undefined) return esc(SYM[cmd]);
        return `<span class="rm">${esc(cmd)}</span>`;
    }
  }

  function readSeq(opts = {}) {
    let out = '';
    while (i < s.length) {
      if (opts.envEnd && s.startsWith('\\end{' + opts.envEnd + '}', i)) {
        i += ('\\end{' + opts.envEnd + '}').length;
        return { html: out, end: 'env' };
      }
      if (opts.row && s.startsWith('\\\\', i)) {
        i += 2; skipBracket();
        return { html: out, end: 'row' };
      }
      if (opts.cell && s[i] === '&') { i++; return { html: out, end: 'cell' }; }
      const c = s[i];
      if (c === '\\') {
        const m = /^\\([a-zA-Z]+)/.exec(s.slice(i));
        if (m) { i += m[0].length; out += readCommand(m[1]); continue; }
        const nc = s[i + 1];
        if (nc === undefined) { i++; break; }
        i += 2;
        if (nc === ' ' || nc === ',' || nc === ';' || nc === ':' || nc === '!') { out += ESC_SPACE; continue; }
        out += esc(SYM[nc] ?? nc);
        continue;
      }
      if (c === '{') { i++; out += readSeq({}).html; continue; }
      if (c === '}') { i++; return { html: out, end: 'brace' }; }
      if (c === '^') { i++; out += `<sup>${readAtomHtml()}</sup>`; continue; }
      if (c === '_') { i++; out += `<sub>${readAtomHtml()}</sub>`; continue; }
      if (c === '~') { i++; out += '&nbsp;'; continue; }
      if (c === ' ') { i++; out += ' '; continue; }
      out += esc(c); i++;
    }
    return { html: out, end: 'eof' };
  }

  return readSeq({}).html;
}

/* ============================ 二、Markdown 渲染 ============================ */

const inlineCache = [];

function renderInline(text) {
  // 1) 行内代码
  const parts = text.split(/(`[^`]+`)/g);
  return parts.map((seg) => {
    if (/^`[^`]+`$/.test(seg)) return `<code>${esc(seg.slice(1, -1))}</code>`;
    let t = esc(seg);
    // 2) 粗体 **x** / 斜体 *x*
    t = t.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    t = t.replace(/(^|[^*])\*([^*\s][^*]*?)\*(?!\*)/g, '$1<em>$2</em>');
    // 3) 链接 [t](u)
    t = t.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, '<a href="$2">$1</a>');
    // 4) 恢复数学占位符
    t = t.replace(/@@MATH(\d+)@@/g, (_m, idx) => inlineCache[Number(idx)]);
    return t;
  }).join('');
}

function splitRow(line) {
  let t = line.trim();
  if (t.startsWith('|')) t = t.slice(1);
  if (t.endsWith('|')) t = t.slice(0, -1);
  return t.split('|').map((c) => c.trim());
}

let headingSeq = 0; // 全局标题序号：跨文件唯一，保证锚点不重复

function convert(md) {
  const lines = md.replace(/\r\n/g, '\n').split('\n');
  const toc = [];
  let html = '';
  let i = 0;

  const blockStart = (line) => (
    /^\s*$/.test(line) ||
    /^#{1,6}\s/.test(line) ||
    /^```/.test(line) ||
    /^\s*\|/.test(line) ||
    /^>\s?/.test(line) ||
    /^\s*([-*+]|\d+[.)])\s+/.test(line) ||
    /^\s*(-{3,}|\*{3,}|_{3,})\s*$/.test(line) ||
    /^@@MATH\d+@@\s*$/.test(line)
  );

  while (i < lines.length) {
    const line = lines[i];

    if (/^\s*$/.test(line)) { i++; continue; }

    // 独占一行的公式
    const mathOnly = /^@@MATH(\d+)@@\s*$/.exec(line);
    if (mathOnly) {
      html += `<div class="mathblock">${inlineCache[Number(mathOnly[1])]}</div>\n`;
      i++;
      continue;
    }

    // 代码块
    if (/^```/.test(line)) {
      const buf = [];
      i++;
      while (i < lines.length && !/^```/.test(lines[i])) { buf.push(lines[i]); i++; }
      i++;
      html += `<pre><code>${esc(buf.join('\n'))}</code></pre>\n`;
      continue;
    }

    // 标题
    const h = /^(#{1,6})\s+(.*)$/.exec(line);
    if (h) {
      const level = h[1].length;
      const id = 'sec-' + (headingSeq++);
      const textHtml = renderInline(h[2].trim());
      if (level <= 2) {
        const plain = textHtml.replace(/<[^>]+>/g, '')
          .replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&').trim();
        toc.push({ level, id, text: plain || h[2].trim() });
      }
      html += `<h${level} id="${id}">${textHtml}</h${level}>\n`;
      i++;
      continue;
    }

    // 分隔线
    if (/^\s*(-{3,}|\*{3,}|_{3,})\s*$/.test(line)) { html += '<hr>\n'; i++; continue; }

    // 表格
    if (/^\s*\|/.test(line) && /^\s*\|[\s:|-]+\|\s*$/.test(lines[i + 1] || '')) {
      const head = splitRow(line);
      const align = splitRow(lines[i + 1]).map((c) => (
        /^:-+:$/.test(c) ? 'center' : /-+:$/.test(c) ? 'right' : 'left'
      ));
      i += 2;
      let body = '';
      while (i < lines.length && /^\s*\|/.test(lines[i])) {
        const cells = splitRow(lines[i]);
        body += '<tr>' + head.map((_x, k) => {
          const a = align[k] ? ` style="text-align:${align[k]}"` : '';
          return `<td${a}>${renderInline(cells[k] ?? '')}</td>`;
        }).join('') + '</tr>\n';
        i++;
      }
      html += '<div class="tablewrap"><table>\n<thead><tr>' +
        head.map((c, k) => `<th${align[k] ? ` style="text-align:${align[k]}"` : ''}>${renderInline(c)}</th>`).join('') +
        '</tr></thead>\n<tbody>\n' + body + '</tbody></table></div>\n';
      continue;
    }

    // 引用块
    if (/^>\s?/.test(line)) {
      const buf = [];
      while (i < lines.length && /^>\s?/.test(lines[i])) { buf.push(lines[i].replace(/^>\s?/, '')); i++; }
      const inner = buf.map((l) => (/^\s*$/.test(l) ? '' : `<p>${renderInline(l)}</p>`)).join('');
      html += `<blockquote>${inner}</blockquote>\n`;
      continue;
    }

    // 列表
    if (/^\s*([-*+]|\d+[.)])\s+/.test(line)) {
      const items = [];
      while (i < lines.length && /^\s*([-*+]|\d+[.)])\s+/.test(lines[i])) {
        const m = /^(\s*)([-*+]|\d+[.)])\s+(.*)$/.exec(lines[i]);
        items.push({ indent: m[1].length, ordered: /\d/.test(m[2]), text: m[3], num: parseInt(m[2], 10) });
        i++;
        // 续行（缩进的普通文本行）
        while (i < lines.length && /^\s+\S/.test(lines[i]) && !/^\s*([-*+]|\d+[.)])\s+/.test(lines[i]) && !blockStart(lines[i])) {
          items[items.length - 1].text += ' ' + lines[i].trim();
          i++;
        }
      }
      // 依据 indent 构建列表树，再递归渲染（标签配对正确，子列表嵌在 <li> 内）
      const rootNode = { lvl: -1, ordered: false, text: '', children: [] };
      const stack = [rootNode];
      for (const it of items) {
        while (stack.length > 1 && stack[stack.length - 1].lvl >= it.indent) stack.pop();
        const node = { lvl: it.indent, ordered: it.ordered, text: it.text, children: [] };
        stack[stack.length - 1].children.push(node);
        stack.push(node);
      }
      const renderTree = (node) => {
        const tag = node.ordered ? 'ol' : 'ul';
        let s = '<' + tag + '>';
        for (const c of node.children) {
          s += '<li>' + renderInline(c.text);
          if (c.children.length) s += renderTree(c);
          s += '</li>';
        }
        return s + '</' + tag + '>';
      };
      html += renderTree(rootNode) + '\n';
      continue;
    }

    // 段落
    const buf = [];
    while (i < lines.length && !blockStart(lines[i])) { buf.push(lines[i]); i++; }
    if (buf.length) {
      const text = buf.map((l) => l.trim()).join(' ');
      html += `<p>${renderInline(text)}</p>\n`;
    } else {
      i++; // 防御：避免死循环
    }
  }
  return { html, toc };
}

/* ============================ 三、主流程 ============================ */

function main() {
const chunks = [];
const allToc = [];
let first = true;

for (const f of FILES) {
  const raw = readFileSync(join(ROOT, f), 'utf8').replace(/\r\n/g, '\n');
  let md = raw;

  // 保护公式：display 优先，其次 inline
  md = md.replace(/\$\$([\s\S]*?)\$\$/g, (m, body) => {
    const token = '@@MATH' + inlineCache.length + '@@';
    inlineCache.push(`<span class="mathdisplay">${texToHtml(body)}</span>`);
    return token;
  });
  md = md.replace(/\$([^\n$]+?)\$/g, (m, body) => {
    const token = '@@MATH' + inlineCache.length + '@@';
    inlineCache.push(`<span class="mathinline">${texToHtml(body)}</span>`);
    return token;
  });

  const { html, toc } = convert(md);
  const title = raw.match(/^#\s+(.*)$/m);
  allToc.push({ file: f, title: title ? title[1].trim() : f, entries: toc });
  chunks.push((first ? '' : '<div class="pagebreak"></div>\n') + html);
  first = false;
}

const combinedMd = FILES.map((f) => readFileSync(join(ROOT, f), 'utf8').replace(/\r\n/g, '\n').trimEnd())
  .join('\n\n---\n\n');
writeFileSync(join(ROOT, '大学物理乙2复习资料.md'), combinedMd + '\n', 'utf8');

const tocHtml = allToc.map((sec) =>
  sec.entries.map((e) => (
    e.level === 1
      ? `<a class="tocfile" href="#${e.id}">${esc(e.text)}</a>`
      : `<a href="#${e.id}">${esc(e.text)}</a>`
  )).join('')
).join('');

const html = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>大学物理乙（二）小测复习资料 · 第12–14章</title>
<style>${CSS}</style>
</head>
<body>
<header class="top">
  <h1 class="doctitle">大学物理乙（二）· 小测复习资料</h1>
  <p class="sub">第 12 章 静电场 ｜ 第 13 章 静电场中的导体和电介质 ｜ 第 14 章 电流和磁场</p>
  <p class="sub2">对应教材《工程物理学（第三版）》· 名誉主编 诸葛向彬 · 主编 陆赟豪、金洪英</p>
  <p class="hint">本页完全离线可用 ｜ 左栏目录可点击 ｜ 浏览器 <b>Ctrl + P</b> 可直接打印或另存为 PDF（已配置分页）</p>
</header>
<div class="layout">
  <nav id="toc"><div class="toctitle">目 录</div>${tocHtml}</nav>
  <main id="content">
${chunks.join('\n')}
  </main>
</div>
<button id="totop" title="回到顶部">↑</button>
<script>${JS}</script>
</body>
</html>
`;

writeFileSync(join(ROOT, '大学物理乙2复习资料.html'), html, 'utf8');

const kb = (n) => (n / 1024).toFixed(1) + ' KB';
console.log('✓ 大学物理乙2复习资料.md  ' + kb(Buffer.byteLength(combinedMd, 'utf8')));
console.log('✓ 大学物理乙2复习资料.html ' + kb(Buffer.byteLength(html, 'utf8')));
console.log('  公式总数：' + inlineCache.length + '（display ' +
  inlineCache.filter((x) => x.startsWith('<span class="mathdisplay"')).length + '）');
console.log('  目录条目：' + allToc.reduce((a, s) => a + s.entries.length, 0));
}

/* ============================ 四、CSS / JS ============================ */

const CSS = `
:root{
  --ink:#1f2328; --ink2:#5b6470; --line:#d9dee5; --bg:#fcfbf9;
  --accent:#b03a2e; --accent2:#0b5fa5; --panel:#f2f3f1; --mathbg:#fbfaf6;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{
  margin:0; background:var(--bg); color:var(--ink);
  font-family:"Microsoft YaHei","PingFang SC","Hiragino Sans GB","Source Han Sans SC","Noto Sans CJK SC",sans-serif;
  font-size:16px; line-height:1.8; -webkit-font-smoothing:antialiased;
}
header.top{padding:26px 26px 18px; border-bottom:3px solid var(--accent); background:linear-gradient(180deg,#fff,#f7f6f2)}
.doctitle{margin:0 0 6px; font-size:26px; letter-spacing:.5px}
.sub{margin:3px 0; color:var(--ink2); font-size:15px}
.sub2{margin:2px 0; color:var(--ink2); font-size:13.5px}
.hint{margin:10px 0 0; color:var(--accent); font-size:13.5px}
.layout{display:flex; align-items:flex-start; gap:26px; padding:0 26px 90px; max-width:1520px; margin:0 auto}
nav#toc{
  position:sticky; top:0; flex:0 0 272px; max-height:100vh; overflow:auto;
  padding:16px 3px 70px 0; font-size:13.5px; line-height:1.55;
}
.toctitle{font-weight:700; font-size:13.5px; letter-spacing:3px; color:var(--ink2); padding:0 0 8px 8px; border-bottom:1px solid var(--line); margin-bottom:8px}
.tocfile{display:block; font-weight:700; color:var(--ink); margin:14px 0 4px; padding:4px 8px; background:var(--panel); border-left:3px solid var(--accent); font-size:13px; text-decoration:none; border-radius:0 4px 4px 0}
a.tocfile:hover{background:#e7ebee; color:var(--accent)}
#toc a{display:block; padding:2px 8px 2px 14px; color:var(--ink2); text-decoration:none; border-left:2px solid transparent; border-radius:0 4px 4px 0}
#toc a:hover{background:#eef0ee; color:var(--ink)}
#toc a.active{color:var(--accent); border-left-color:var(--accent); background:#f5efec; font-weight:700}
main#content{flex:1 1 auto; min-width:0; max-width:920px; padding-top:16px}
main#content h1{font-size:24px; margin:36px 0 14px; padding-bottom:8px; border-bottom:2px solid var(--accent); line-height:1.4}
main#content h2{font-size:19.5px; margin:30px 0 10px; padding:7px 12px; border-left:5px solid var(--accent); background:var(--panel); line-height:1.5}
main#content h3{font-size:17px; margin:24px 0 8px; color:#1f3b57; border-bottom:1px dotted #c9d2db; padding-bottom:3px}
main#content h4{font-size:16px; margin:20px 0 6px; color:var(--accent2)}
main#content p{margin:9px 0}
main#content ul,main#content ol{margin:8px 0 8px 1.5em; padding:0}
main#content li{margin:4px 0}
main#content strong{color:#0b3d91}
main#content em{color:#7a4b00; font-style:normal; font-weight:600}
main#content blockquote{margin:14px 0; padding:10px 16px; background:#fffdf2; border-left:4px solid #e0b33f; color:#4a3a05; border-radius:0 6px 6px 0; font-size:15px}
main#content blockquote p{margin:4px 0}
main#content code{font-family:Consolas,"Cascadia Mono",monospace; font-size:.9em; background:#eef1f4; padding:1px 5px; border-radius:4px; color:#a4273e}
main#content pre{background:#f6f7f5; border:1px solid var(--line); border-radius:8px; padding:12px 14px; overflow:auto; line-height:1.55}
main#content pre code{background:none; padding:0; color:#333; font-size:13px}
main#content hr{border:none; border-top:1px dashed #c6ccd4; margin:26px 0}
.tablewrap{overflow-x:auto; margin:14px 0}
main#content table{border-collapse:collapse; width:100%; font-size:14.5px; background:#fff}
main#content th,main#content td{border:1px solid var(--line); padding:6px 10px; vertical-align:top}
main#content th{background:#e9eef3; font-weight:700}
main#content tbody tr:nth-child(even) td{background:#fafbfc}
.pagebreak{page-break-before:always; break-before:page; height:0}
.mathblock{margin:12px 0; padding:8px 10px; background:var(--mathbg); border-radius:6px; overflow-x:auto; text-align:center}
.mathinline{white-space:nowrap}
.fr{display:inline-block; vertical-align:middle; text-align:center; margin:0 .14em; line-height:1.16; font-size:.95em}
.fr>.nu{display:block; border-bottom:1.3px solid currentColor; padding:0 .16em}
.fr>.de{display:block; padding:0 .16em}
.sq{white-space:nowrap}
.sq>.rad{border-top:1.1px solid currentColor; padding:0 .1em; margin-left:-.04em}
.env{display:inline-flex; align-items:center; vertical-align:middle; margin:0 .15em}
.env>.brace{font-size:1.05em; transform:scale(1.9,.95); display:inline-block; margin-right:.06em; line-height:.9}
.env>.dbar{font-size:1.35em; margin:0 .06em}
.env>.dpar{font-size:1.35em; margin:0 .02em}
.grid{display:inline-flex; flex-direction:column; row-gap:.14em; text-align:left; vertical-align:middle; margin:0 .1em}
.grow{display:inline-flex; column-gap:1.1em; align-items:baseline}
.grid.cases .grow{column-gap:1.7em}
.cell{white-space:nowrap}
.rm{font-style:normal; font-family:"Times New Roman",Georgia,serif}
.it{font-style:italic}
.bf{font-weight:700; font-style:italic}
.bf>.rm{font-style:normal}
.cal{font-family:"Times New Roman",Georgia,serif; font-style:italic}
.fn{font-style:normal; font-family:"Times New Roman",Georgia,serif; margin-right:.12em}
.delim{font-size:1.15em}
.msp{display:inline-block; width:.17em}
.mquad{display:inline-block; width:1em}
.mqquad{display:inline-block; width:2em}
.boxed{display:inline-block; border:1.4px solid currentColor; padding:.08em .35em; border-radius:3px; margin:0 .1em}
.ovl{text-decoration:overline}
.unl{text-decoration:underline}
sup,sub{font-size:.72em; line-height:0}
#totop{position:fixed; right:20px; bottom:22px; width:44px; height:44px; border-radius:50%; border:1px solid var(--line); background:#fff; color:var(--ink2); font-size:18px; cursor:pointer; box-shadow:0 2px 10px rgba(0,0,0,.12); display:none}
#totop:hover{color:var(--accent); border-color:var(--accent)}
@media (max-width:1020px){
  .layout{display:block; padding:0 14px 60px}
  nav#toc{position:static; max-height:none; flex:none; border-bottom:1px solid var(--line); padding-bottom:12px; margin-bottom:8px}
  main#content{max-width:none}
}
@media print{
  @page{size:A4; margin:15mm 13mm}
  body{background:#fff; font-size:11pt; line-height:1.62}
  header.top{padding:0 0 8px; background:none}
  .doctitle{font-size:19pt}
  nav#toc,#totop,.hint{display:none!important}
  .layout{display:block; padding:0; max-width:none}
  main#content{max-width:none; padding-top:0}
  main#content h1{font-size:16pt; margin:0 0 10px}
  main#content h2{font-size:13pt; page-break-after:avoid; break-after:avoid}
  main#content h3,main#content h4{page-break-after:avoid; break-after:avoid}
  main#content table,.mathblock,main#content blockquote{page-break-inside:avoid; break-inside:avoid}
  main#content a{color:inherit; text-decoration:none}
  main#content pre{white-space:pre-wrap}
}
`;

const JS = `
(function(){
  var links=[].slice.call(document.querySelectorAll('#toc a'));
  var targets=links.map(function(a){return document.getElementById(a.getAttribute('href').slice(1));});
  function upd(){
    var pos=window.scrollY+130, best=0;
    for(var i=0;i<targets.length;i++){
      if(targets[i]&&targets[i].offsetTop<=pos) best=i;
    }
    links.forEach(function(a,i){a.classList.toggle('active',i===best);});
    document.getElementById('totop').style.display=window.scrollY>600?'block':'none';
  }
  window.addEventListener('scroll',upd,{passive:true});
  upd();
  document.getElementById('totop').addEventListener('click',function(){window.scrollTo({top:0,behavior:'smooth'});});
})();
`;

if (!process.env.SKIP_MAIN) main();