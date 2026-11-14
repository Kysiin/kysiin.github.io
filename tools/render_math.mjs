#!/usr/bin/env node
/* Build-time LaTeX → CHTML (MathJax v3 modular API, loaded from MATHJAX_ROOT).
   stdin : {"items":[{"id":"m1","tex":"E=mc^2","display":false}, ...]}
   stdout: {"__css__":"<stylesheet text>","m1":"<mjx-container …>…</mjx-container>", ...}
   Fonts are referenced as fonts/<name>.woff, relative to the stylesheet.
*/
import path from 'node:path'
import { pathToFileURL } from 'node:url'

const root = process.env.MATHJAX_ROOT
if (!root) {
  process.stderr.write('MATHJAX_ROOT is not set\n')
  process.exit(2)
}

const load = async (rel) => import(pathToFileURL(path.join(root, rel)).href)

const { mathjax } = await load('js/mathjax.js')
const { TeX } = await load('js/input/tex.js')
const { CHTML } = await load('js/output/chtml.js')
const { liteAdaptor } = await load('js/adaptors/liteAdaptor.js')
const { RegisterHTMLHandler } = await load('js/handlers/html.js')
const { AllPackages } = await load('js/input/tex/AllPackages.js')

const adaptor = liteAdaptor()
RegisterHTMLHandler(adaptor)
const tex = new TeX({ packages: AllPackages })
const chtml = new CHTML({ fontURL: 'fonts' })
const doc = mathjax.document('', { InputJax: tex, OutputJax: chtml })

let buf = ''
process.stdin.setEncoding('utf8')
for await (const chunk of process.stdin) buf += chunk

const input = JSON.parse(buf || '{}')
const out = {}
for (const it of input.items || []) {
  try {
    const node = doc.convert(it.tex, { display: !!it.display })
    out[it.id] = adaptor.outerHTML(node)
  } catch (e) {
    out[it.id] = '<span class="ef-field">［公式渲染失败］</span>'
  }
}
out.__css__ = adaptor.textContent(chtml.styleSheet(doc))
process.stdout.write(JSON.stringify(out))
