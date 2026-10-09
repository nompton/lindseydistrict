/**
 * GET /api/market — Lindsey Street corridor market snapshot.
 *
 * Cloudflare Pages Function. Proxies GRID's ATLAS market data SERVER-SIDE so the
 * API key never reaches the browser. Returns a stable JSON shape the front-end
 * widget renders.
 *
 * To go live, set these in the Pages project (Settings → Environment variables,
 * or `npx wrangler pages secret put ATLAS_API_KEY`):
 *   ATLAS_API_URL  – the ATLAS endpoint returning Lindsey-corridor stats
 *   ATLAS_API_KEY  – bearer token (optional, if ATLAS needs auth)
 * Then map ATLAS's fields to `stats` in the TODO below and flip source → "live".
 *
 * Until configured it returns source:"placeholder" with null values, and the
 * widget shows a tasteful "live market data coming soon" state (no fake numbers).
 */
export async function onRequestGet({ env }) {
  const snapshot = {
    corridor: "W Lindsey St · Norman, OK",
    period: "",
    source: "placeholder",
    stats: [
      { key: "lease",   label: "Avg asking lease",   unit: "/sq ft/yr", value: null },
      { key: "vacancy", label: "Vacancy rate",       unit: "%",         value: null },
      { key: "avail",   label: "Spaces available",   unit: "",          value: null },
      { key: "dom",     label: "Avg days on market", unit: "days",      value: null },
    ],
    note: "Live ATLAS market data coming soon.",
  };

  const url = env && env.ATLAS_API_URL;
  if (url) {
    try {
      const res = await fetch(url, {
        headers: env.ATLAS_API_KEY ? { Authorization: `Bearer ${env.ATLAS_API_KEY}` } : {},
        cf: { cacheTtl: 1800, cacheEverything: true }, // edge-cache 30 min
      });
      if (res.ok) {
        const d = await res.json();
        // TODO: map ATLAS response → stats (field names below are placeholders):
        //   snapshot.stats[0].value = d.avg_lease_rate;      // e.g. "18–24"
        //   snapshot.stats[1].value = d.vacancy_rate;        // e.g. 7.4
        //   snapshot.stats[2].value = d.available_spaces;    // e.g. 12
        //   snapshot.stats[3].value = d.avg_days_on_market;  // e.g. 96
        //   snapshot.period = d.period;                      // e.g. "Oct 2026"
        //   snapshot.source = "live";
        //   snapshot.note   = "";
        // Until the mapping is filled in, surface the raw payload for wiring:
        return json({ ...snapshot, note: "ATLAS reached — map fields in functions/api/market.js", _atlas: d });
      }
    } catch (_) {
      // fall through to placeholder
    }
  }

  return json(snapshot);
}

function json(obj) {
  return new Response(JSON.stringify(obj), {
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "public, max-age=900",
    },
  });
}
