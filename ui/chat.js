// NEXUS user chat: premium home with popular questions, then a focused conversation.
const $ = (id) => document.getElementById(id);
const store = { get: (k, d) => { try { return localStorage.getItem(k) ?? d; } catch { return d; } },
                set: (k, v) => { try { localStorage.setItem(k, v); } catch {} } };
const sharedQuestion = new URLSearchParams(location.search).get("q");  // shareable links: /?q=...
if (location.search) history.replaceState(null, "", "/");
let lang = store.get("nexus_lang", "ar");
let busy = false, tab = "all";
let session = newSession();

const ICONS = {
  all: '<path d="M4 6h16M4 12h16M4 18h10"/>', web: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
  code: '<path d="m8 8-4 4 4 4M16 8l4 4-4 4M14 5l-4 14"/>', weather: '<circle cx="12" cy="10" r="4"/><path d="M12 2v2M4.9 4.9l1.4 1.4M2 10h2M17.7 6.3l1.4-1.4M7 18h10a3 3 0 0 0 0-6"/>',
  currency: '<circle cx="9" cy="9" r="6"/><path d="M15.5 9.5a6 6 0 1 1-6 6"/>', python: '<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M8 7h8M8 12h2M12 12h2M16 12h0M8 16h2M12 16h2M16 16h0"/>',
  datetime: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>', units: '<path d="M3 17 17 3l4 4L7 21zM7 13l2 2M10 10l2 2M13 7l2 2"/>',
  arrow: '<path d="M19 12H5M11 6l-6 6 6 6"/>', link: '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7L11.5 7M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1.5-1.5"/>',
};
const svg = (name) => `<svg viewBox="0 0 24 24">${ICONS[name] || ""}</svg>`;

const T = {
  ar: { eyebrow: "مساعد ذكي بعقل مُدرَّب ذاتياً", hello1: "أهلاً بك،", hello2: "وش تبي تعرف اليوم؟", newChat: "محادثة جديدة",
        placeholder: "اسأل عن أي شيء… معلومة، كود، طقس، عملة", hint: "NEXUS قد يخطئ أحياناً، تحقّق من المعلومات المهمة.",
        error: "تعذّر الوصول للخادم، حاول مرة ثانية.", copy: "نسخ", copied: "تم النسخ ✓", source: "المصدر",
        cats: { all: "الكل", web: "معرفة", code: "برمجة", weather: "طقس", currency: "عملات", python: "حساب", datetime: "الوقت", units: "تحويل" },
        skills: { chat: "محادثة", file: "ملفات", system: "نظام" } },
  en: { eyebrow: "An assistant with a self-trained brain", hello1: "Welcome,", hello2: "what would you like to know?", newChat: "New chat",
        placeholder: "Ask anything… facts, code, weather, currency", hint: "NEXUS can make mistakes. Verify important information.",
        error: "Couldn't reach the server, please try again.", copy: "Copy", copied: "Copied ✓", source: "Source",
        cats: { all: "All", web: "Knowledge", code: "Code", weather: "Weather", currency: "Currency", python: "Math", datetime: "Time", units: "Units" },
        skills: { chat: "Chat", file: "Files", system: "System" } },
};
const POPULAR = [
  ["web", "ما هي عاصمة اليابان؟", "What is the capital of Japan?"], ["code", "كيف أعكس نص في بايثون؟", "How to reverse a string in Python"],
  ["weather", "كيف الجو في الرياض؟", "Weather in Riyadh"], ["currency", "كم سعر الدولار بالريال؟", "Convert 100 USD to EUR"],
  ["web", "كم ارتفاع برج خليفة؟", "How tall is Mount Everest?"], ["python", "كم 15٪ من 200؟", "What is 15% of 200"],
  ["web", "من مؤسس جوجل؟", "Who founded Tesla?"], ["web", "من هو ابن سينا؟", "Who was Albert Einstein?"],
  ["code", "حلقة for في جافاسكربت", "For loop in JavaScript"], ["datetime", "التاريخ الهجري اليوم", "What is the hijri date today?"],
  ["web", "اشرح لي الثقب الأسود", "Explain photosynthesis"], ["units", "حول 10 كيلومتر الى ميل", "Convert 5 miles to km"],
  ["web", "كم عدد سكان مصر؟", "Population of France"], ["code", "كيف أقرأ ملف في جافا؟", "Parse JSON in JavaScript"],
  ["weather", "الطقس في دبي", "Weather in London"], ["currency", "حول 100 يورو الى ريال", "How much is 50 GBP in dollars"],
  ["python", "احسب مضروب 10", "Calculate 2 ** 16"], ["units", "100 فهرنهايت كم مئوية", "Convert 70 kg to pounds"],
];
const t = (k) => T[lang][k];

function newSession() {
  try { return crypto.randomUUID(); } catch { return String(Date.now()) + Math.random().toString(16).slice(2); }
}

// ---------- Markdown (safe subset) ----------
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
function inline(s) {
  return esc(s).replace(/\*\*(.+?)\*\*/g, "<b>$1</b>").replace(/`([^`\n]+)`/g, "<code>$1</code>")
    .replace(/\s*🔗\s*(https?:\/\/[^\s<]+)/g, (_, url) => `<div><a class="src" href="${url}" target="_blank" rel="noopener">${svg("link")}${t("source")} · ${new URL(url).hostname.replace("www.", "")}</a></div>`)
    .replace(/\n/g, "<br>");
}
function md(text) {
  return String(text).split(/```(\w*)\n?([\s\S]*?)```/g).map((part, i, all) => {
    if (i % 3 === 0) return inline(part.replace(/^\n+|\n+$/g, ""));
    if (i % 3 === 1) return "";
    const langName = all[i - 1] || "text";
    return `<div class="code"><header><span>${esc(langName)}</span><button class="copy" data-copy>${t("copy")}</button></header><pre>${esc(part.trim())}</pre></div>`;
  }).join("");
}

// ---------- Rendering ----------
function applyLang() {
  document.documentElement.lang = lang;
  document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
  document.querySelectorAll("[data-t]").forEach((el) => (el.textContent = t(el.dataset.t)));
  $("input").placeholder = t("placeholder");
  $("btn-lang").textContent = lang === "ar" ? "EN" : "ع";
  renderTabs(); renderPopular();
}
function renderTabs() {
  $("tabs").innerHTML = Object.entries(t("cats")).map(([k, label]) =>
    `<button class="tab ${k === tab ? "on" : ""}" data-tab="${k}" role="tab">${svg(k)}${label}</button>`).join("");
}
function renderPopular() {
  const items = POPULAR.filter(([cat]) => tab === "all" || cat === tab).slice(0, tab === "all" ? 9 : 6);
  $("popular").innerHTML = items.map(([cat, ar, en], i) => {
    const q = lang === "ar" ? ar : en;
    return `<button class="q" data-q="${esc(q)}" style="animation-delay:${i * 40}ms"><span class="cat">${svg(cat)}${t("cats")[cat]}</span>
      <span class="text">${esc(q)}</span><span class="go">${svg("arrow")}</span></button>`;
  }).join("");
}

function setMode(chatting) {
  document.body.classList.toggle("chat-mode", chatting);
  document.body.classList.toggle("home-mode", !chatting);
  (chatting ? $("slot-dock") : $("slot-home")).prepend($("composer"));
}
const scrollDown = () => ($("scroll").scrollTop = $("scroll").scrollHeight);
function autosize() { const el = $("input"); el.style.height = "auto"; el.style.height = Math.min(el.scrollHeight, 200) + "px"; }
function refreshSend() { $("send").disabled = busy || !$("input").value.trim(); }

async function send(text) {
  text = (text || "").trim();
  if (!text || busy) return;
  setMode(true);
  busy = true;
  $("input").value = ""; autosize(); refreshSend();
  $("thread").insertAdjacentHTML("beforeend", `<div class="u" dir="auto">${esc(text)}</div>`);
  const bot = document.createElement("div");
  bot.className = "b";
  bot.innerHTML = `<span class="mark"><i></i></span><div><div class="meta">NEXUS</div><div class="body"><span class="thinking"><i></i><i></i><i></i></span></div></div>`;
  $("thread").appendChild(bot); scrollDown();
  try {
    const res = await fetch("/api/chat", { method: "POST", headers: { "Content-Type": "application/json" },
                                           body: JSON.stringify({ message: text, session }) });
    if (!res.ok) throw new Error(res.statusText);
    const data = await res.json();
    const skill = t("cats")[data.intent] || t("skills")[data.intent];
    if (skill) bot.querySelector(".meta").insertAdjacentHTML("beforeend", `<span class="badge">${skill}</span>`);
    bot.querySelector(".body").innerHTML = `<div dir="auto">${md(data.answer)}</div>`;
  } catch {
    bot.querySelector(".body").textContent = t("error");
  } finally {
    busy = false; refreshSend(); scrollDown(); $("input").focus();
  }
}

// ---------- Events ----------
document.addEventListener("click", (e) => {
  const q = e.target.closest("[data-q]"), tb = e.target.closest("[data-tab]"), cp = e.target.closest("[data-copy]");
  if (q) send(q.dataset.q);
  if (tb) { tab = tb.dataset.tab; renderTabs(); renderPopular(); }
  if (cp) navigator.clipboard?.writeText(cp.closest(".code").querySelector("pre").textContent)
    .then(() => { cp.textContent = t("copied"); setTimeout(() => (cp.textContent = t("copy")), 1600); });
});
$("input").addEventListener("input", () => { autosize(); refreshSend(); });
$("input").addEventListener("keydown", (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(e.target.value); } });
$("composer").onsubmit = (e) => { e.preventDefault(); send($("input").value); };
$("btn-new").onclick = () => { $("thread").innerHTML = ""; session = newSession(); setMode(false); $("input").focus(); };
$("btn-lang").onclick = () => { lang = lang === "ar" ? "en" : "ar"; store.set("nexus_lang", lang); applyLang(); };

applyLang(); setMode(false); refreshSend(); $("input").focus();
if (sharedQuestion) send(sharedQuestion);
