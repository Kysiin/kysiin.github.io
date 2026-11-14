/* 本地全文搜索：读取 assets/search.json，Ctrl/⌘+K 唤起，↑↓ 选择，Enter 打开。 */
(function () {
  var script = document.currentScript
  var base = script ? script.src.replace(/assets\/search\.js.*$/, '') : ''
  var ver = (script && script.src.match(/[?&]v=([^&]+)/) || [])[1] || ''
  var index = null
  var loading = false
  var active = 0
  var results = []

  var style = document.createElement('style')
  style.textContent = [
    '.efs{position:fixed;inset:0;z-index:200;display:none;background:rgba(0,0,0,.35);padding:8vh 1rem 1rem}',
    '.efs[data-open]{display:block}',
    '.efs-panel{max-width:44rem;margin:0 auto;background:var(--ef-panel);border:1px solid var(--ef-ink);box-shadow:0 8px 40px rgba(0,0,0,.18)}',
    '.efs input{width:100%;box-sizing:border-box;padding:.9rem 1rem;border:0;border-bottom:1px solid var(--ef-rule);' +
      'background:transparent;color:var(--ef-ink);font:inherit;font-size:1rem;outline:none}',
    '.efs ul{list-style:none;margin:0;padding:0;max-height:60vh;overflow:auto;overscroll-behavior:contain}',
    '.efs li a{display:block;padding:.6rem 1rem;border-bottom:1px solid var(--ef-rule);text-decoration:none;color:var(--ef-ink)}',
    '.efs li a[data-active]{background:var(--ef-chip);border-left:3px solid var(--ef-trace);padding-left:calc(1rem - 3px)}',
    '.efs .t{font-weight:600}',
    '.efs .w{display:inline-block;min-width:2.1em;margin-right:.45em;padding:0 .3em;font-size:.66rem;' +
      'line-height:1.6;font-weight:400;text-align:center;border:1px solid var(--ef-rule);' +
      'color:var(--ef-ink-2);vertical-align:.12em}',
    '.efs .w[data-w="课程"],.efs .w[data-w="实验"],.efs .w[data-w="专题"]{border-color:var(--ef-trace);color:var(--ef-ink)}',
    '.efs .m{display:block;color:var(--ef-ink-2);font-size:.78rem;margin-top:.15rem}',
    '.efs .x{display:block;color:var(--ef-ink-2);font-size:.8rem;margin-top:.2rem;',
      'overflow:hidden;text-overflow:ellipsis;white-space:nowrap}',
    '.efs .empty{padding:1.2rem 1rem;color:var(--ef-ink-2);font-size:.9rem}',
    '.efs mark{background:var(--ef-signal);color:var(--ef-on-signal);padding:0 .1em}',
    '.efs-btn{position:relative}',
    '.efs-btn kbd{font-family:var(--ef-font-mono);font-size:.7rem;opacity:.6;margin-left:.4em}'
  ].join('')
  document.head.appendChild(style)

  var overlay = document.createElement('div')
  overlay.className = 'efs'
  overlay.innerHTML =
    '<div class="efs-panel" role="dialog" aria-modal="true" aria-label="搜索资料">' +
    '<input type="search" placeholder="搜索课程、实验、标题或正文…" aria-label="搜索" />' +
    '<ul></ul></div>'
  document.body.appendChild(overlay)
  var input = overlay.querySelector('input')
  var list = overlay.querySelector('ul')

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]
    })
  }

  function load() {
    if (index || loading) return
    loading = true
    var url = base + 'assets/search.json' + (ver ? '?v=' + encodeURIComponent(ver) : '')
    fetch(url).then(function (r) { return r.json() })
      .then(function (data) {
        index = data
        loading = false
        if (overlay.hasAttribute('data-open')) render(input.value)
      })
      .catch(function () { index = []; loading = false })
  }

  function highlight(text, terms) {
    var t = esc(text)
    if (!terms || !terms.length) return t
    var pat = terms.slice().sort(function (a, b) { return b.length - a.length })
      .map(function (s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') })
      .join('|')
    if (!pat) return t
    return t.replace(new RegExp('(' + pat + ')', 'gi'), '<mark>$1</mark>')
  }

  /* 字段权重：课程索引页 > 实验编号 > 标题 > 正文 */
  var ARTICLE_W = { l: 300, t: 180, b: 24 }
  var ARTICLE_TAG = { l: '实验', t: '标题', b: '正文' }
  var COURSE_W = { t: 1000, g: 700, c: 500, a: 450, r: 450, x: 60 }

  function matchScore(value, term) {
    var v = String(value == null ? '' : value).toLowerCase()
    var i = v.indexOf(term)
    if (i < 0) return 0
    var s = 1
    if (i === 0) s += 0.5       // 命中有前缀加分
    if (v === term) s += 1.5    // 整段相等再加分
    return s
  }

  function scoreItem(it, terms) {
    var weights = it.k === 'course' ? COURSE_W : ARTICLE_W
    var total = 0, best = 0, bestKey = ''
    for (var i = 0; i < terms.length; i++) {
      var term = terms[i], local = 0, key = ''
      for (var f in weights) {
        var sc = matchScore(it[f], term) * weights[f]
        if (sc > local) { local = sc; key = f }
      }
      if (!local) return null     // 每个词都要命中
      total += local
      if (local > best) { best = local; bestKey = key }
    }
    if (terms.length > 1) {       // 整串命中再加一次
      var phrase = terms.join(' ')
      for (var f2 in weights) {
        total += matchScore(it[f2], phrase) * weights[f2] * 0.8
      }
    }
    var tag = it.k === 'course'
      ? (it.g || '课程')
      : (ARTICLE_TAG[bestKey] || '正文')
    return { score: total, tag: tag }
  }

  function snippet(it, terms) {
    var text = it.b || it.x || ''
    if (!text) return ''
    var low = text.toLowerCase(), pos = -1
    for (var i = 0; i < terms.length; i++) {
      var p = low.indexOf(terms[i])
      if (p >= 0 && (pos < 0 || p < pos)) pos = p
    }
    if (pos < 0) return text.slice(0, 160)
    var start = Math.max(0, pos - 40)
    var end = Math.min(text.length, pos + 120)
    return (start ? '…' : '') + text.slice(start, end) + (end < text.length ? '…' : '')
  }

  function render(q) {
    var terms = q.toLowerCase().split(/\s+/).filter(Boolean)
    if (!terms.length) {
      list.innerHTML = '<li><span class="empty">输入关键词开始搜索；按 课程 / 实验 / 标题 / 正文 的顺序命中。</span></li>'
      active = 0
      return
    }

    var scored = []
    ;(index || []).forEach(function (it, i) {
      var s = scoreItem(it, terms)
      if (s) scored.push({ it: it, score: s.score, tag: s.tag, i: i })
    })
    scored.sort(function (a, b) {
      if (b.score !== a.score) return b.score - a.score
      if (a.it.k !== b.it.k) return a.it.k === 'course' ? -1 : 1
      var la = (a.it.t || '').length, lb = (b.it.t || '').length
      if (la !== lb) return la - lb
      return a.i - b.i
    })
    var top = scored.slice(0, 30)
    results = top.map(function (x) { return x.it })

    if (!top.length) {
      list.innerHTML = '<li><span class="empty">没有找到匹配的内容。</span></li>'
      return
    }
    active = 0
    list.innerHTML = top.map(function (r, i) {
      var it = r.it
      var meta = it.k === 'course'
        ? esc(it.c || '') + (it.n ? ' · ' + it.n + ' 篇文章' : '')
        : highlight(it.c, terms) + (it.s ? ' · ' + esc(it.s) : '') + (it.l ? ' · ' + esc(it.l) : '')
      return '<li><a href="' + base + it.u + '"' + (i === 0 ? ' data-active' : '') + '>' +
        '<span class="t"><span class="w" data-w="' + esc(r.tag) + '">' + esc(r.tag) + '</span>' +
        highlight(it.t, terms) + '</span>' +
        '<span class="m">' + meta + '</span>' +
        '<span class="x">' + highlight(snippet(it, terms), terms) + '</span></a></li>'
    }).join('')
  }

  function open() {
    load()
    overlay.setAttribute('data-open', '')
    input.value = ''
    render('')
    setTimeout(function () { input.focus() }, 20)
  }

  function close() {
    overlay.removeAttribute('data-open')
  }

  function move(step) {
    var links = list.querySelectorAll('a')
    if (!links.length) return
    links[active].removeAttribute('data-active')
    active = (active + step + links.length) % links.length
    links[active].setAttribute('data-active', '')
    links[active].scrollIntoView({ block: 'nearest' })
  }

  input.addEventListener('input', function () { render(input.value) })
  overlay.addEventListener('click', function (e) { if (e.target === overlay) close() })
  // 滚轮/触摸在结果列表以外不穿透到背后的页面（页面滚动条保持可见、不隐藏）
  function containScroll(e) {
    var t = e.target
    if (t && t.closest && t.closest('.efs ul')) return
    e.preventDefault()
  }
  overlay.addEventListener('wheel', containScroll, { passive: false })
  overlay.addEventListener('touchmove', containScroll, { passive: false })
  document.addEventListener('keydown', function (e) {
    var openNow = overlay.hasAttribute('data-open')
    if ((e.key === 'k' || e.key === 'K') && (e.metaKey || e.ctrlKey)) {
      e.preventDefault()
      openNow ? close() : open()
      return
    }
    if (!openNow) return
    if (e.key === 'Escape') { close(); return }
    if (e.key === 'ArrowDown') { e.preventDefault(); move(1) }
    if (e.key === 'ArrowUp') { e.preventDefault(); move(-1) }
    if (e.key === 'Enter') {
      var links = list.querySelectorAll('a')
      if (links[active]) window.location.href = links[active].getAttribute('href')
    }
  })

  // 顶栏按钮（各页面只放一个占位的 <span data-search-slot>）
  document.querySelectorAll('[data-search-slot]').forEach(function (slot) {
    var btn = document.createElement('button')
    btn.type = 'button'
    btn.className = 'ef-btn small efs-btn'
    btn.innerHTML = '搜索<kbd>⌘K</kbd>'
    btn.addEventListener('click', open)
    slot.replaceWith(btn)
  })
})()
