// NEXUS-1 developer dashboard.
const $ = (id) => document.getElementById(id);
const store = { get: (k, d) => { try { return localStorage.getItem(k) ?? d; } catch { return d; } },
                set: (k, v) => { try { localStorage.setItem(k, v); } catch {} } };
let token = new URLSearchParams(location.search).get("token") || store.get("nexus_dev_token", "");
if (location.search.includes("token=")) { store.set("nexus_dev_token", token); history.replaceState(null, "", "/dev"); }

const INTENT_AR = { chat: "دردشة", python: "حساب/كود", file: "ملفات", web: "بحث", system: "أوامر نظام", unknown: "؟" };
const SIZE_AR = { small: "صغير", medium: "متوسط", large: "كبير" };
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const num = (n) => (n ?? 0).toLocaleString("en-US");
const pct = (x) => (x == null ? "—" : (x * 100).toFixed(1) + "%");

async function api(path, opts = {}) {
  const res = await fetch(path, { ...opts, headers: { "Content-Type": "application/json", "X-Nexus-Token": token } });
  if (res.status === 401) { showGate(); throw new Error("unauthorized"); }
  if (!res.ok) throw new Error((await res.json().catch(() => ({}))).detail || res.statusText);
  return res.json();
}
const tile = (label, value, sub = "") => `<div class="tile"><p>${label}</p><b>${value}</b>${sub ? `<small>${sub}</small>` : ""}</div>`;
const gridOpts = { color: "rgba(255,255,255,.05)" };

const trainChart = new Chart($("train-chart"), {
  type: "line",
  data: { labels: [], datasets: [
    { label: "الخطأ Loss", data: [], borderColor: "#a78bfa", tension: .35, yAxisID: "y" },
    { label: "الدقة Accuracy", data: [], borderColor: "#22d3ee", tension: .35, yAxisID: "y1" }] },
  options: { maintainAspectRatio: false, animation: { duration: 250 }, plugins: { legend: { labels: { color: "#8b93a5" } } },
    scales: { x: { ticks: { color: "#8b93a5" }, grid: gridOpts }, y: { ticks: { color: "#a78bfa" }, grid: gridOpts },
              y1: { position: "right", min: 0, max: 1, ticks: { color: "#22d3ee" }, grid: { display: false } } } },
});
const intentChart = new Chart($("intent-chart"), {
  type: "bar", data: { labels: [], datasets: [{ data: [], backgroundColor: "#22d3ee", borderRadius: 6 }] },
  options: { indexAxis: "y", maintainAspectRatio: false, plugins: { legend: { display: false } },
    scales: { x: { ticks: { color: "#8b93a5", precision: 0 }, grid: gridOpts }, y: { ticks: { color: "#e8eaf0" }, grid: { display: false } } } },
});

function renderOverview(o) {
  const b = o.brain, u = o.usage;
  $("brain-tiles").innerHTML = [
    tile("حجم العقل", num(b.params), "معامل (parameter)"),
    tile("النسخة", b.version ? "v" + b.version : "—", SIZE_AR[b.size] || ""),
    tile("الطبقات", b.n_layers ?? "—", `${b.n_heads ?? "?"} رؤوس انتباه`),
    tile("عرض العقل", b.d_model ?? "—", "d_model"),
    tile("المفردات", num(b.vocab), "كلمة يعرفها"),
    tile("خطوات التدريب", num(b.total_steps), `آخر تدريب: ${num(b.steps)}`),
    tile("دقة الاختبار", pct(b.val_acc), `${num(o.taught)} مثال علّمته`),
  ].join("");
  $("usage-tiles").innerHTML = [
    tile("الأسئلة", num(u.questions)),
    tile("خطوات الوكيل", num(u.agent_steps), "تخطيط + أداة + تدقيق"),
    tile("متوسط الرد", u.avg_ms + "ms"),
    tile("نسبة التحقق", pct(u.verified_rate), "أجوبة اجتازت المدقق"),
    tile("مدة التشغيل", Math.floor(u.uptime_s / 3600) + "h " + Math.floor((u.uptime_s % 3600) / 60) + "m"),
  ].join("");
  const entries = Object.entries(u.intents).sort((a, b) => b[1] - a[1]);
  intentChart.data.labels = entries.map(([k]) => INTENT_AR[k] || k);
  intentChart.data.datasets[0].data = entries.map(([, v]) => v);
  intentChart.update();
  const key = u.recent.map((r) => r.time + r.text).join("|");
  if (key !== lastRecentKey) { lastRecentKey = key; renderRecent(u.recent, o.intents); }
  $("versions").innerHTML = o.versions.slice().reverse().map((v) => `<tr><td class="mono">v${v.version}</td><td>${SIZE_AR[v.size] || v.size}</td>
      <td class="mono">${num(v.params)}</td><td class="mono">${num(v.steps)}</td><td class="mono">${pct(v.val_acc)}</td>
      <td class="mono text-slate-400">${v.date}</td></tr>`).join("") || `<tr><td colspan="6" class="text-slate-500 p-4">—</td></tr>`;
  if (!$("size").options.length) $("size").innerHTML = o.sizes.map((s) => `<option value="${s}">${SIZE_AR[s]}</option>`).join("");
}

// Only redraw when new questions arrive, so a correction being chosen is not wiped by the refresh.
let lastRecentKey = null;
function renderRecent(recent, intents) {
  const u = { recent };
  const options = intents.map((i) => `<option value="${i}">${INTENT_AR[i]}</option>`).join("");
  $("recent").innerHTML = u.recent.length ? u.recent.map((r, i) => `<tr>
      <td class="mono text-slate-400">${r.time}</td><td dir="auto" class="max-w-xs truncate">${esc(r.text)}</td>
      <td>${INTENT_AR[r.intent] || r.intent}</td><td class="mono">${pct(r.confidence)}</td>
      <td class="whitespace-nowrap"><select class="field text-xs" data-i="${i}">${options}</select>
        <button class="text-cyan-300 text-xs ms-2" data-teach="${i}">علّم ✓</button></td></tr>`).join("")
    : `<tr><td colspan="5" class="text-slate-500 p-4">ما فيه أسئلة للحين. جرّب صفحة المستخدمين.</td></tr>`;
  $("recent").querySelectorAll("select").forEach((s) => (s.value = u.recent[s.dataset.i].intent));
  $("recent").querySelectorAll("[data-teach]").forEach((btn) => (btn.onclick = () => teach(u.recent[btn.dataset.teach].text,
    $("recent").querySelector(`select[data-i="${btn.dataset.teach}"]`).value, btn)));
}

async function teach(text, intent, btn) {
  const r = await api("/api/dev/teach", { method: "POST", body: JSON.stringify({ text, intent }) });
  btn.textContent = "✓ تم"; btn.disabled = true;
  $("train-msg").textContent = `صار عندك ${r.taught} مثال. درّب العقل عشان يتعلّمها.`;
}

async function pollTraining() {
  const s = await api("/api/dev/train/status");
  trainChart.data.labels = s.history.map((m) => m.epoch);
  trainChart.data.datasets[0].data = s.history.map((m) => m.loss);
  trainChart.data.datasets[1].data = s.history.map((m) => m.val_acc);
  trainChart.update();
  $("train").disabled = s.running;
  if (s.running) $("train-msg").textContent = `جاري التدريب… دورة ${s.history.length}`;
  else if (s.error) $("train-msg").textContent = "⚠ " + s.error;
  else if (s.result) $("train-msg").textContent = `✓ النسخة v${s.result.version}: ${num(s.result.params)} معامل خلال ${s.result.seconds} ثانية`;
  if (s.running) setTimeout(pollTraining, 500); else refresh();
}
$("train").onclick = async () => {
  await api("/api/dev/train", { method: "POST", body: JSON.stringify({ size: $("size").value, epochs: +$("epochs").value || 12 }) });
  pollTraining();
};

async function loadFiles() {
  const files = await api("/api/dev/files");
  $("files").innerHTML = files.map((f) => `<li class="flex justify-between px-3 py-2 rounded-lg hover:bg-white/5"><span class="mono truncate">${esc(f.name)}</span>
    <span class="text-slate-500 text-xs">${(f.size / 1024).toFixed(1)}KB</span></li>`).join("") || `<li class="p-3 text-slate-500">لا توجد ملفات</li>`;
}

async function refresh() {
  try { renderOverview(await api("/api/dev/overview")); loadFiles(); $("live").style.opacity = 1; }
  catch { $("live").style.opacity = .3; }
}
function showGate() { $("gate").classList.replace("hidden", "flex"); $("gate-input").focus(); }
$("gate-form").onsubmit = (e) => { e.preventDefault(); token = $("gate-input").value.trim(); store.set("nexus_dev_token", token); location.reload(); };
$("logout").onclick = () => { store.set("nexus_dev_token", ""); location.reload(); };

if (!token) showGate(); else { refresh(); pollTraining(); setInterval(refresh, 5000); }
