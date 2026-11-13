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
import os, re, sys, json, html, shutil, hashlib, subprocess, http.server, socketserver, threading
from urllib.parse import quote

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = 0  # 0 = let the OS pick a free port (avoids clashing with wrangler dev, etc.)
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
    socketserver.TCPServer.allow_reuse_address = True
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
             "--dump-dom", f"http://127.0.0.1:{httpd.server_address[1]}/__pre.html"],
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
    generate_category_pages()
    stamp_assets()
    log("done. Commit + push to deploy.")


# ---- business detail pages + sitemap -------------------------------------

def slug(name):
    # Must match slug() in js/app.js. Accents are stripped, not dropped (ñ -> n).
    import unicodedata
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_name.lower()).strip("-")

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
      <img class="brand-badge" src="/assets/badge-104.png" alt="Historic Lindsey Street District badge" width="52" height="52">
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

# ---- category landing pages (SEO) -----------------------------------------
# One page per category with at least MIN_CATEGORY_SIZE businesses; smaller
# categories would be thin content. Slugs are stable public URLs.
MIN_CATEGORY_SIZE = 3
CATEGORY_PAGES = {
    "food":    {"slug": "restaurants",   "h1": "Restaurants & Food on Lindsey Street",    "blurb": "Restaurants, drive-ins, coffee, tea, and quick bites."},
    "service": {"slug": "services",      "h1": "Services on Lindsey Street",              "blurb": "Insurance, real estate, legal, tax, repair, wireless, and other everyday services."},
    "beauty":  {"slug": "health-beauty", "h1": "Health & Beauty on Lindsey Street",       "blurb": "Salons, barbers, nails, massage, dental, pharmacy, and urgent care."},
    "shop":    {"slug": "shops",         "h1": "Shops on Lindsey Street",                 "blurb": "Grocery, discount, thrift, specialty, and seasonal shops."},
    "auto":    {"slug": "auto",          "h1": "Auto Repair & Service on Lindsey Street", "blurb": "Tires, oil changes, repair, parts, and fuel."},
    "bank":    {"slug": "banks",         "h1": "Banks & Lenders on Lindsey Street",       "blurb": "Banks, credit unions, and consumer lenders."},
    "smoke":   {"slug": "smoke-vape",    "h1": "Smoke & Vape Shops on Lindsey Street",    "blurb": "Vape, CBD, and dispensaries."},
    "gym":     {"slug": "fitness",       "h1": "Gyms & Fitness on Lindsey Street",        "blurb": "Gyms and training studios."},
}

def category_page_keys(businesses):
    counts = {}
    for b in businesses: counts[b["category"]] = counts.get(b["category"], 0) + 1
    return [k for k in CATEGORY_PAGES if counts.get(k, 0) >= MIN_CATEGORY_SIZE]

def category_url(key):
    # Extensionless: Cloudflare Pages 308-redirects /x.html → /x, so canonicals,
    # sitemap and links must use the final URL (the FILE is still <slug>.html).
    return f"/category/{CATEGORY_PAGES[key]['slug']}"

def biz_page_html(b, cats, by_cat, by_center, cat_keys=()):
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
        "url": f"https://lindseydistrict.com/biz/{slug(name)}",
    }
    if addr:
        ld["address"] = {"@type": "PostalAddress", "streetAddress": addr_short, "addressLocality": "Norman", "addressRegion": "OK"}
    if b.get("phone"): ld["telephone"] = b["phone"]
    if b.get("website"): ld["sameAs"] = [b["website"]]
    if isinstance(b.get("lat"), (int, float)) and isinstance(b.get("lng"), (int, float)):
        ld["geo"] = {"@type": "GeoCoordinates", "latitude": b["lat"], "longitude": b["lng"]}
    crumb = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://lindseydistrict.com/"},
        {"@type": "ListItem", "position": 2, "name": "Directory", "item": "https://lindseydistrict.com/#directory"},
    ] + ([{"@type": "ListItem", "position": 3, "name": cat["label"], "item": "https://lindseydistrict.com" + category_url(b["category"])},
          {"@type": "ListItem", "position": 4, "name": name}] if b["category"] in cat_keys else
         [{"@type": "ListItem", "position": 3, "name": name}])}

    claim = f'/submit.html?business={quote(name)}&category={quote(cat["label"])}'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="https://lindseydistrict.com/biz/{slug(name)}">
<meta name="robots" content="index, follow">
<meta property="og:title" content="{esc(name)} — Lindsey Street District">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="business.business">
<meta property="og:url" content="https://lindseydistrict.com/biz/{slug(name)}">
<meta property="og:image" content="https://lindseydistrict.com/assets/og-card.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://lindseydistrict.com/assets/og-card.png">
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
  <nav class="crumbs"><a href="/">Home</a> / <a href="/#directory">Directory</a> / {(f'<a href="{category_url(b["category"])}">' + esc(cat['label']) + '</a>') if b["category"] in cat_keys else '<span>' + esc(cat['label']) + '</span>'}</nav>
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

    cat_keys = category_page_keys(businesses)
    bizdir = os.path.join(ROOT, "biz")
    if os.path.exists(bizdir): shutil.rmtree(bizdir)
    os.makedirs(bizdir)
    for b in businesses:
        open(os.path.join(bizdir, slug(b["name"]) + ".html"), "w").write(
            biz_page_html(b, cats, by_cat, by_center, cat_keys))
    log(f"generated {len(businesses)} business pages in /biz")

    # sitemap: static pages + every business page
    urls = [("https://lindseydistrict.com/", "weekly", "1.0"),
            ("https://lindseydistrict.com/invest", "weekly", "0.8"),
            ("https://lindseydistrict.com/submit", "monthly", "0.5")]
    urls += [(f"https://lindseydistrict.com{category_url(k)}", "weekly", "0.7") for k in cat_keys]
    urls += [(f"https://lindseydistrict.com/biz/{slug(b['name'])}", "monthly", "0.5") for b in businesses]
    body = "\n".join(f"  <url><loc>{u}</loc><changefreq>{c}</changefreq><priority>{p}</priority></url>" for u, c, p in urls)
    open(os.path.join(ROOT, "sitemap.xml"), "w").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "\n</urlset>\n")
    log(f"wrote sitemap.xml ({len(urls)} urls)")


def category_page_html(key, items, cats, cat_keys):
    c = CATEGORY_PAGES[key]; cat = cats.get(key, {"label": key, "emoji": ""})
    url = "https://lindseydistrict.com" + category_url(key)
    n = len(items)
    title = f"{c['h1']}, Norman OK"
    names = ", ".join(x["name"] for x in items[:4])
    desc = f"{n} {cat['label'].lower()} businesses along W Lindsey Street in Norman, OK, including {names}."
    cards = []
    for x in items:
        sub = re.sub(r",\s*Norman,\s*OK$", "", x.get("address", ""))
        if x.get("center"): sub += f" · {x['center']}"
        tel = re.sub(r"[^0-9+]", "", x.get("phone", ""))
        phone = f'<span class="ra"><a href="tel:{esc(tel)}">{esc(x["phone"])}</a></span>' if x.get("phone") else ""
        fav = ' <span class="cat-fav">★ Local Favorite</span>' if x.get("featured") else ""
        cards.append(f'<div class="biz-related-card"><a href="/biz/{slug(x["name"])}.html">{esc(x["name"])}</a>{fav}'
                     f'<span class="ra">{esc(sub)}</span>{phone}</div>')
    others = " · ".join(f'<a href="{category_url(k)}">{esc(cats.get(k, {}).get("label", k))}</a>' for k in cat_keys if k != key)
    ld_list = {"@context": "https://schema.org", "@type": "ItemList", "name": c["h1"], "numberOfItems": n,
               "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": f"https://lindseydistrict.com/biz/{slug(x['name'])}", "name": x["name"]} for i, x in enumerate(items)]}
    ld_crumb = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://lindseydistrict.com/"},
        {"@type": "ListItem", "position": 2, "name": "Directory", "item": "https://lindseydistrict.com/#directory"},
        {"@type": "ListItem", "position": 3, "name": cat["label"]}]}
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | Lindsey Street District</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{esc(c['h1'])}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:image" content="https://lindseydistrict.com/assets/og-card.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://lindseydistrict.com/assets/og-card.png">
<meta name="theme-color" content="#141414">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Alfa+Slab+One&family=Bebas+Neue&family=Work+Sans:wght@400;500;600;700&family=Yellowtail&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/styles.css">
<script type="application/ld+json">{json.dumps(ld_list, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(ld_crumb, ensure_ascii=False)}</script>
</head>
<body>
{BIZ_HEADER}
<section class="section wrap">
  <nav class="crumbs"><a href="/">Home</a> / <a href="/#directory">Directory</a> / <span>{esc(cat['label'])}</span></nav>
  <p class="eyebrow">{cat.get('emoji', '')} {esc(cat['label'])}</p>
  <h1 class="biz-name">{esc(c['h1'])}</h1>
  <p class="biz-intro">{esc(c['blurb'])} {n} businesses along W Lindsey Street in Norman, Oklahoma, from the OU campus west to I-35.</p>
  <div class="biz-related-grid cat-grid">{''.join(cards)}</div>
  <div class="biz-claim">Run a {esc(cat['label'].lower())} business on Lindsey that's missing or out of date here? <a href="/submit.html">List or update it free →</a></div>
  <p class="cat-links">More on Lindsey Street: {others}</p>
  <a class="biz-back" href="/#directory">← Back to the full directory</a>
</section>
{BIZ_FOOTER}
</body>
</html>"""

def generate_category_pages():
    businesses, cats = parse_data()
    keys = category_page_keys(businesses)
    outdir = os.path.join(ROOT, "category")
    if os.path.exists(outdir): shutil.rmtree(outdir)
    os.makedirs(outdir)
    for k in keys:
        items = sorted([b for b in businesses if b["category"] == k], key=lambda b: (not b.get("featured"), b["name"].lower()))
        open(os.path.join(outdir, CATEGORY_PAGES[k]["slug"] + ".html"), "w").write(category_page_html(k, items, cats, keys))
    log(f"generated {len(keys)} category pages in /category")


# ---- cache-busting: fingerprint CSS/JS references --------------------------
# Cloudflare serves css/js with a 4h browser cache, but HTML with max-age=0.
# Stamping each reference with a content hash (?v=xxxxxxxx) means fresh HTML
# always points at the matching JS/CSS, so a deploy never pairs new HTML with
# a stale cached script.
ASSETS = ["css/styles.css", "js/app.js", "js/data.js"]

def asset_hash(rel):
    return hashlib.sha1(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()[:8]

def stamp_assets():
    hashes = {a: asset_hash(a) for a in ASSETS}
    pat = re.compile(r'((?:href|src)=")(/?)(' + "|".join(re.escape(a) for a in ASSETS) + r')(?:\?v=[0-9a-f]+)?(")')
    files = [os.path.join(ROOT, f) for f in ("index.html", "invest.html", "submit.html", "404.html")]
    for sub in ("biz", "category"):
        d = os.path.join(ROOT, sub)
        if os.path.isdir(d):
            files += [os.path.join(d, f) for f in os.listdir(d) if f.endswith(".html")]
    n = 0
    for f in files:
        if not os.path.exists(f): continue
        t = open(f).read()
        t2 = pat.sub(lambda m: f'{m.group(1)}{m.group(2)}{m.group(3)}?v={hashes[m.group(3)]}{m.group(4)}', t)
        if t2 != t:
            open(f, "w").write(t2); n += 1
    log("stamped asset versions " + ", ".join(f"{a.split('/')[-1]}={h}" for a, h in hashes.items()) + f" into {n} files")


if __name__ == "__main__":
    main()
