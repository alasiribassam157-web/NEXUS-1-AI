// NEXUS-1 user chat: simple ChatGPT-style conversation.
const $ = (id) => document.getElementById(id);
const store = { get: (k, d) => { try { return localStorage.getItem(k) ?? d; } catch { return d; } },
                set: (k, v) => { try { localStorage.setItem(k, v); } catch {} } };
if (location.search) history.replaceState(null, "", "/");  // drop old ?token= links
let lang = store.get("nexus_lang", "ar");

const TEXT = {
  ar: { hello: "كيف أقدر أساعدك اليوم؟", placeholder: "اسأل NEXUS-1 أي شيء…", hint: "NEXUS-1 عقل مُدرَّب ذاتياً وقد يخطئ أحياناً.",
        cards: [["ابحث عن", "الذكاء الاصطناعي"], ["احسب", "مضروب 12"], ["من هو", "ابن سينا"], ["اكتب ملاحظة", "انشئ ملف ideas.txt"]],
        error: "صار خطأ، حاول مرة ثانية." },
  en: { hello: "How can I help you today?", placeholder: "Ask NEXUS-1 anything…", hint: "NEXUS-1 is a self-trained brain and can make mistakes.",
        cards: [["Search for", "machine learning"], ["Calculate", "factorial of 12"], ["Who is", "Alan Turing"], ["Write a note", "create file ideas.txt"]],
        error: "Something went wrong, please try again." },
};
const t = () => TEXT[lang];

const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
function md(text) {
  const parts = String(text).split(/```(?:\w+)?\n?([\s\S]*?)```/g);
  return parts.map((p, i) => i % 2 ? `<pre>${esc(p.trim())}</pre>`
    : esc(p).replace(/\*\*(.+?)\*\*/g, "<b>$1</b>").replace(/`([^`]+)`/g, "<code>$1</code>")
        .replace(/(https?:\/\/[^\s<]+)/g, '<a target="_blank" rel="noopener" href="$1">$1</a>').replace(/\n/g, "<br>")).join("");
}

function applyLang() {
  document.documentElement.lang = lang;
  document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
  $("hello").textContent = t().hello;
  $("input").placeholder = t().placeholder;
  $("hint").textContent = t().hint;
  $("btn-lang").textContent = lang === "ar" ? "EN" : "ع";
  $("cards").innerHTML = t().cards.map(([a, b]) => `<button class="card" data-q="${esc(a + " " + b)}"><b>${esc(a)}</b>${esc(b)}</button>`).join("");
  $("cards").querySelectorAll(".card").forEach((c) => (c.onclick = () => send(c.dataset.q)));
}

function showThread() { $("empty").classList.add("hidden"); $("thread").classList.remove("hidden"); }
const scrollDown = () => ($("scroll").scrollTop = $("scroll").scrollHeight);

async function send(text) {
  text = text.trim();
  if (!text || $("send").disabled) return;
  showThread();
  $("thread").insertAdjacentHTML("beforeend", `<div class="msg-user fade" dir="auto">${esc(text)}</div>`);
  const bot = document.createElement("div");
  bot.className = "msg-bot fade";
  bot.innerHTML = `<span class="orb-sm"></span><div class="body"><span class="dots"><span></span><span></span><span></span></span></div>`;
  $("thread").appendChild(bot);
  $("input").value = ""; autosize(); setBusy(true); scrollDown();
  try {
    const res = await fetch("/api/chat", { method: "POST", headers: { "Content-Type": "application/json" },
                                           body: JSON.stringify({ message: text }) });
    if (!res.ok) throw new Error(res.statusText);
    const data = await res.json();
    bot.querySelector(".body").innerHTML = `<div dir="auto">${md(data.answer)}</div>`;
  } catch {
    bot.querySelector(".body").textContent = t().error;
  } finally {
    setBusy(false); scrollDown(); $("input").focus();
  }
}

function setBusy(busy) { $("send").disabled = busy || !$("input").value.trim(); $("send").dataset.busy = busy ? "1" : ""; }
function autosize() { const el = $("input"); el.style.height = "auto"; el.style.height = Math.min(el.scrollHeight, 200) + "px"; }

$("input").addEventListener("input", () => { autosize(); if (!$("send").dataset.busy) setBusy(false); });
$("input").addEventListener("keydown", (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(e.target.value); } });
$("form").onsubmit = (e) => { e.preventDefault(); send($("input").value); };
$("btn-new").onclick = () => { $("thread").innerHTML = ""; $("thread").classList.add("hidden"); $("empty").classList.remove("hidden"); };
$("btn-lang").onclick = () => { lang = lang === "ar" ? "en" : "ar"; store.set("nexus_lang", lang); applyLang(); };

applyLang();
setBusy(false);
