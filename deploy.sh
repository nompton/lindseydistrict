#!/usr/bin/env bash
# Guarded deploy for lindseydistrict.com (Cloudflare Pages).
#
# Deploys the COMMITTED tree (git archive HEAD) — never the working dir — and
# refuses to deploy anything that looks broken. Every step must succeed; a
# failure at any point aborts before wrangler runs.
#
#   ./deploy.sh            # deploy HEAD to production
#
# Why this exists: an earlier ad-hoc deploy ran after `git archive` failed
# (the repo was in iCloud and git objects had been evicted), and pushed an
# empty bundle to production — every page 404'd until it was redeployed.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
PROJECT=lindseydistrict
fail() { echo "deploy.sh: ABORT — $*" >&2; exit 1; }

# 1) iCloud eviction check: dataless files hang or break git reads.
if find . -flags +dataless -print -quit 2>/dev/null | grep -q .; then
  fail "iCloud-evicted (dataless) files in $ROOT. Move the repo out of iCloud or re-clone it."
fi

# 2) Clean, pushed state: deploy exactly what's on origin/main.
[ -z "$(git status --porcelain)" ] || fail "uncommitted changes — commit (and push) first."
git fetch -q origin main || fail "git fetch failed."
[ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ] || fail "HEAD is not origin/main — push or pull first."
SHA="$(git rev-parse HEAD)"

# 3) Build the bundle from the committed tree.
OUT="$(mktemp -d)"; trap 'rm -rf "$OUT"' EXIT
git archive HEAD | tar -x -C "$OUT" || fail "git archive failed."

# 4) Sanity-check the bundle before it goes anywhere near production.
for f in index.html invest.html submit.html 404.html js/app.js js/data.js css/styles.css \
         data/market.json sitemap.xml _headers functions/api/market.js; do
  [ -s "$OUT/$f" ] || fail "bundle is missing $f"
done
BIZ=$(find "$OUT/biz" -name '*.html' | wc -l | tr -d ' ')
[ "$BIZ" -ge 100 ] || fail "only $BIZ business pages in bundle (expected 100+)."
DUPES=$(find "$OUT" -name '* [0-9].*' | wc -l | tr -d ' ')
[ "$DUPES" -eq 0 ] || fail "$DUPES iCloud conflict-copy files ('name 2.html') in bundle."
CARDS=$(grep -o '<article' "$OUT/index.html" | wc -l | tr -d ' ')
[ "$CARDS" -ge 100 ] || fail "index.html has only $CARDS baked cards — run python3 build.py."

echo "deploy.sh: bundle OK — $(find "$OUT" -type f | wc -l | tr -d ' ') files, $BIZ business pages, $CARDS baked cards, commit ${SHA:0:7}"

# 5) Deploy.
npx --yes wrangler@4 pages deploy "$OUT" --project-name="$PROJECT" --branch=main \
  --commit-hash="$SHA" --commit-dirty=false

# 6) Smoke-test production.
sleep 5
for u in / /invest /submit /js/app.js /biz/velvet-taco /api/market; do
  code=$(curl -s -o /dev/null -w '%{http_code}' "https://lindseydistrict.com$u?deploycheck=$SHA")
  [ "$code" = "200" ] || fail "post-deploy check: $u returned $code — roll back in the Cloudflare dashboard."
done
echo "deploy.sh: live and healthy (${SHA:0:7})."
