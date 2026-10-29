// NEXUS-1 front-end: chat, training studio, file monitor.
const $ = (id) => document.getElementById(id);
const store = { get: (k, d) => { try { return localStorage.getItem(k) ?? d; } catch { return d; } },
                set: (k, v) => { try { localStorage.setItem(k, v); } catch {} } };
let lang = store.get("nexus_lang", "en");
let token = new URLSearchParams(location.search).get("token") || store.get("nexus_token", "");
const t = (k) => I18N[lang][k];
const knownFiles = new Set();

if (location.search.includes("token=")) { store.set("nexus_token", token); history.replaceState(null, "", "/"); }

async function api(path, opts = {}) {
  const res = await fetch(path, { ...opts, headers: { "Content-Type": "application/json", "X-Nexus-Token": token, ...(opts.headers || {}) } });
  if (res.status === 401) { showGate(); throw new Error("unauthorized"); }
  if (!res.ok) throw new Error((await res.json().catch(() => ({}))).detail || res.statusText);
  return res.json();
}

const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
function md(text) {
  const parts = String(text).split(/```(?:\w+)?\n?([\s\S]*?)```/g);
  return parts.map((p, i) => i % 2 ? `<pre class="code">${esc(p.trim())}</pre>`
    : esc(p).replace(/\*\*(.+?)\*\*/g, "<b>$1</b>").replace(/`([^`]+)`/g, '<code class="text-cyan-300">$1</code>')
        .replace(/(https?:\/\/[^\s<]+)/g, '<a class="text-cyan-300 underline" target="_blank" href="$1">$1</a>').replace(/\n/g, "<br>")).join("");
}

// ---------- i18n ----------
function applyLang() {
  document.documentElement.lang = lang;
  document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
  document.querySelectorAll("[data-i18n]").forEach((el) => (el.textContent = t(el.dataset.i18n)));
  document.querySelectorAll("[data-i18n-ph]").forEach((el) => (el.placeholder = t(el.dataset.i18nPh)));
  $("lang-label").textContent = lang === "ar" ? "EN" : "عربي";
  $("suggestions").innerHTML = t("suggestions").map((s) => `<button class="chip">${esc(s)}</button>`).join("");
  $("suggestions").querySelectorAll(".chip").forEach((c) => (c.onclick = () => send(c.textContent)));
}
$("btn-lang").onclick = () => { lang = lang === "ar" ? "en" : "ar"; store.set("nexus_lang", lang); applyLang(); refreshHealth(); };

// ---------- Chat ----------
function addUser(text) {
  $("chat").insertAdjacentHTML("beforeend", `<div class="msg-user">${esc(text)}</div>`);
}
function addBot(html) {
  const el = document.createElement("div");
  el.className = "msg-bot";
  el.innerHTML = html;
  $("chat").appendChild(el);
  $("chat").scrollTop = $("chat").scrollHeight;
  return el;
}
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function send(text) {
  text = text.trim();
  if (!text) return;
  addUser(text);
  $("chat-input").value = "";
  const bot = addBot(`<div class="steps"></div><div class="typing"><span></span><span></span><span></span></div>`);
  try {
    const data = await api("/api/chat", { method: "POST", body: JSON.stringify({ message: text }) });
    const box = bot.querySelector(".steps");
    for (const s of data.steps) {   // reveal reasoning steps one by one
      box.insertAdjacentHTML("beforeend", `<div class="step ${s.status}"><span class="tag tag-${s.stage}">${t("stages")[s.stage]}</span>
        <span class="text-sm">${esc(s.title)}</span>${s.detail ? `<div class="step-detail">${esc(s.detail)}</div>` : ""}</div>`);
      $("chat").scrollTop = $("chat").scrollHeight;
      await sleep(260);
    }
    bot.querySelector(".typing").outerHTML = `<div class="answer">${md(data.answer)}<div class="text-[10px] text-slate-500 mt-2">${data.ms ?? 0} ms</div></div>`;
    if (data.files?.length) loadFiles();
  } catch (e) {
    bot.querySelector(".typing").outerHTML = `<div class="answer text-rose-300">⚠ ${esc(e.message)}</div>`;
  }
  $("chat").scrollTop = $("chat").scrollHeight;
}
$("chat-form").onsubmit = (e) => { e.preventDefault(); send($("chat-input").value); };
$("chat-input").onkeydown = (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(e.target.value); } };
$("btn-clear").onclick = () => { $("chat").innerHTML = ""; addBot(`<div class="answer">${md(t("welcome"))}</div>`); };

// ---------- Training studio ----------
const chart = new Chart($("train-chart"), {
  type: "line",
  data: { labels: [], datasets: [
    { label: "Loss", data: [], borderColor: "#a78bfa", backgroundColor: "rgba(167,139,250,.15)", fill: true, tension: .35, yAxisID: "y" },
    { label: "Val Acc", data: [], borderColor: "#22d3ee", backgroundColor: "rgba(34,211,238,.1)", fill: true, tension: .35, yAxisID: "y1" },
  ] },
  options: { animation: { duration: 300 }, maintainAspectRatio: false,
    plugins: { legend: { labels: { color: "#94a3b8", boxWidth: 10 } } },
    scales: { x: { ticks: { color: "#64748b" }, grid: { color: "rgba(255,255,255,.04)" } },
      y: { ticks: { color: "#a78bfa" }, grid: { color: "rgba(255,255,255,.04)" } },
      y1: { position: "right", min: 0, max: 1, ticks: { color: "#22d3ee" }, grid: { display: false } } } },
});

function renderHistory(h) {
  chart.data.labels = h.map((m) => m.epoch);
  chart.data.datasets[0].data = h.map((m) => m.loss);
  chart.data.datasets[1].data = h.map((m) => m.val_acc);
  chart.update();
  const last = h[h.length - 1];
  if (last) { $("st-epoch").textContent = `${last.epoch}/${last.epochs}`; $("st-acc").textContent = `${(last.val_acc * 100).toFixed(1)}%`; $("st-time").textContent = `${last.elapsed}s`; }
}

async function pollTraining() {
  const s = await api("/api/train/status");
  renderHistory(s.history);
  $("btn-train").disabled = s.running;
  $("btn-train").querySelector("span").textContent = s.running ? t("training") : t("train");
  if (s.error) $("train-msg").textContent = "⚠ " + s.error;
  else if (s.result) $("train-msg").textContent = t("done")(s.result);
  if (s.running) setTimeout(pollTraining, 400); else refreshHealth();
}
$("btn-train").onclick = async () => {
  const r = await api("/api/train", { method: "POST" });
  if (!r.started) $("train-msg").textContent = t("busy");
  pollTraining();
};

// ---------- Files ----------
async function loadFiles() {
  const files = await api("/api/files");
  $("file-list").innerHTML = files.length ? files.map((f) => `<li class="file-row ${knownFiles.size && !knownFiles.has(f.name) ? "new" : ""}" data-name="${esc(f.name)}">
      <i data-lucide="${f.name.endsWith(".py") ? "file-code" : "file-text"}" class="w-4 h-4 text-cyan-300 shrink-0"></i>
      <span class="truncate font-mono text-xs flex-1" dir="ltr">${esc(f.name)}</span><span class="text-[10px] text-slate-500">${(f.size / 1024).toFixed(1)}KB</span></li>`).join("")
    : `<li class="p-3 text-xs text-slate-500">${t("no_files")}</li>`;
  files.forEach((f) => knownFiles.add(f.name));
  $("file-list").querySelectorAll(".file-row").forEach((r) => (r.onclick = () => openFile(r.dataset.name)));
  lucide.createIcons();
}
async function openFile(name) {
  const f = await api(`/api/files/content?name=${encodeURIComponent(name)}`);
  $("modal-title").textContent = f.name; $("modal-body").textContent = f.content;
  $("modal").classList.replace("hidden", "flex");
}
$("modal-close").onclick = () => $("modal").classList.replace("flex", "hidden");
$("btn-refresh").onclick = loadFiles;

// ---------- Health / gate / boot ----------
async function refreshHealth() {
  const h = await fetch("/api/health").then((r) => r.json());
  const pill = $("pill-model");
  pill.classList.toggle("ready", h.model_ready);
  pill.lastElementChild.textContent = h.model_ready ? t("model_ready") : t("model_missing");
  $("pill-safe").classList.toggle("hidden", !h.safe_mode);
  if (!h.model_ready) setTimeout(refreshHealth, 2000);
}
function showGate() { $("gate").classList.replace("hidden", "flex"); }
$("gate-form").onsubmit = (e) => { e.preventDefault(); token = $("gate-input").value.trim(); store.set("nexus_token", token); location.reload(); };

applyLang();
lucide.createIcons();
addBot(`<div class="answer">${md(t("welcome"))}</div>`);
refreshHealth();
if (token) { loadFiles(); pollTraining(); setInterval(loadFiles, 5000); } else showGate();
