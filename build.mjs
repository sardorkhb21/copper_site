// Build copperpos.uz into dist/ — one real page per language, for search engines.
//
//   node build.mjs          → writes dist/
//   (deploy) npx wrangler pages deploy dist --project-name copper-site --branch main
//
// WHY: index.html switches language with JavaScript, so a search engine only
// ever saw the Uzbek text — Russian searches ("программа для ресторана") could
// never find the site. This script renders each language into its own URL
// (/ , /ru/ , /en/) from the SAME page and the SAME I18N dictionary, and adds
// what search engines need: canonical + hreflang links, share images, favicons,
// structured data, sitemap.xml, robots.txt and a real 404 page.
//
// index.html stays the one file you edit. Never edit dist/ by hand.

import fs from "node:fs";
import path from "node:path";

const SITE = "https://copperpos.uz";
const ROOT = path.dirname(new URL(import.meta.url).pathname);
const DIST = path.join(ROOT, "dist");
const src = fs.readFileSync(path.join(ROOT, "index.html"), "utf8");

// ── The I18N dictionary, read straight out of index.html ─────────────────
const start = src.indexOf("const I18N =");
const end = src.indexOf("\n};", start);
if (start < 0 || end < 0) throw new Error("I18N dictionary not found in index.html");
const I18N = new Function(`${src.slice(start, end + 3)}\nreturn I18N;`)();

// ── Per-language search text (title / description are what Google shows) ─
const LANGS = {
  uz: {
    url: `${SITE}/`, ogLocale: "uz_UZ",
    title: "Copper POS — restoran va kafe uchun kassa dasturi | O'zbekiston",
    desc: "Kafe, restoran va choyxonalar uchun bulutli kassa dasturi: buyurtmalar, stollar, oshxona printeri, QR menyu, nasiya va hisobotlar. Android planshetda ishlaydi.",
    ogAlt: "Copper POS — restoran va kafe uchun kassa tizimi",
    planNote: "oylik obuna",
  },
  ru: {
    url: `${SITE}/ru/`, ogLocale: "ru_RU",
    title: "Copper POS — программа для ресторана и кафе в Узбекистане",
    desc: "Облачная POS-система для кафе, ресторанов и чайхан: заказы, столы, кухонный принтер, QR-меню, насия (долги) и отчёты. Работает на Android-планшете.",
    ogAlt: "Copper POS — касса для ресторанов и кафе",
    planNote: "ежемесячная подписка",
  },
  en: {
    url: `${SITE}/en/`, ogLocale: "en_US",
    title: "Copper POS — Restaurant & Cafe POS System in Uzbekistan",
    desc: "Cloud POS for cafes, restaurants and teahouses in Uzbekistan: orders, tables, kitchen printing, QR menu ordering, tabs and reports. Runs on Android tablets.",
    ogAlt: "Copper POS — POS for restaurants and cafes",
    planNote: "monthly subscription",
  },
};
const PLANS = [["Standard", "299000"], ["Premium", "399000"]];

const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const attr = (s) => esc(s).replace(/"/g, "&quot;");
const stripTags = (s) => String(s).replace(/<[^>]+>/g, "");

// Replace the text of every data-i18n / data-i18n-html element, exactly as
// applyLang() does in the browser — just ahead of time.
function translate(html, dict) {
  let changed = 0;
  const swap = (re, render) => {
    html = html.replace(re, (m, tag, attrs, key, inner) => {
      if (dict[key] == null) return m;
      const out = render(dict[key]);
      if (out !== inner) changed++;
      return `<${tag}${attrs}>${out}</${tag}>`;
    });
  };
  swap(/<([a-zA-Z0-9]+)(\s[^>]*?\bdata-i18n="([^"]+)"[^>]*)>([\s\S]*?)<\/\1>/g, esc);
  swap(/<([a-zA-Z0-9]+)(\s[^>]*?\bdata-i18n-html="([^"]+)"[^>]*)>([\s\S]*?)<\/\1>/g, (v) => v);
  return { html, changed };
}

// Replace one exact snippet; fail loudly if index.html no longer contains it,
// so a future edit can never silently ship a half-built page.
function must(html, find, repl) {
  const n = html.split(find).length - 1;
  if (n !== 1) throw new Error(`expected exactly 1 match, found ${n}: ${find.slice(0, 70)}`);
  return html.replace(find, () => repl);
}

function headFor(lang) {
  const L = LANGS[lang], d = I18N[lang];
  const faq = [];
  for (let i = 1; d[`q${i}`]; i++) faq.push({
    "@type": "Question", name: d[`q${i}`],
    acceptedAnswer: { "@type": "Answer", text: stripTags(d[`a${i}`]) },
  });
  const ld = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "Organization", "@id": `${SITE}/#org`, name: "Copper", url: `${SITE}/`,
        logo: `${SITE}/icon-512.png`, areaServed: "UZ",
        founder: { "@type": "Person", name: "Sardor Kholmonov" },
        sameAs: ["https://t.me/copperpos", "https://play.google.com/store/apps/details?id=uz.copper.pos"],
        contactPoint: { "@type": "ContactPoint", contactType: "sales", url: "https://t.me/copperpos", availableLanguage: ["uz", "ru", "en"] },
      },
      { "@type": "WebSite", "@id": `${SITE}/#website`, url: `${SITE}/`, name: "Copper POS", publisher: { "@id": `${SITE}/#org` }, inLanguage: ["uz", "ru", "en"] },
      {
        "@type": "SoftwareApplication", name: "Copper POS", url: L.url, inLanguage: lang,
        applicationCategory: "BusinessApplication", operatingSystem: "Android",
        description: L.desc, image: `${SITE}/og-${lang}.png`, publisher: { "@id": `${SITE}/#org` },
        offers: PLANS.map(([name, price]) => ({ "@type": "Offer", name, price, priceCurrency: "UZS", description: L.planNote })),
      },
      { "@type": "FAQPage", inLanguage: lang, mainEntity: faq },
    ],
  };
  const alt = Object.entries(LANGS).map(([l, x]) => `<link rel="alternate" hreflang="${l}" href="${x.url}">`).join("\n");
  const others = Object.entries(LANGS).filter(([l]) => l !== lang)
    .map(([, x]) => `<meta property="og:locale:alternate" content="${x.ogLocale}">`).join("\n");
  return `<title>${esc(L.title)}</title>
<meta name="description" content="${attr(L.desc)}">
<link rel="canonical" href="${L.url}">
${alt}
<link rel="alternate" hreflang="x-default" href="${SITE}/">
<meta name="theme-color" content="#FFFFFF">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Copper POS">
<meta property="og:locale" content="${L.ogLocale}">
${others}
<meta property="og:title" content="${attr(L.title)}">
<meta property="og:description" content="${attr(L.desc)}">
<meta property="og:url" content="${L.url}">
<meta property="og:image" content="${SITE}/og-${lang}.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="${attr(L.ogAlt)}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" type="image/png" sizes="192x192" href="/icon-192.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<script type="application/ld+json">${JSON.stringify(ld).replace(/</g, "\\u003c")}</script>`;
}

function pageFor(lang) {
  const d = I18N[lang];
  let html = src;

  // <head>: everything from <title> to the old data-URI favicon is replaced.
  html = html.replace(/<title>[\s\S]*?<link rel="icon"[^>]*>/, () => headFor(lang));
  html = must(html, '<html lang="uz">', `<html lang="${lang}">`);

  // Language switcher: real links (crawlable), not JS buttons.
  html = must(html,
    `<button data-lang="uz" class="on">UZ</button>
        <button data-lang="ru">RU</button>
        <button data-lang="en">EN</button>`,
    ["uz", "ru", "en"].map((l) =>
      `<a href="${l === "uz" ? "/" : `/${l}/`}" hreflang="${l}" lang="${l}" data-lang="${l}"${l === lang ? ' class="on" aria-current="page"' : ""}>${l.toUpperCase()}</a>`
    ).join("\n        "));
  html = must(html, "  .lang button {", "  .lang a { text-decoration:none; }\n  .lang button, .lang a {");
  html = must(html, "  .lang button.on {", "  .lang button.on, .lang a.on {");
  html = must(html,
    `document.querySelectorAll("#lang button").forEach(b => b.classList.toggle("on", b.dataset.lang === l));`,
    `document.querySelectorAll("#lang a").forEach(b => b.classList.toggle("on", b.dataset.lang === l));`);
  html = must(html, `  try { localStorage.setItem("copper_lang", l); } catch(e){}\n`, "");
  html = must(html,
    `document.querySelectorAll("#lang button").forEach(b => b.addEventListener("click", () => applyLang(b.dataset.lang)));`,
    `document.querySelectorAll("#lang a").forEach(a => a.addEventListener("click", () => { try { localStorage.setItem("copper_lang", a.dataset.lang); } catch(e){} }));`);
  // Start in this page's language. A visitor who CHOSE another language
  // before is sent to it from the home page only (search bots keep no
  // storage, so they always get the page they asked for).
  html = must(html,
    `let start = "uz";
try { const saved = localStorage.getItem("copper_lang"); if (saved && I18N[saved]) start = saved; } catch(e){}
applyLang(start);`,
    `const PAGE_LANG = "${lang}";
try { const saved = localStorage.getItem("copper_lang"); if (PAGE_LANG === "uz" && saved && saved !== "uz" && I18N[saved]) location.replace("/" + saved + "/" + location.hash); } catch(e){}
applyLang(PAGE_LANG);`);

  // Paths must work from /ru/ and /en/ too.
  html = html.replace(/src="images\//g, 'src="/images/');
  html = html.replace(/href="\/privacy\.html"/g, 'href="/privacy"');

  // Photo tiles: describe them, and reserve their space (no layout jump).
  html = html.replace(/<img src="\/images\/type-(\w+)\.jpg" alt=""/g, (m, k) =>
    `<img src="/images/type-${k}.jpg" alt="${attr(d[`type_${k}`] ?? "")}" width="800" height="1100"`);

  // App screenshots: alt text from the dictionary (data-i18n-alt="key").
  html = html.replace(/alt="[^"]*" data-i18n-alt="([^"]+)"/g, (m, k) =>
    d[k] == null ? m : `alt="${attr(d[k])}" data-i18n-alt="${k}"`);

  const { html: out, changed } = translate(html, d);
  return { html: out, changed };
}

// ── Write dist/ ───────────────────────────────────────────────────────────
fs.rmSync(DIST, { recursive: true, force: true });
fs.mkdirSync(DIST, { recursive: true });
const copyDir = (from, to) => {
  fs.mkdirSync(to, { recursive: true });
  for (const n of fs.readdirSync(from)) {
    if (n.startsWith(".")) continue;
    const a = path.join(from, n), b = path.join(to, n);
    fs.statSync(a).isDirectory() ? copyDir(a, b) : fs.copyFileSync(a, b);
  }
};

for (const lang of Object.keys(LANGS)) {
  const { html, changed } = pageFor(lang);
  const file = lang === "uz" ? path.join(DIST, "index.html") : path.join(DIST, lang, "index.html");
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, html);
  console.log(`${lang}: ${path.relative(ROOT, file)}  (${changed} texts translated, ${(html.length / 1024).toFixed(0)} KB)`);
}

// Privacy page: same text, plus favicon + canonical.
let privacy = fs.readFileSync(path.join(ROOT, "privacy.html"), "utf8");
privacy = privacy.replace(/<link rel="icon"[^>]*>/,
  `<link rel="canonical" href="${SITE}/privacy">\n<link rel="icon" href="/favicon.ico" sizes="48x48">\n<link rel="apple-touch-icon" href="/apple-touch-icon.png">`);
fs.writeFileSync(path.join(DIST, "privacy.html"), privacy);

copyDir(path.join(ROOT, "images"), path.join(DIST, "images"));
copyDir(path.join(ROOT, "static"), DIST);

// Sitemap with language alternates.
const today = new Date().toISOString().slice(0, 10);
const alts = Object.entries(LANGS).map(([l, x]) => `    <xhtml:link rel="alternate" hreflang="${l}" href="${x.url}"/>`)
  .concat(`    <xhtml:link rel="alternate" hreflang="x-default" href="${SITE}/"/>`).join("\n");
const urls = Object.values(LANGS).map((x) =>
  `  <url>\n    <loc>${x.url}</loc>\n    <lastmod>${today}</lastmod>\n${alts}\n  </url>`)
  .concat(`  <url>\n    <loc>${SITE}/privacy</loc>\n    <lastmod>${today}</lastmod>\n  </url>`);
fs.writeFileSync(path.join(DIST, "sitemap.xml"),
  `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
${urls.join("\n")}
</urlset>
`);
console.log("dist/ ready:", fs.readdirSync(DIST).join(", "));
