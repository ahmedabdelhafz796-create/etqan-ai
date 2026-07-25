/* ============================================================
   E-tqan book authoring DSL → HTML fragments.
   Each helper returns an HTML string. A book is authored as an
   array of chapters; the renderer assembles cover + colophon +
   clickable ToC + chapters into a print-ready document.
   ============================================================ */

let _ids = new Set();
export function resetIds() { _ids = new Set(); }
export function slug(s) {
  let base = String(s).toLowerCase().replace(/[^\w؀-ۿ]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 48) || "sec";
  let id = base, i = 2;
  while (_ids.has(id)) id = `${base}-${i++}`;
  _ids.add(id);
  return id;
}

const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
// lightweight inline markdown: **bold**, *italic*, `code`, [text](url)
export function md(s) {
  return esc(s)
    .replace(/`([^`]+)`/g, (_, c) => `<code>${c}</code>`)
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/(^|[^*])\*([^*\n]+)\*/g, "$1<em>$2</em>")
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
}

/* ---- block helpers ---- */
export const p = (t) => `<p>${md(t)}</p>`;
export const lead = (t) => `<p class="lead">${md(t)}</p>`;
export const h3 = (t) => `<h3 id="${slug(t)}">${md(t)}</h3>`;
export const h4 = (t) => `<h4>${md(t)}</h4>`;
export const ul = (items) => `<ul>${items.map((i) => `<li>${md(i)}</li>`).join("")}</ul>`;
export const ol = (items) => `<ol>${items.map((i) => `<li>${md(i)}</li>`).join("")}</ol>`;
export const divider = () => `<div class="divider">✦ ✦ ✦</div>`;

export function callout(kind, body, label) {
  const labels = { tip: "Pro Tip", warn: "Watch Out", note: "Note", key: "Key Concept", pitfall: "Common Pitfall" };
  const lb = label || labels[kind] || "Note";
  const html = Array.isArray(body) ? body.map((t) => `<p>${md(t)}</p>`).join("") : `<p>${md(body)}</p>`;
  return `<div class="callout ${kind}"><span class="lbl">${lb}</span>${html}</div>`;
}
export const tip = (b, l) => callout("tip", b, l);
export const warn = (b, l) => callout("warn", b, l);
export const note = (b, l) => callout("note", b, l);
export const key = (b, l) => callout("key", b, l);
export const pitfall = (b, l) => callout("pitfall", b, l);

export const pull = (t, who) => `<div class="pull">${md(t)}${who ? `<span class="who">— ${md(who)}</span>` : ""}</div>`;

export function code(lang, src, filename) {
  // store raw; highlighting happens in the browser render pass
  const b64 = Buffer.from(src).toString("base64");
  return `<div class="code"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span>${
    filename ? `<span class="fn">${esc(filename)}</span>` : ""}<span class="lang">${esc(lang)}</span></div>` +
    `<pre><code class="language-${esc(lang)}" data-src="${b64}"></code></pre></div>`;
}

export function table(headers, rows, caption) {
  const th = headers.map((h) => `<th>${md(h)}</th>`).join("");
  const tr = rows.map((r) => `<tr>${r.map((c) => `<td>${md(c)}</td>`).join("")}</tr>`).join("");
  return `<table>${caption ? `<caption>${md(caption)}</caption>` : ""}<thead><tr>${th}</tr></thead><tbody>${tr}</tbody></table>`;
}

export const cards = (cols, items) =>
  `<div class="grid${cols}">${items.map((c) => `<div class="card"><div class="ct">${md(c.t)}</div>${
    c.body ? `<p>${md(c.body)}</p>` : ""}${c.list ? ul(c.list) : ""}${c.code ? code(c.lang || "text", c.code) : ""}</div>`).join("")}</div>`;

export const cheatsheet = (items) => cards(2, items);

export const checklist = (items) =>
  `<ul class="checklist">${items.map((i) => `<li>${md(i)}</li>`).join("")}</ul>`;

export function exercise(title, intro, tasks, tag = "Exercise") {
  return `<div class="exercise"><div class="hd"><span class="tag">${esc(tag)}</span><span class="ti">${md(title)}</span></div>` +
    `<div class="bd">${intro ? `<p>${md(intro)}</p>` : ""}${tasks ? ol(tasks) : ""}</div></div>`;
}

export function project(title, body) {
  const inner = Array.isArray(body) ? body.join("") : body;
  return `<div class="project"><div class="hd"><span class="tag">Project</span><span class="ti">${md(title)}</span></div><div class="bd">${inner}</div></div>`;
}

export function caseStudy(title, body) {
  const inner = Array.isArray(body) ? body.join("") : body;
  return `<div class="casestudy"><div class="hd"><span class="tag">Case Study</span><span class="ti">${md(title)}</span></div><div class="bd">${inner}</div></div>`;
}

export function quiz(items, heading = "Check Your Understanding") {
  const qs = items.map((it, i) => {
    const opts = it.options ? `<ol class="opts">${it.options.map((o) => `<li>${md(o)}</li>`).join("")}</ol>` : "";
    const ans = it.answer ? `<div class="ans"><b>Answer:</b> ${md(it.answer)}${it.explain ? ` — ${md(it.explain)}` : ""}</div>` : "";
    return `<div class="q">${i + 1}. ${md(it.q)}</div>${opts}${ans}`;
  }).join("");
  return `<div class="quiz"><div class="qh">${esc(heading)}</div>${qs}</div>`;
}

export function figure(inner, caption) {
  return `<figure><div class="diagram">${inner}</div>${caption ? `<figcaption>${md(caption)}</figcaption>` : ""}</figure>`;
}

/* Simple SVG flow diagram: array of node labels → horizontal/vertical flow */
export function flow(nodes, { dir = "h", caption } = {}) {
  const w = 760, pad = 12;
  if (dir === "h") {
    const n = nodes.length, bw = (w - pad * 2 - (n - 1) * 34) / n, bh = 58, y = 14;
    let x = pad, svg = "";
    nodes.forEach((lab, i) => {
      svg += box(x, y, bw, bh, lab);
      if (i < n - 1) svg += arrow(x + bw, y + bh / 2, x + bw + 34, y + bh / 2);
      x += bw + 34;
    });
    return figure(`<svg viewBox="0 0 ${w} ${bh + 28}" xmlns="http://www.w3.org/2000/svg" style="width:100%">${svg}</svg>`, caption);
  } else {
    const bw = 320, bh = 50, x = (w - bw) / 2; let y = 12, svg = "";
    nodes.forEach((lab, i) => {
      svg += box(x, y, bw, bh, lab);
      if (i < nodes.length - 1) svg += arrow(x + bw / 2, y + bh, x + bw / 2, y + bh + 26, true);
      y += bh + 26;
    });
    return figure(`<svg viewBox="0 0 ${w} ${y}" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:420px">${svg}</svg>`, caption);
  }
  function box(x, y, w, h, lab) {
    const lines = String(lab).split("\n");
    const t = lines.map((l, i) => `<tspan x="${x + w / 2}" dy="${i === 0 ? 0 : 14}">${esc(l)}</tspan>`).join("");
    return `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="12" fill="var(--accent-soft)" stroke="var(--accent)" stroke-width="1.5"/>` +
      `<text x="${x + w / 2}" y="${y + h / 2 - (lines.length - 1) * 7 + 4}" text-anchor="middle" font-family="Inter" font-size="12" font-weight="600" fill="var(--accent-ink)">${t}</text>`;
  }
  function arrow(x1, y1, x2, y2, v) {
    return `<line x1="${x1}" y1="${y1}" x2="${x2 - (v ? 0 : 6)}" y2="${y2 - (v ? 6 : 0)}" stroke="var(--accent)" stroke-width="2"/>` +
      `<path d="${v ? `M${x2 - 5},${y2 - 6} L${x2 + 5},${y2 - 6} L${x2},${y2} Z` : `M${x2 - 6},${y1 - 5} L${x2 - 6},${y1 + 5} L${x2},${y1} Z`}" fill="var(--accent)"/>`;
  }
}

/* ---- structural ---- */
export function chapter(no, title, { eyebrow, intro, goals } = {}, ...blocks) {
  const id = slug(`ch-${no}-${title}`);
  const goalsHtml = goals
    ? `<div class="goals"><div class="h">By the end of this chapter you will</div><ul>${goals.map((g) => `<li>${md(g)}</li>`).join("")}</ul></div>`
    : "";
  const head = `<div class="chapter-opener"><div class="eyebrow">${esc(eyebrow || "Chapter")}</div>` +
    `<div class="cno">${String(no).padStart(2, "0")}</div><h1>${md(title)}</h1>` +
    `${intro ? `<p class="intro">${md(intro)}</p>` : ""}${goalsHtml}</div>`;
  const body = `<div class="chapter-body"><div class="body">${blocks.join("\n")}</div></div>`;
  return { id, no, title, html: `<section class="chapter" id="${id}">${head}${body}</section>` };
}

/* collect ToC entries: chapters + their h3s */
export function tocFrom(chapters) {
  return chapters.map((c) => {
    const secs = [...c.html.matchAll(/<h3 id="([^"]+)">(.*?)<\/h3>/g)].map((m) => ({ id: m[1], t: m[2].replace(/<[^>]+>/g, "") }));
    return { id: c.id, no: c.no, title: c.title, secs };
  });
}

/* ============================================================
   APPENDIX BLOCKS — summary, cheat sheet, glossary, references,
   learning roadmap. Used to close every E-tqan book with the
   reference material a premium commercial title is expected to have.
   ============================================================ */

/** Chapter summary: the key takeaways, numbered. */
export function summary(items, heading = "Chapter Summary") {
  return `<h3 id="${slug(heading)}">${md(heading)}</h3>` +
    `<div class="callout key"><span class="lbl">${esc(heading)}</span>${ol(items)}</div>`;
}

/**
 * Cheat sheet: compact two-column reference cards.
 * items: [{ t: "Section", rows: [[label, value], …] }]
 */
export function cheatSheet(items, heading = "Cheat Sheet") {
  const cards = items.map((sec) => {
    const rows = (sec.rows || []).map(
      ([k, v]) => `<tr><td style="width:42%"><code>${esc(k)}</code></td><td>${md(v)}</td></tr>`
    ).join("");
    return `<div class="card"><div class="ct">${md(sec.t)}</div>` +
      `<table style="margin:.4em 0 0"><tbody>${rows}</tbody></table></div>`;
  }).join("");
  return `<h3 id="${slug(heading)}">${md(heading)}</h3><div class="grid2">${cards}</div>`;
}

/** Glossary: alphabetical term → definition table. */
export function glossary(entries, heading = "Glossary") {
  const rows = [...entries]
    .sort((a, b) => String(a.term).localeCompare(String(b.term)))
    .map((e) => [`**${e.term}**`, e.def]);
  return `<h3 id="${slug(heading)}">${md(heading)}</h3>` + table(["Term", "Meaning"], rows);
}

/** References & further reading: annotated list. */
export function references(items, heading = "References & Further Reading") {
  const lis = items.map((r) =>
    `<li><strong>${md(r.name)}</strong>${r.note ? ` — ${md(r.note)}` : ""}${r.url ? `<br><span style="font-family:'JetBrains Mono';font-size:.8em;color:var(--ink-faint)">${esc(r.url)}</span>` : ""}</li>`
  ).join("");
  return `<h3 id="${slug(heading)}">${md(heading)}</h3><ul>${lis}</ul>`;
}

/**
 * Learning roadmap: a staged plan table plus a visual flow of the stages.
 * stages: [{ when: "Week 1–2", focus: "…" }]
 */
export function roadmap(stages, heading = "Learning Roadmap") {
  const rows = stages.map((s) => [s.when, s.focus]);
  const flowNodes = stages.map((s) => String(s.when));
  return `<h3 id="${slug(heading)}">${md(heading)}</h3>` +
    table(["Stage", "Focus"], rows) +
    (flowNodes.length >= 2 && flowNodes.length <= 5
      ? flow(flowNodes, { caption: "Your path through this book, stage by stage." })
      : "");
}
