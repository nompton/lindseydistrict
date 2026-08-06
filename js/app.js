/* =========================================================
   Lindsey Street District — app logic
   ========================================================= */
(function () {
  "use strict";

  /* ---------- tiny helpers ---------- */
  const $  = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const esc = (str) =>
    String(str).replace(/[&<>"']/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  /* ---------- approximate geocoding along W Lindsey St ----------
     The district runs roughly east-west along W Lindsey Street.
     We interpolate longitude from the street number and nudge
     latitude by side-of-street + a deterministic jitter so pins
     that share an address don't stack. Positions are APPROXIMATE
     and meant to show relative location; add explicit lat/lng to
     a business in data.js to pin it exactly. */
  function hashStr(s) {
    let h = 0;
    for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0;
    return h;
  }
  function approxCoords(b) {
    if (typeof b.lat === "number" && typeof b.lng === "number") return [b.lat, b.lng];
    const a = String(b.address || "");
    const m = a.match(/(\d{3,4})/);
    if (!m) return null;
    const n = Math.min(Math.max(parseInt(m[1], 10), 700), 2400);
    // Lindsey corridor: number 800 -> lng -97.4520, number 2320 -> lng -97.4790
    let lng = -97.4520 - (n - 800) * (0.0270 / 1520);
    let lat = 35.2045 + (n % 2 === 0 ? -0.00075 : 0.00075);
    // cross-street corrections for non-Lindsey addresses
    const low = a.toLowerCase();
    if (low.includes("mcgee")) lng = -97.4640;
    else if (low.includes("24th")) lng = -97.4726;
    else if (low.includes("berry")) lng = -97.4585;
    // deterministic jitter to de-stack shared addresses
    const h = hashStr(b.name);
    lat += ((h % 100) / 100 - 0.5) * 0.0010;
    lng += ((Math.floor(h / 100) % 100) / 100 - 0.5) * 0.0010;
    return [lat, lng];
  }

  /* ---------- state ---------- */
  let activeCat = "all";
  let query = "";

  /* ---------- mobile nav ---------- */
  const toggle = $(".nav-toggle");
  const links = $(".nav-links");
  if (toggle && links) {
    toggle.addEventListener("click", () => {
      const open = links.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    links.addEventListener("click", (e) => {
      if (e.target.tagName === "A") links.classList.remove("open");
    });
  }

  /* ---------- SVG icons ---------- */
  const icon = {
    pin:   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 12-9 12s-9-5-9-12a9 9 0 0 1 18 0Z"/><circle cx="12" cy="10" r="3"/></svg>',
    phone: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3 19.5 19.5 0 0 1-6-6 19.8 19.8 0 0 1-3-8.6A2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2Z"/></svg>',
    clock: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
  };

  /* ---------- directory rendering ---------- */
  const grid = $("#dirGrid");

  function matches(b) {
    const inCat = activeCat === "all" || b.category === activeCat;
    if (!inCat) return false;
    if (!query) return true;
    const hay = (b.name + " " + b.desc + " " + (b.address || "")).toLowerCase();
    return hay.includes(query);
  }

  function cardHTML(b) {
    const cat = CATEGORIES[b.category] || { label: b.category, emoji: "📍" };
    const links = [];
    if (b.website)   links.push(`<a href="${esc(b.website)}" target="_blank" rel="noopener">Website ↗</a>`);
    if (b.instagram) links.push(`<a href="${esc(b.instagram)}" target="_blank" rel="noopener">Instagram ↗</a>`);
    if (b.facebook)  links.push(`<a href="${esc(b.facebook)}" target="_blank" rel="noopener">Facebook ↗</a>`);
    if (b.address)   links.push(`<a href="https://maps.google.com/?q=${encodeURIComponent(b.address)}" target="_blank" rel="noopener">Directions ↗</a>`);

    const meta = [];
    if (b.address) meta.push(`<div class="row">${icon.pin}<span>${esc(b.address)}${b.center ? ` · ${esc(b.center)}` : ""}</span></div>`);
    if (b.phone)   meta.push(`<div class="row">${icon.phone}<a href="tel:${esc(b.phone.replace(/[^0-9+]/g,""))}">${esc(b.phone)}</a></div>`);
    if (b.hours)   meta.push(`<div class="row">${icon.clock}<span>${esc(b.hours)}</span></div>`);

    return `
      <article class="card">
        <div class="card-top">
          <span class="card-cat">${esc(cat.label)}</span>
          <span class="cat-emoji" aria-hidden="true">${cat.emoji}</span>
        </div>
        <div class="card-body">
          <h3>${esc(b.name)}</h3>
          <p class="card-desc">${esc(b.desc || "")}</p>
          <div class="card-meta">${meta.join("")}</div>
          ${links.length ? `<div class="card-links">${links.join("")}</div>` : ""}
        </div>
      </article>`;
  }

  function render() {
    if (!grid) return;
    const list = BUSINESSES.filter(matches);
    grid.innerHTML = list.length
      ? list.map(cardHTML).join("")
      : `<p class="empty">No spots match that yet — try another category or search.</p>`;
    const countEl = $("#dirCount");
    if (countEl) countEl.textContent = list.length;
  }

  /* ---------- filter chips ---------- */
  const filterBar = $("#filters");
  if (filterBar) {
    const cats = ["all", ...Object.keys(CATEGORIES)];
    filterBar.innerHTML = cats.map((c) => {
      const label = c === "all" ? "All" : CATEGORIES[c].label;
      const emoji = c === "all" ? "✦" : CATEGORIES[c].emoji;
      return `<button class="chip" data-cat="${c}" aria-pressed="${c === "all"}">${emoji} ${label}</button>`;
    }).join("");
    filterBar.addEventListener("click", (e) => {
      const btn = e.target.closest(".chip");
      if (!btn) return;
      activeCat = btn.dataset.cat;
      $$(".chip", filterBar).forEach((c) => c.setAttribute("aria-pressed", c === btn));
      render();
    });
  }

  /* ---------- search ---------- */
  const search = $("#dirSearch");
  if (search) {
    search.addEventListener("input", () => {
      query = search.value.trim().toLowerCase();
      render();
    });
  }

  render();

  /* ---------- stats ---------- */
  const totalEl = $("#statTotal");
  if (totalEl) totalEl.textContent = BUSINESSES.length + "+";
  const catEl = $("#statCats");
  if (catEl) catEl.textContent = Object.keys(CATEGORIES).length;

  /* ---------- events ---------- */
  const eventsEl = $("#eventsList");
  if (eventsEl && typeof EVENTS !== "undefined") {
    eventsEl.innerHTML = EVENTS.map((ev) => `
      <div class="event">
        <div class="date"><div class="m">${esc(ev.month)}</div><div class="d">${esc(ev.day)}</div></div>
        <div>
          <div class="when">${esc(ev.when)}</div>
          <h3>${esc(ev.title)}</h3>
          <p>${esc(ev.desc)}</p>
        </div>
      </div>`).join("");
  }

  /* ---------- map (Leaflet) ---------- */
  const mapEl = $("#map");
  if (mapEl && window.L) {
    const map = L.map("map", { scrollWheelZoom: false }).setView(MAP_CONFIG.center, MAP_CONFIG.zoom);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map);

    const pins = [];
    BUSINESSES.forEach((b) => {
      const c = approxCoords(b);
      if (!c) return;
      const cat = CATEGORIES[b.category] || { emoji: "📍", label: "" };
      const mk = L.marker(c).addTo(map);
      mk.bindPopup(
        `<strong>${esc(b.name)}</strong><br>${cat.emoji} ${esc(cat.label)}` +
        (b.address ? `<br><span style="color:#6f655c">${esc(b.address)}</span>` : "")
      );
      pins.push(c);
    });
    if (pins.length > 1) map.fitBounds(pins, { padding: [40, 40] });
    map.on("click", () => map.scrollWheelZoom.enable());
  }

  /* ---------- footer year ---------- */
  const yr = $("#year");
  if (yr) yr.textContent = new Date().getFullYear();

  /* ---------- lead capture → GRID Real Estate (ATLAS) ----------
     Every business that lists, and every space/commercial inquiry, becomes a
     tagged lead in GRID's CRM. Lindsey Street is a prime commercial corridor,
     so the district directory doubles as a top-of-funnel for GRID's commercial
     real estate + property management business. */
  const LEAD_ENDPOINT = "https://portal.thegridre.com/api/public/contact/submit";
  async function postLead(payload) {
    const res = await fetch(LEAD_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ site: "Lindsey District", ...payload }),
    });
    if (!res.ok) throw new Error();
  }

  // "List your business" — a directory signup is also a warm commercial contact.
  const form = $("#submitForm");
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const btn = form.querySelector('button[type="submit"]');
      const d = Object.fromEntries(new FormData(form).entries());
      if (btn) { btn.disabled = true; btn.textContent = "Submitting…"; }
      try {
        await postLead({
          lead_type: "directory",
          interest: "business-listing",
          subject: "Lindsey District directory listing",
          name: d.business_name,
          email: d.email,
          phone: d.phone,
          address: d.address,
          message: [
            d.category && `Category: ${d.category}`,
            d.shopping_center && `Center: ${d.shopping_center}`,
            d.website && `Web: ${d.website}`,
            d.instagram && `IG: ${d.instagram}`,
            d.description,
          ].filter(Boolean).join(" · "),
        });
        const ok = $("#formSuccess");
        if (ok) { ok.hidden = false; ok.scrollIntoView({ behavior: "smooth", block: "center" }); }
        form.reset();
        if (btn) btn.textContent = "Submitted ✓";
      } catch {
        if (btn) { btn.disabled = false; btn.textContent = "Submit Listing"; }
        alert("Something went wrong — please email hello@lindseydistrict.com and we'll add you.");
      }
    });
  }

  // "Space on Lindsey" — GRID commercial real estate lead capture (tenant /
  // landlord-seller / investor), routed by intent.
  const sform = $("#spaceForm");
  if (sform) {
    sform.addEventListener("submit", async (e) => {
      e.preventDefault();
      const btn = sform.querySelector('button[type="submit"]');
      const d = Object.fromEntries(new FormData(sform).entries());
      const intent = d.intent || "";
      const leadType = /own|list|lease out|sell|landlord/i.test(intent) ? "seller" : "buyer";
      if (btn) { btn.disabled = true; btn.textContent = "Sending…"; }
      try {
        await postLead({
          lead_type: leadType,
          interest: "commercial",
          subject: "Lindsey Street commercial inquiry",
          name: d.name,
          email: d.email,
          phone: d.phone,
          sms_consent: d.sms_consent || "",
          message: [
            intent && `Interest: ${intent}`,
            d.business && `Business/property: ${d.business}`,
            d.message,
          ].filter(Boolean).join(" · "),
        });
        const ok = $("#spaceSuccess");
        if (ok) { ok.hidden = false; ok.scrollIntoView({ behavior: "smooth", block: "center" }); }
        sform.reset();
        if (btn) btn.textContent = "Sent ✓";
      } catch {
        if (btn) { btn.disabled = false; btn.textContent = "Get in touch"; }
      }
    });
  }

  // "Live in the district" — residential renter/buyer capture. Rent intents
  // route as renter leads, buy intents as buyer leads.
  const lform = $("#liveForm");
  if (lform) {
    lform.addEventListener("submit", async (e) => {
      e.preventDefault();
      const btn = lform.querySelector('button[type="submit"]');
      const d = Object.fromEntries(new FormData(lform).entries());
      const buying = /buy/i.test(d.intent || "");
      if (btn) { btn.disabled = true; btn.textContent = "Sending…"; }
      try {
        await postLead({
          lead_type: buying ? "buyer" : "renter",
          interest: buying ? "buying" : "renting",
          subject: "Live in Lindsey District inquiry",
          name: d.name,
          email: d.email,
          phone: d.phone,
          sms_consent: d.sms_consent || "",
          message: [
            d.intent && `Looking to: ${d.intent}`,
            d.beds && `Beds: ${d.beds}`,
            d.message,
          ].filter(Boolean).join(" · "),
        });
        const ok = $("#liveSuccess");
        if (ok) { ok.hidden = false; ok.scrollIntoView({ behavior: "smooth", block: "center" }); }
        lform.reset();
        if (btn) btn.textContent = "Sent ✓";
      } catch {
        if (btn) { btn.disabled = false; btn.textContent = "Find my place"; }
      }
    });
  }

  // "Let GRID run the back office" — apartment community / property-owner PM
  // pitch. The lead is a management prospect (seller-side) for GRID.
  const mform = $("#manageForm");
  if (mform) {
    mform.addEventListener("submit", async (e) => {
      e.preventDefault();
      const btn = mform.querySelector('button[type="submit"]');
      const d = Object.fromEntries(new FormData(mform).entries());
      if (btn) { btn.disabled = true; btn.textContent = "Sending…"; }
      try {
        await postLead({
          lead_type: "seller",
          interest: "property-management",
          subject: "Apartment / property management inquiry",
          name: d.name,
          email: d.email,
          phone: d.phone,
          message: [
            d.community && `Community/property: ${d.community}`,
            d.units && `Units: ${d.units}`,
            d.message,
          ].filter(Boolean).join(" · "),
        });
        const ok = $("#manageSuccess");
        if (ok) { ok.hidden = false; ok.scrollIntoView({ behavior: "smooth", block: "center" }); }
        mform.reset();
        if (btn) btn.textContent = "Sent ✓";
      } catch {
        if (btn) { btn.disabled = false; btn.textContent = "Request a proposal"; }
      }
    });
  }
})();
