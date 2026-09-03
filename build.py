#!/usr/bin/env python3
"""
Prerender build for lindseydistrict.com
---------------------------------------
Produces a deployable ./dist with the directory baked into static HTML for SEO.

How it works: it loads the real index.html in headless Chrome so the actual
app.js / data.js render the cards + JSON-LD, extracts that output, and injects
it into dist/index.html. This keeps ONE source of truth (app.js) — the static
HTML can never drift from the live renderer.

Usage:  python3 build.py         # writes ./dist
Then deploy ./dist (see README / deploy command).
Re-run after editing js/data.js so the static output stays current.
"""
import os, re, sys, json, html, shutil, subprocess, time, http.server, socketserver, threading

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")
PORT = 8799
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
COPY = ["assets", "css", "js", "submit.html", "404.html", "robots.txt", "sitemap.xml"]

def log(m): print(f"[build] {m}")

def serve():
    os.chdir(ROOT)
    handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd

def main():
    if not os.path.exists(CHROME):
        log(f"ERROR: Chrome not found at {CHROME}"); sys.exit(1)

    src = open(os.path.join(ROOT, "index.html")).read()

    # 1) temp page: strip external Leaflet (avoid network) + append an extractor
    pre = re.sub(r'<script src="https://unpkg\.com/leaflet[^>]*></script>\s*', "", src)
    extractor = """
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
  var t = document.createElement('textarea');
  t.id = '__pre';
  t.textContent = JSON.stringify(out);
  document.body.appendChild(t);
});
</script>
"""
    pre = pre.replace("</body>", extractor + "\n</body>")
    tmp = os.path.join(ROOT, "__pre.html")
    open(tmp, "w").write(pre)

    httpd = serve()
    try:
        log("rendering with headless Chrome…")
        dump = subprocess.run(
            [CHROME, "--headless=new", "--disable-gpu", "--virtual-time-budget=8000",
             "--dump-dom", f"http://127.0.0.1:{PORT}/__pre.html"],
            capture_output=True, text=True, timeout=90,
        ).stdout
    finally:
        httpd.shutdown()
        os.remove(tmp)

    m = re.search(r'<textarea id="__pre">(.*)</textarea>', dump, re.S)
    if not m:
        log("ERROR: could not find prerender payload (render failed)"); sys.exit(1)
    data = json.loads(html.unescape(m.group(1)))
    feat, dirs, count, ld = data["featured"], data["dir"], data["count"], data["ld"]
    n_dir = dirs.count("<article")
    n_feat = feat.count("<article")
    if n_dir == 0:
        log("ERROR: directory rendered 0 cards"); sys.exit(1)
    log(f"rendered {n_dir} directory cards, {n_feat} featured, count='{count}', ld={'yes' if ld else 'no'}")

    # 2) build dist/index.html from clean source with content injected
    out = src
    out = out.replace('id="featuredGrid"></div>', 'id="featuredGrid">' + feat + '</div>')
    out = out.replace('id="dirGrid"></div>', 'id="dirGrid">' + dirs + '</div>')
    if count:
        out = out.replace('<span id="dirCount">—</span>', '<span id="dirCount">' + count + '</span>')
    if ld:
        out = out.replace("</head>", '<script type="application/ld+json" id="ld-itemlist">' + ld + '</script>\n</head>')

    # 3) assemble dist/
    if os.path.exists(DIST): shutil.rmtree(DIST)
    os.makedirs(DIST)
    for item in COPY:
        s = os.path.join(ROOT, item)
        d = os.path.join(DIST, item)
        if os.path.isdir(s): shutil.copytree(s, d)
        elif os.path.exists(s): shutil.copy2(s, d)
    open(os.path.join(DIST, "index.html"), "w").write(out)
    # CNAME is not needed on Cloudflare Pages (custom domain set in dashboard)
    log(f"wrote {DIST}")
    log("done. Deploy ./dist")

if __name__ == "__main__":
    main()
