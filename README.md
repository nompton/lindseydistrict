# Lindsey Street District

The official website + business directory for the **Historic Lindsey Street District** in Norman, Oklahoma.
Static site (plain HTML/CSS/JS, no build step) — designed to deploy on GitHub Pages at **lindseydistrict.com**.

---

## What's here

```
index.html        Home: hero, about, directory (search + category filters), map, events, get-listed
submit.html       "List your business" form
404.html          Friendly not-found page
css/styles.css    Brand design system (colors, type, components)
js/data.js        ← the directory content: businesses, categories, events  (EDIT THIS)
js/app.js         Rendering, filtering, search, map, mobile nav
assets/           Logos, badge, favicons, brand art
CNAME             Custom domain for GitHub Pages (lindseydistrict.com)
robots.txt        / sitemap.xml — SEO
```

## Editing the directory

Everything the visitor sees in the directory lives in **`js/data.js`** — no coding required beyond copy/paste.

**Add or edit a business** — copy a block in the `BUSINESSES` array and fill it in:

```js
{ "name": "Velvet Taco", "category": "food",
  "address": "1440 W Lindsey, Norman, OK",
  "center": "Hollywood Shopping Center",   // optional
  "phone": "(405) 555-0100",               // optional
  "website": "https://…",                  // optional
  "instagram": "https://instagram.com/…",  // optional
  "facebook": "https://facebook.com/…" },  // optional
```

- `category` **must** match a key in the `CATEGORIES` object at the top of the file
  (`food`, `service`, `beauty`, `shop`, `auto`, `bank`, `smoke`, `gym`, `fun`, `civic`, `education`, `pets`, `worship`).
- Any field you leave out is simply hidden on the card.
- To add a **new category**, add a line to `CATEGORIES` (with a label + emoji), then use its key on businesses.

**Events** — edit the `EVENTS` array in the same file.

## The map

Pins are placed **automatically from each business's street address** along Lindsey Street, so the map
populates with zero extra work. Positions are **approximate** (good enough to show the general layout).
To pin a business precisely, add exact coordinates to it:

```js
{ "name": "…", "category": "…", "address": "…", "lat": 35.2054, "lng": -97.4620 },
```

Get coordinates by right-clicking the spot in Google Maps → the lat/lng shows at the top.
The map uses **Leaflet + OpenStreetMap** (free, no API key).

## Making the "List your business" form actually send

The form currently shows a friendly on-page confirmation (no backend). To receive real submissions,
create a free endpoint at **[Formspree](https://formspree.io)** and set it on the form in `submit.html`:

```html
<form id="submitForm" action="https://formspree.io/f/XXXXXXX" method="POST">
```

Also update the fallback email in `submit.html` (currently `hello@lindseydistrict.com`).

## Deploying to GitHub Pages

1. Create a GitHub repo and push this folder to it.
2. Repo **Settings → Pages** → Source: `main` branch, `/ (root)`.
3. The included `CNAME` sets the custom domain to `lindseydistrict.com`. In your domain registrar's DNS,
   point the domain at GitHub Pages:
   - `A` records for the apex → `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - `CNAME` for `www` → `<your-username>.github.io`
4. Back in Settings → Pages, tick **Enforce HTTPS** once the certificate is issued.

## Local preview

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

---

Brand: Historic Lindsey Street District · Norman, OK · [@lindseystreetdistrict](https://www.instagram.com/lindseystreetdistrict)
