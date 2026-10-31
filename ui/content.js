// NEXUS user page: texts, icons, cities and popular questions (loaded first).
const ICONS = {
  web: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
  code: '<path d="m8 8-4 4 4 4M16 8l4 4-4 4M14 5l-4 14"/>',
  weather: '<circle cx="12" cy="10" r="4"/><path d="M12 2v2M4.9 4.9l1.4 1.4M2 10h2M17.7 6.3l1.4-1.4M7 18h10a3 3 0 0 0 0-6"/>',
  currency: '<circle cx="9" cy="9" r="6"/><path d="M15.5 9.5a6 6 0 1 1-6 6"/>',
  python: '<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M8 7h8M8 12h2M12 12h2M8 16h2M12 16h2"/>',
  datetime: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  units: '<path d="M3 17 17 3l4 4L7 21zM7 13l2 2M10 10l2 2M13 7l2 2"/>',
  prayer: '<path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/>',
  translate: '<path d="M4 5h8M8 3v2M5 9c1.5 3 4 5 7 6M11 5c-1 4-4 8-7 10M14 21l4-9 4 9M15.5 18h5"/>',
  link: '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7L11.5 7M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1.5-1.5"/>',
  copy: '<rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h10"/>',
  check: '<path d="m5 12 5 5 9-10"/>', chat: '<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/>',
};
const svg = (name) => `<svg viewBox="0 0 24 24" aria-hidden="true">${ICONS[name] || ""}</svg>`;

const T = {
  ar: { morning: "صباح الخير", evening: "مساء الخير", ask: "وش تبي تعرف؟", city: "مدينتك",
        weatherNow: "الطقس الآن", nextPrayer: "الصلاة القادمة", dollar: "الدولار اليوم", sar: "ريال سعودي",
        codeDay: "مثال برمجي اليوم", after: "بعد", hours: "س", minutes: "د", unavailable: "غير متاح الآن",
        popular: "أسئلة مشهورة", history: "المحادثات", newChat: "محادثة جديدة", today: "اليوم", earlier: "سابقاً",
        empty: "ما فيه محادثات للحين", placeholder: "اسأل NEXUS عن أي شيء…",
        hint: "NEXUS قد يخطئ أحياناً، تحقّق من المعلومات المهمة.", error: "تعذّر الوصول للخادم، حاول مرة ثانية.",
        copy: "نسخ", copied: "تم النسخ", source: "المصدر", dark: "الوضع الليلي", light: "الوضع النهاري", langBtn: "EN",
        cats: { web: "معرفة", code: "برمجة", weather: "طقس", currency: "عملات", python: "حساب", datetime: "الوقت",
                units: "تحويل", prayer: "الصلاة", translate: "ترجمة" },
        skills: { chat: "محادثة", file: "ملفات", system: "نظام" } },
  en: { morning: "Good morning", evening: "Good evening", ask: "What's on your mind?", city: "Your city",
        weatherNow: "Weather now", nextPrayer: "Next prayer", dollar: "US dollar today", sar: "Saudi riyal",
        codeDay: "Code of the day", after: "in", hours: "h", minutes: "m", unavailable: "Unavailable right now",
        popular: "Popular questions", history: "Conversations", newChat: "New chat", today: "Today", earlier: "Earlier",
        empty: "No conversations yet", placeholder: "Ask NEXUS anything…",
        hint: "NEXUS can make mistakes. Verify important information.", error: "Couldn't reach the server, please try again.",
        copy: "Copy", copied: "Copied", source: "Source", dark: "Dark mode", light: "Light mode", langBtn: "ع",
        cats: { web: "Knowledge", code: "Code", weather: "Weather", currency: "Currency", python: "Math", datetime: "Time",
                units: "Units", prayer: "Prayer", translate: "Translate" },
        skills: { chat: "Chat", file: "Files", system: "System" } },
};

// [Arabic, English] names used for the dashboard city picker (sent to the geocoder as-is)
const CITIES = [["الرياض", "Riyadh"], ["جدة", "Jeddah"], ["مكة المكرمة", "Mecca"], ["المدينة المنورة", "Medina"],
  ["الدمام", "Dammam"], ["أبها", "Abha"], ["تبوك", "Tabuk"], ["دبي", "Dubai"], ["الكويت", "Kuwait City"],
  ["الدوحة", "Doha"], ["المنامة", "Manama"], ["مسقط", "Muscat"], ["القاهرة", "Cairo"], ["عمّان", "Amman"], ["لندن", "London"]];

// category -> [Arabic question, English question] pairs shown under the composer
const POPULAR = {
  web: [["ما هي عاصمة اليابان؟", "What is the capital of Japan?"], ["كم ارتفاع برج خليفة؟", "How tall is Mount Everest?"],
        ["من مؤسس جوجل؟", "Who founded Tesla?"], ["اشرح لي الثقب الأسود باختصار", "Explain photosynthesis in short"]],
  code: [["كيف أعكس نص في بايثون؟", "How to reverse a string in Python"], ["حلقة for في جافاسكربت", "For loop in JavaScript"],
         ["كيف أقرأ ملف في جافا؟", "Parse JSON in JavaScript"], ["مثال على كلاس في C#", "Create a class in C++"]],
  prayer: [["مواقيت الصلاة في الرياض", "Prayer times in Mecca"], ["متى أذان المغرب في جدة؟", "When is maghrib in Cairo?"],
           ["وقت صلاة الفجر في المدينة", "Fajr time in London"], ["مواقيت الصلاة في دبي", "Prayer times in Istanbul"]],
  weather: [["كيف الجو في الرياض؟", "Weather in Riyadh"], ["الطقس في دبي", "Weather in London"],
            ["درجة الحرارة في أبها", "Temperature in Tokyo"], ["هل الجو حار في جدة؟", "Is it cold in Paris?"]],
  currency: [["كم سعر الدولار بالريال؟", "Convert 100 USD to EUR"], ["حول 100 يورو الى ريال", "How much is 50 GBP in dollars"],
             ["كم 1000 ين بالدولار؟", "1000 yen in dollars"], ["سعر الدرهم مقابل الريال", "Euro to dollar"]],
  translate: [["ترجم صقر للانجليزي", "How do you say coffee in Arabic?"], ["وش معنى friend بالعربي؟", "Translate الذكاء الاصطناعي"],
              ["ترجم برج خليفة للانجليزي", "What is book in Arabic?"], ["كيف أقول مدرسة بالانجليزي؟", "Translate good morning to Arabic"]],
  python: [["كم 15٪ من 200؟", "What is 15% of 200"], ["احسب مضروب 10", "Calculate 2 ** 16"],
           ["كم يساوي 125 ضرب 8؟", "Square root of 144"], ["الجذر التربيعي لـ 625", "What is 7 times 8"]],
  datetime: [["التاريخ الهجري اليوم", "What is the hijri date today?"], ["كم الساعة الحين؟", "What time is it?"]],
  units: [["حول 10 كيلومتر الى ميل", "Convert 5 miles to km"], ["100 فهرنهايت كم مئوية", "Convert 70 kg to pounds"]],
};
