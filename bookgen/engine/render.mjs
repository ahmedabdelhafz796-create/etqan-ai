import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { chromium } from "playwright";
import hljs from "highlight.js";
import { tocFrom } from "./dsl.mjs";

/** Highlight all <code data-src="base64"> blocks server-side. */
function highlightCode(html) {
  return html.replace(/<code class="language-(\w+)" data-src="([^"]*)"><\/code>/g, (_, lang, b64) => {
    const src = Buffer.from(b64, "base64").toString("utf8");
    let out;
    try {
      out = hljs.getLanguage(lang) ? hljs.highlight(src, { language: lang }).value : hljs.highlightAuto(src).value;
    } catch {
      out = src.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    }
    return `<code class="language-${lang} hljs">${out}</code>`;
  });
}

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const EXE = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome";

function coverHtml(meta) {
  const dirAttr = meta.dir === "rtl" ? ' dir="rtl"' : "";
  return `<div class="cover"${dirAttr}>
    <div class="grid"></div><div class="halo"></div>
    <div class="cover-inner">
      <div class="brand-row"><div class="monogram">E</div>
        <div class="brand-name">E-TQAN<small>${meta.brandLine || "PREMIUM DIGITAL LIBRARY"}</small></div></div>
      <div class="edition-badge" style="margin-top:26px">${meta.edition || "First Edition · 2026"}</div>
      <div class="kicker">${meta.kicker || "A Complete Practical Guide"}</div>
      <h1 class="title">${meta.title}</h1>
      <div class="subtitle">${meta.subtitle || ""}</div>
      <div class="rule"></div>
      <div class="meta">
        <div>${meta.levelLabel || "Level"}<b>${meta.level || "All levels"}</b></div>
        <div>${meta.langLabel || "Language"}<b>${meta.language || "English"}</b></div>
        <div>${meta.formatLabel || "Format"}<b>Premium PDF</b></div>
      </div>
      <div class="foot"><span>${meta.footLeft || "E-TQAN EDUCATION"}</span><span>${meta.footRight || "ETQAN.AI"}</span></div>
    </div>
  </div>`;
}

function colophonHtml(meta) {
  const dirAttr = meta.dir === "rtl" ? ' dir="rtl"' : "";
  const c = meta.colophon || {};
  return `<div class="colophon"${dirAttr}>
    <div class="mark">E-tqan</div>
    <h2>${meta.title}</h2>
    <div class="fine" style="margin-top:.4em">${c.tagline || meta.subtitle || ""}</div>
    <div class="push fine">
      <p><strong>${c.editionLine || "An E-tqan Premium Edition."}</strong></p>
      ${(c.body || []).map((t) => `<p>${t}</p>`).join("")}
      <p>${c.copyright || `© 2026 E-tqan. All rights reserved. This book is original educational material produced by E-tqan. No part may be reproduced or redistributed without permission.`}</p>
      <p>${c.support || "Support: @Ahm_t_AHZ01 on Telegram."}</p>
    </div>
  </div>`;
}

function tocHtml(chapters, meta) {
  const dirAttr = meta.dir === "rtl" ? ' dir="rtl"' : "";
  const entries = tocFrom(chapters);
  const rows = entries.map((c) => {
    const sub = c.secs.map((s) => `<li class="sec"><a href="#${s.id}"><span class="t">${s.t}</span><span class="dots"></span></a></li>`).join("");
    return `<li><a href="#${c.id}"><span class="n">${String(c.no).padStart(2, "0")}</span><span class="t">${c.title}</span><span class="dots"></span></a></li>${sub}`;
  }).join("");
  return `<div class="toc"${dirAttr}><div class="sub">${meta.tocKicker || "Table of Contents"}</div><h2>${meta.tocTitle || "What's Inside"}</h2><ol>${rows}</ol></div>`;
}

export async function renderBook(book, outPath) {
  const meta = book.meta;
  const chapters = book.chapters;
  const dirAttr = meta.dir === "rtl" ? ' dir="rtl"' : "";
  const themeCss = fs.readFileSync(path.join(__dirname, "theme.css"), "utf8");
  const fontsCss = fs.readFileSync(path.join(__dirname, "fonts.css"), "utf8")
    // make font URLs absolute for the file:// page
    .replace(/url\('fonts\//g, `url('${path.join(__dirname, "..", "fonts")}/`);
  const hljsCss = ""; // token colors are in theme.css

  const body = highlightCode(
    coverHtml(meta) + colophonHtml(meta) + tocHtml(chapters, meta) + chapters.map((c) => c.html).join("\n")
  );
  const html = `<!doctype html><html lang="${meta.lang || "en"}"><head><meta charset="utf-8">
    <style>${fontsCss}</style><style>${themeCss}${hljsCss}</style></head>
    <body data-accent="${meta.accent || "gold"}"${dirAttr}>${body}</body></html>`;

  const tmpHtml = outPath.replace(/\.pdf$/, ".html");
  fs.writeFileSync(tmpHtml, html);

  const browser = await chromium.launch({ executablePath: EXE, args: ["--no-sandbox", "--font-render-hinting=none"] });
  const page = await browser.newPage();
  await page.goto("file://" + tmpHtml, { waitUntil: "networkidle" });
  await page.waitForTimeout(150);

  await page.pdf({
    path: outPath,
    format: "A4",
    printBackground: true,
    displayHeaderFooter: true,
    tagged: true,
    outline: true,
    margin: { top: "0mm", bottom: "14mm", left: "0mm", right: "0mm" },
    headerTemplate: "<div></div>",
    footerTemplate: `<div style="width:100%;font-family:Inter,sans-serif;font-size:7.5pt;color:#9a8f7c;
      padding:0 16mm;display:flex;justify-content:space-between;align-items:center;">
      <span style="letter-spacing:.12em;text-transform:uppercase">${(meta.title || "").replace(/</g, "")}</span>
      <span class="pageNumber"></span></div>`,
  });
  await browser.close();
  fs.rmSync(tmpHtml, { force: true });
  const kb = (fs.statSync(outPath).size / 1024).toFixed(0);
  console.log(`  ✓ ${path.basename(outPath)} (${kb} KB, ${chapters.length} chapters)`);
}
