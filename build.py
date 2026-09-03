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
    log(f"baked into index.html ({len(out)//1024} KB). Commit + push to deploy.")

if __name__ == "__main__":
    main()
