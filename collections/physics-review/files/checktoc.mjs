// 校验目录锚点：id 唯一、每个目录链接都指向文案一致的标题、章名可跳转
import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = dirname(fileURLToPath(import.meta.url));
const h = readFileSync(join(ROOT, '大学物理乙2复习资料.html'), 'utf8');

/* 1) id 唯一性 */
const ids = [...h.matchAll(/\sid="([^"]+)"/g)].map((m) => m[1]);
const counter = new Map();
ids.forEach((id) => counter.set(id, (counter.get(id) || 0) + 1));
const dups = [...counter.entries()].filter(([, c]) => c > 1);
console.log(`id 总数=${ids.length}  重复 id=${dups.length}` + (dups.length ? ' -> ' + JSON.stringify(dups.slice(0, 6)) : ''));

/* 2) 目录链接核对 */
const navStart = h.indexOf('<nav id="toc">');
const nav = h.slice(navStart, h.indexOf('</nav>', navStart));
const links = [...nav.matchAll(/<a( class="tocfile")? href="#([^"]+)">([^<]*)<\/a>/g)]
  .map((m) => ({ h1: Boolean(m[1]), id: m[2], text: m[3].trim() }));
console.log(`目录链接=${links.length}（章名 ${links.filter((l) => l.h1).length} + 小节 ${links.filter((l) => !l.h1).length}）`);

const plainOf = (s) => s.replace(/<[^>]+>/g, '')
  .replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&').trim();

const headingPos = new Map();
for (const m of h.matchAll(/<h([1-6]) id="([^"]+)">([\s\S]*?)<\/h\1>/g)) {
  headingPos.set(m[2], { level: Number(m[1]), text: plainOf(m[3]), index: m.index });
}

let bad = 0;
for (const l of links) {
  const t = headingPos.get(l.id);
  if (!t) { bad++; console.log(`  ✗ 无对应标题：${l.text} -> #${l.id}`); continue; }
  if (t.text !== l.text) { bad++; console.log(`  ✗ 文案不符：目录「${l.text}」→ 标题「${t.text}」`); }
  if (l.h1 && t.level !== 1) { bad++; console.log(`  ✗ 章名链接指向的不是 h1：${l.text}`); }
  if (!l.h1 && t.level !== 2) { bad++; console.log(`  ✗ 小节链接指向的不是 h2：${l.text}`); }
}
console.log(bad === 0 ? '✓ 目录链接全部指向唯一且文案一致的标题' : `✗ 有 ${bad} 处错配`);

/* 3) 抽查章节锚点位置（应严格递增、且各自指向本章开头） */
const probe = ['大学物理乙（二）小测复习资料 · 使用说明', '三章公式速查表（带适用条件）',
  '第12章 静电场', '第13章 静电场中的导体和电介质', '第14章 电流和磁场', '答案与解析'];
let lastPos = -1, ordered = true;
for (const p of probe) {
  const l = links.find((x) => x.text === p);
  const t = l && headingPos.get(l.id);
  console.log(`  ${p}  ->  #${l ? l.id : '缺失'}  @${t ? t.index : '?'}`);
  if (t) { if (t.index < lastPos) ordered = false; lastPos = t.index; }
}
console.log(ordered ? '✓ 章顺序与锚点位置一致' : '✗ 锚点顺序异常');

process.exit(dups.length === 0 && bad === 0 && ordered ? 0 : 2);
