// Bento home: greeting, city picker and live tiles (weather, next prayer, dollar, code of the day).
let homeData = null;

function cityName() {
  const saved = store.get("nexus_city", "0");
  const pair = CITIES[Number(saved)] || CITIES[0];
  return lang === "ar" ? pair[0] : pair[1];
}

function renderHello() {
  const hour = new Date().getHours();
  $("hello").textContent = `${hour < 12 ? t("morning") : t("evening")} 👋`;
  $("city").innerHTML = CITIES.map(([ar, en], i) => `<option value="${i}">${esc(lang === "ar" ? ar : en)}</option>`).join("");
  $("city").value = store.get("nexus_city", "0");
}

// «بعد ساعتين و10 دقائق» / "in 2h 10m"
function countdown(h, m) {
  if (lang !== "ar") return `in ${h ? `${h}h ` : ""}${m}m`;
  const hours = h === 0 ? "" : h === 1 ? "ساعة" : h === 2 ? "ساعتين" : h <= 10 ? `${h} ساعات` : `${h} ساعة`;
  const mins = m === 0 ? "" : m === 1 ? "دقيقة" : m === 2 ? "دقيقتين" : m <= 10 ? `${m} دقائق` : `${m} دقيقة`;
  const parts = [hours, mins].filter(Boolean).join(" و");
  return parts ? `بعد ${parts}` : "الآن";
}

function tileHead(icon, label) { return `<div class="tile-head">${svg(icon)}<span>${label}</span></div>`; }
function skeleton(id, icon, label) {
  $(id).innerHTML = `${tileHead(icon, label)}<div class="tile-body"><span class="shimmer"></span><span class="shimmer short"></span></div>`;
}

function renderTiles() {
  const d = homeData;
  const city = d ? d.city : cityName();
  const w = d && d.weather, p = d && d.prayer, fx = d && d.usd_sar, c = d && d.code;
  $("tile-weather").dataset.q = lang === "ar" ? `كيف الجو في ${city}؟` : `Weather in ${city}`;
  $("tile-weather").innerHTML = tileHead("weather", t("weatherNow")) + (w
    ? `<div class="tile-body"><b class="big">${w.temp}°</b><span>${esc(city)} · ${esc(w.desc)}</span>
       <small>↑ ${w.high}°  ↓ ${w.low}°</small></div>` : `<div class="tile-body"><small>${t("unavailable")}</small></div>`);
  $("tile-prayer").dataset.q = lang === "ar" ? `مواقيت الصلاة في ${city}` : `Prayer times in ${city}`;
  $("tile-prayer").innerHTML = tileHead("prayer", t("nextPrayer")) + (p
    ? `<div class="tile-body"><b class="big">${esc(p.name)}</b><span>${esc(p.time)}</span>
       <small>${countdown(p.in_hours, p.in_minutes)}</small></div>`
    : `<div class="tile-body"><small>${t("unavailable")}</small></div>`);
  $("tile-fx").dataset.q = lang === "ar" ? "كم سعر الدولار بالريال؟" : "Convert 1 USD to SAR";
  $("tile-fx").innerHTML = tileHead("currency", t("dollar")) + (fx
    ? `<div class="tile-body"><b class="big">${fx.toFixed(2)}</b><span>${t("sar")}</span><small>1 USD</small></div>`
    : `<div class="tile-body"><small>${t("unavailable")}</small></div>`);
  if (c) {
    $("tile-code").dataset.q = c.question;
    $("tile-code").innerHTML = `${tileHead("code", t("codeDay"))}<div class="tile-body">
      <span class="code-title">${esc(c.title)} · ${esc(c.language)}</span><pre>${esc(c.code)}</pre></div>`;
  }
}

async function loadHome() {
  ["tile-weather", "tile-prayer", "tile-fx", "tile-code"].forEach((id, i) =>
    skeleton(id, ["weather", "prayer", "currency", "code"][i], t(["weatherNow", "nextPrayer", "dollar", "codeDay"][i])));
  try {
    const res = await fetch(`/api/home?city=${encodeURIComponent(cityName())}&lang=${lang}`);
    homeData = res.ok ? await res.json() : null;
  } catch { homeData = null; }
  renderTiles();
}
