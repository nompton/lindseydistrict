/**
 * GET /api/market — Norman / Lindsey corridor market data.
 *
 * Order of precedence:
 *   1. ATLAS live (if ATLAS_API_URL is set in the Pages env) — proxied
 *      server-side so the API key never reaches the browser. Map its fields in
 *      the TODO below and set source = "live".
 *   2. The committed public-records snapshot at /data/market.json
 *      (source = "snapshot", dated). Refresh that file to update the numbers.
 */
export async function onRequestGet({ env, request }) {
  const snapshot = await loadSnapshot(env, request);

  if (env && env.ATLAS_API_URL) {
    try {
      const res = await fetch(env.ATLAS_API_URL, {
        headers: env.ATLAS_API_KEY ? { Authorization: `Bearer ${env.ATLAS_API_KEY}` } : {},
        cf: { cacheTtl: 1800, cacheEverything: true },
      });
      if (res.ok) {
        const d = await res.json();
        // TODO: map ATLAS fields onto snapshot.stats, set snapshot.period,
        // then snapshot.source = "live". Until then, expose the raw payload.
        return json({ ...snapshot, _atlas: d });
      }
    } catch (_) { /* fall through to snapshot */ }
  }

  return json(snapshot);
}

async function loadSnapshot(env, request) {
  try {
    const res = await env.ASSETS.fetch(new URL("/data/market.json", request.url));
    if (res.ok) return await res.json();
  } catch (_) { /* fall through */ }
  return { source: "placeholder", period: "", stats: [], note: "Market data unavailable." };
}

function json(obj) {
  return new Response(JSON.stringify(obj), {
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "public, max-age=900" },
  });
}
