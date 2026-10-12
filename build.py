#!/usr/bin/env python3
"""
SEO prerender for lindseydistrict.com — bakes the directory into index.html.
------------------------------------------------------------------------------
Renders the REAL app.js / data.js in headless Chrome, then writes the generated
cards + JSON-LD directly into index.html (between HTML markers). This keeps ONE
source of truth (app.js) so the static HTML can never drift, and — because the
result is committed — EVERY deploy path (Cloudflare auto-deploy on git push, or
manual wrangler) serves the fully static, crawlable directory.

Idempotent: it first resets the marked regions to empty, so re-running always
reflects the current data.js.

Usage:  python3 build.py        # updates index.html in place
Re-run after editing js/data.js, then commit + push (auto-deploys).
"""
import os, re, sys, json, html, subprocess, http.server, socketserver, threading
from urllib.parse import quote

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = 8799
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

def log(m): print(f"[build] {m}")

def reset(src):
    src = re.sub(r'<!--FEAT:START-->.*?<!--FEAT:END-->',
                 '<!--FEAT:START--><div class="dir-grid" id="featuredGrid"></div><!--FEAT:END-->', src, flags=re.S)
    src = re.sub(r'<!--DIR:START-->.*?<!--DIR:END-->',
                 '<!--DIR:START--><div class="dir-grid" id="dirGrid"></div><!--DIR:END-->', src, flags=re.S)
    src = re.sub(r'<!--LD:START-->.*?<!--LD:END-->', '<!--LD:START--><!--LD:END-->', src, flags=re.S)
    src = re.sub(r'<span id="dirCount">[^<]*</span>', '<span id="dirCount">—</span>', src)
    return src

def serve():
    os.chdir(ROOT)
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), http.server.SimpleHTTPRequestHandler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd

def main():
    if not os.path.exists(CHROME):
        log(f"ERROR: Chrome not found at {CHROME}"); sys.exit(1)

    index = os.path.join(ROOT, "index.html")
    clean = reset(open(index).read())
    for marker in ("<!--FEAT:START-->", "<!--DIR:START-->", "<!--LD:START-->"):
        if marker not in clean:
            log(f"ERROR: missing marker {marker} in index.html"); sys.exit(1)

    # temp render page: strip external Leaflet (no network) + append extractor
    pre = re.sub(r'<script src="https://unpkg\.com/leaflet[^>]*></script>\s*', "", clean)
    pre = pre.replace("</body>", """
<script>
window.addEventListener('load', function () {
  var out = {
    featured: (document.getElementById('featuredGrid')||{}).innerHTML || '',
    dir:      (document.getElementById('dirGrid')||{}).innerHTML || '',
    count:    (document.getElementById('dirCount')||{}).textContent || '',
    ld: ''
  };
  document.querySelectorAll('script[type="application/ld+json"]').forEach(function (s) {
    if (s.textContent.indexOf('"ItemList"') > -1) out.ld = s.textContent;
  });
  var t = document.createElement('textarea'); t.id = '__pre';
  t.textContent = JSON.stringify(out); document.body.appendChild(t);
});
</script>
</body>""")
    tmp = os.path.join(ROOT, "__pre.html")
    open(tmp, "w").write(pre)

    httpd = serve()
    try:
        log("rendering with headless Chrome…")
        dump = subprocess.run(
            [CHROME, "--headless=new", "--disable-gpu", "--virtual-time-budget=8000",
             "--dump-dom", f"http://127.0.0.1:{PORT}/__pre.html"],
            capture_output=True, text=True, timeout=90).stdout
    finally:
        httpd.shutdown(); os.remove(tmp)

    m = re.search(r'<textarea id="__pre">(.*)</textarea>', dump, re.S)
    if not m:
        log("ERROR: render produced no payload"); sys.exit(1)
    d = json.loads(html.unescape(m.group(1)))
    feat, dirs, count, ld = d["featured"], d["dir"], d["count"], d["ld"]
    n = dirs.count("<article")
    if n == 0:
        log("ERROR: 0 directory cards rendered"); sys.exit(1)
    log(f"rendered {n} directory cards, {feat.count('<article')} featured, count={count}, ld={'yes' if ld else 'no'}")

    # bake into the clean template
    out = clean
    out = out.replace('<!--FEAT:START--><div class="dir-grid" id="featuredGrid"></div><!--FEAT:END-->',
                      '<!--FEAT:START--><div class="dir-grid" id="featuredGrid">' + feat + '</div><!--FEAT:END-->')
    out = out.replace('<!--DIR:START--><div class="dir-grid" id="dirGrid"></div><!--DIR:END-->',
                      '<!--DIR:START--><div class="dir-grid" id="dirGrid">' + dirs + '</div><!--DIR:END-->')
    if ld:
        out = out.replace('<!--LD:START--><!--LD:END-->',
                          '<!--LD:START--><script type="application/ld+json" id="ld-itemlist">' + ld + '</script><!--LD:END-->')
    if count:
        out = out.replace('<span id="dirCount">—</span>', '<span id="dirCount">' + count + '</span>')

    open(index, "w").write(out)
    log(f"baked into index.html ({len(out)//1024} KB).")

    generate_biz_pages()
    log("done. Commit + push to deploy.")


# ---- business detail pages + sitemap -------------------------------------

def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

def parse_data():
    s = open(os.path.join(ROOT, "js", "data.js")).read()
    businesses = json.loads(re.search(r"const BUSINESSES = (\[.*?\]);", s, re.S).group(1))
    cm = re.search(r"const CATEGORIES = (\{.*?\});", s, re.S).group(1)
    cm = re.sub(r"([{,]\s*)([A-Za-z_]\w*):", r'\1"\2":', cm)  # quote keys
    categories = json.loads(cm)
    return businesses, categories

def esc(x):
    return (str(x).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;").replace("'", "&#39;"))

ICON = {
    "pin": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 12-9 12s-9-5-9-12a9 9 0 0 1 18 0Z"/><circle cx="12" cy="10" r="3"/></svg>',
    "phone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3 19.5 19.5 0 0 1-6-6 19.8 19.8 0 0 1-3-8.6A2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2Z"/></svg>',
    "clock": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
    "shop": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9h18l-1 11H4L3 9Z"/><path d="M8 9V6a4 4 0 0 1 8 0v3"/></svg>',
}

BIZ_HEADER = """<header class="site-header">
  <div class="wrap nav">
    <a class="brand" href="/" aria-label="Lindsey Street District home">
      <img class="brand-badge" src="/assets/badge-transparent.png" alt="Historic Lindsey Street District badge" width="52" height="52">
      <span class="brand-word"><span class="l1">Lindsey</span><span class="l2">STREET DISTRICT</span></span>
    </a>
    <button class="nav-toggle" aria-label="Menu" aria-expanded="false"><span></span><span></span><span></span></button>
    <nav class="nav-links">
      <a href="/#directory">Directory</a>
      <a href="/#map-section">Map</a>
      <a href="/invest">Invest</a>
      <a class="btn btn--red" href="/submit.html">List Your Business</a>
    </nav>
  </div>
</header>"""

BIZ_FOOTER = """<footer class="site-footer">
  <div class="wrap footer-bottom" style="border:0">
    <a href="/" style="color:var(--gold)">Lindsey Street District</a> · Norman, Oklahoma ·
    <a href="/#directory" style="color:#d9cdbd">Browse the directory</a>
  </div>
</footer>
<button id="toTop" class="to-top" aria-label="Back to top">↑</button>
<script>
(function(){var t=document.querySelector('.nav-toggle'),l=document.querySelector('.nav-links');
if(t&&l){t.addEventListener('click',function(){var o=l.classList.toggle('open');t.setAttribute('aria-expanded',o);});}
var b=document.getElementById('toTop');if(b){addEventListener('scroll',function(){b.classList.toggle('show',scrollY>700);},{passive:true});b.addEventListener('click',function(){scrollTo({top:0,behavior:'smooth'});});}})();
</script>"""

def biz_page_html(b, cats, by_cat, by_center):
    cat = cats.get(b["category"], {"label": b["category"], "emoji": "📍"})
    name = b["name"]; addr = b.get("address", "")
    addr_short = re.sub(r",\s*Norman,\s*OK$", "", addr)
    title = f"{name} — {cat['label']} on Lindsey Street, Norman OK"
    desc = f"{name}: {cat['label']} in the Historic Lindsey Street District, Norman OK" + (f" at {addr_short}." if addr_short else ".")

    meta = []
    if addr:
        meta.append(f'<div class="row">{ICON["pin"]}<span>{esc(addr)}{(" · " + esc(b["center"])) if b.get("center") else ""}</span></div>')
    tel = re.sub(r"[^0-9+]", "", b.get("phone", ""))
    if b.get("phone"):
        meta.append(f'<div class="row">{ICON["phone"]}<a href="tel:{esc(tel)}">{esc(b["phone"])}</a></div>')
    if b.get("hours"):
        meta.append(f'<div class="row">{ICON["clock"]}<span>{esc(b["hours"])}</span></div>')

    actions = []
    if addr:
        actions.append(f'<a class="btn btn--teal" href="https://maps.google.com/?q={esc(addr)}" target="_blank" rel="noopener">Directions ↗</a>')
    if b.get("phone"):
        actions.append(f'<a class="btn btn--outline" href="tel:{esc(tel)}">Call</a>')
    if b.get("website"):
        actions.append(f'<a class="btn btn--outline" href="{esc(b["website"])}" target="_blank" rel="noopener">Website ↗</a>')
    if b.get("instagram"):
        actions.append(f'<a class="btn btn--outline" href="{esc(b["instagram"])}" target="_blank" rel="noopener">Instagram ↗</a>')
    if b.get("facebook"):
        actions.append(f'<a class="btn btn--outline" href="{esc(b["facebook"])}" target="_blank" rel="noopener">Facebook ↗</a>')

    # related: same category (exclude self), then same center
    related = [x for x in by_cat.get(b["category"], []) if x["name"] != name][:6]
    rel_html = ""
    if related:
        cards = "".join(
            f'<div class="biz-related-card"><a href="/biz/{slug(x["name"])}.html">{esc(x["name"])}</a>'
            + (f'<span class="ra">{esc(re.sub(r", Norman, OK$", "", x.get("address","")))}</span>' if x.get("address") else "")
            + "</div>"
            for x in related)
        rel_html = f'<section class="biz-related"><h2>More {esc(cat["label"])} on Lindsey Street</h2><div class="biz-related-grid">{cards}</div></section>'

    center_html = ""
    if b.get("center"):
        same = [x for x in by_center.get(b["center"], []) if x["name"] != name][:6]
        if same:
            cards = "".join(
                f'<div class="biz-related-card"><a href="/biz/{slug(x["name"])}.html">{esc(x["name"])}</a>'
                + f'<span class="ra">{esc((cats.get(x["category"],{}) or {}).get("label",""))}</span></div>'
                for x in same)
            center_html = f'<section class="biz-related"><h2>Also at {esc(b["center"])}</h2><div class="biz-related-grid">{cards}</div></section>'

    ld = {
        "@context": "https://schema.org", "@type": "LocalBusiness", "name": name,
        "url": f"https://lindseydistrict.com/biz/{slug(name)}.html",
    }
    if addr:
        ld["address"] = {"@type": "PostalAddress", "streetAddress": addr_short, "addressLocality": "Norman", "addressRegion": "OK"}
    if b.get("phone"): ld["telephone"] = b["phone"]
    if b.get("website"): ld["sameAs"] = [b["website"]]
    crumb = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://lindseydistrict.com/"},
        {"@type": "ListItem", "position": 2, "name": "Directory", "item": "https://lindseydistrict.com/#directory"},
        {"@type": "ListItem", "position": 3, "name": name},
    ]}

    claim = f'/submit.html?business={quote(name)}&category={quote(cat["label"])}'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="https://lindseydistrict.com/biz/{slug(name)}.html">
<meta name="robots" content="index, follow">
<meta property="og:title" content="{esc(name)} — Lindsey Street District">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="business.business">
<meta property="og:url" content="https://lindseydistrict.com/biz/{slug(name)}.html">
<meta property="og:image" content="https://lindseydistrict.com/assets/good-times-await.png">
<meta name="theme-color" content="#141414">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Alfa+Slab+One&family=Bebas+Neue&family=Work+Sans:wght@400;500;600;700&family=Yellowtail&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/styles.css">
<script type="application/ld+json">{json.dumps(ld)}</script>
<script type="application/ld+json">{json.dumps(crumb)}</script>
</head>
<body>
{BIZ_HEADER}
<section class="section wrap">
  <nav class="crumbs"><a href="/">Home</a> / <a href="/#directory">Directory</a> / <span>{esc(cat['label'])}</span></nav>
  <p class="eyebrow">{cat['emoji']} {esc(cat['label'])}</p>
  <h1 class="biz-name">{esc(name)}</h1>
  <div class="biz-meta">{''.join(meta)}</div>
  <div class="biz-actions">{''.join(actions)}</div>
  <p class="biz-intro">{esc(name)} is a {esc(cat['label'].lower())} business in the Historic Lindsey Street District — Norman's walkable live, work &amp; play corridor just west of the University of Oklahoma{(', at ' + esc(addr_short)) if addr_short else ''}.</p>
  <div class="biz-claim">Own or manage {esc(name)}? <a href="{claim}">Claim &amp; update this listing →</a></div>
  {rel_html}
  {center_html}
  <a class="biz-back" href="/#directory">← Back to the directory</a>
</section>
{BIZ_FOOTER}
</body>
</html>"""

def generate_biz_pages():
    businesses, cats = parse_data()
    by_cat, by_center = {}, {}
    for b in businesses:
        by_cat.setdefault(b["category"], []).append(b)
        if b.get("center"):
            by_center.setdefault(b["center"], []).append(b)

    bizdir = os.path.join(ROOT, "biz")
    if os.path.exists(bizdir): shutil.rmtree(bizdir)
    os.makedirs(bizdir)
    for b in businesses:
        open(os.path.join(bizdir, slug(b["name"]) + ".html"), "w").write(
            biz_page_html(b, cats, by_cat, by_center))
    log(f"generated {len(businesses)} business pages in /biz")

    # sitemap: static pages + every business page
    urls = [("https://lindseydistrict.com/", "weekly", "1.0"),
            ("https://lindseydistrict.com/invest.html", "weekly", "0.8"),
            ("https://lindseydistrict.com/submit.html", "monthly", "0.5")]
    urls += [(f"https://lindseydistrict.com/biz/{slug(b['name'])}.html", "monthly", "0.5") for b in businesses]
    body = "\n".join(f"  <url><loc>{u}</loc><changefreq>{c}</changefreq><priority>{p}</priority></url>" for u, c, p in urls)
    open(os.path.join(ROOT, "sitemap.xml"), "w").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "\n</urlset>\n")
    log(f"wrote sitemap.xml ({len(urls)} urls)")


if __name__ == "__main__":
    main()
