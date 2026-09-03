# Lindsey Street District

The official website + business directory for the **Historic Lindsey Street District** in Norman, Oklahoma —
and a lead-generation funnel for **GRID Real Estate**. Live at **[lindseydistrict.com](https://lindseydistrict.com)**,
hosted on **Cloudflare Pages**.

Plain HTML/CSS/JS. The only build step is an optional SEO **prerender** (`build.py`).

---

## What's here

```
index.html        Home: hero, about, directory, deals, map, events, lead funnels, newsletter
submit.html       "List / claim your business" form (prefills from ?business=…)
404.html          Friendly not-found page
css/styles.css    Brand design system (colors, type, components)
js/data.js        ← the content: businesses, categories, deals, events  (EDIT THIS)
js/app.js         Rendering, filtering, search, map, forms, deals unlock, prerender-aware
build.py          SEO prerender → bakes the directory into index.html (static HTML)
assets/           Logos, badge, favicons, brand art
robots.txt        / sitemap.xml — SEO
```

## Editing the directory

Everything the visitor sees lives in **`js/data.js`** — no coding beyond copy/paste.

**Add / edit a business** — copy a block in the `BUSINESSES` array:

```js
{ "name": "Velvet Taco", "category": "food",
  "address": "1440 W Lindsey, Norman, OK",
  "center": "Hollywood Shopping Center",   // optional
  "phone": "(405) 555-0100",               // optional
  "website": "https://…",                  // optional
  "instagram": "https://instagram.com/…",  // optional
  "facebook": "https://facebook.com/…",    // optional
  "featured": true },                      // optional → shows in "Local Favorites"
```

- `category` **must** match a key in `CATEGORIES` at the top of the file
  (`food`, `service`, `beauty`, `shop`, `auto`, `bank`, `smoke`, `gym`, `fun`, `civic`, `education`, `pets`, `worship`).
- Blank/omitted fields are hidden. `"featured": true` promotes a business to the Local Favorites row.
- **Deals** (the email-unlock incentive) and **Events** are the `DEALS` and `EVENTS` arrays in the same file.
  ⚠️ Replace the placeholder deals with **real, business-approved** offers before promoting.

## Leads → GRID Real Estate

Every form (list/claim a business, Live Here, Lease Space, property management, newsletter, deals unlock)
POSTs to the GRID CRM at `portal.thegridre.com` with a `lead_type` / `interest` tag. Config is at the top of
the lead section in `js/app.js` (`LEAD_ENDPOINT`, `GRID_SITE_KEY`).

## The map

Pins are placed **automatically from each business's street address** (approximate). To pin one exactly, add
`"lat": 35.2054, "lng": -97.4620` to it (right-click the spot in Google Maps to get coordinates).
Uses **Leaflet + OpenStreetMap** (free, no API key).

## Build & deploy (Cloudflare Pages)

The site is hosted on Cloudflare Pages and **auto-deploys when you push to `main`**.

For SEO, the directory is **baked into `index.html`** as static HTML (so crawlers and no-JS visitors see all
listings). `build.py` renders the real `app.js`/`data.js` in headless Chrome and writes the generated cards +
`ItemList` JSON-LD back into `index.html` between `<!--DIR:START-->` / `<!--FEAT:START-->` / `<!--LD:START-->`
markers — one source of truth, so the static HTML never drifts. It's idempotent (safe to re-run).

**Whenever you edit `js/data.js`** (add a business, change a deal, etc.):

```bash
python3 build.py            # re-bake index.html
git add -A && git commit -m "update listings" && git push   # auto-deploys
```

To deploy manually instead: `npx wrangler@4 pages deploy . --project-name=lindseydistrict --branch=main`.
The custom domains (`lindseydistrict.com`, `www`) are attached to the Pages project in the Cloudflare dashboard.

> If you edit `index.html` structure by hand, keep the `<!-- …:START/END -->` marker comments intact and
> re-run `python3 build.py` afterward.

## Local preview

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

---

Brand: Historic Lindsey Street District · Norman, OK · [@lindseystreetdistrict](https://www.instagram.com/lindseystreetdistrict)
