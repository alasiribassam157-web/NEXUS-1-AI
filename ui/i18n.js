// Bilingual strings (English / Arabic RTL)
window.I18N = {
  en: {
    tagline: "Autonomous Agent · Custom Transformer Brain",
    safe: "Safe mode", command_room: "Agent Command Room", studio: "Neural Training Studio",
    train: "Train / Upgrade Model", training: "Training…", epoch: "Epoch", val_acc: "Val Acc",
    time: "Time", files: "Task & File Monitor", placeholder: "Give NEXUS-1 a task…",
    model_ready: "Brain online", model_missing: "Brain untrained", no_files: "No files yet — ask the agent to create some.",
    gate_title: "Enter access token", gate_ph: "Token from .nexus_token", gate_btn: "Unlock",
    done: (r) => `Done: ${r.params.toLocaleString()} params in ${r.seconds}s → nexus_brain.pt`,
    busy: "Training already in progress", welcome: "Welcome to **NEXUS-1**. Assign me a task — I'll plan it, choose a tool, verify it with my internal critic, then answer.",
    stages: { plan: "Plan", tool: "Tool", critic: "Critic", result: "Result" },
    suggestions: ["calculate factorial of 12", "create file notes.txt with content Hello NEXUS", "list files",
                  "search for machine learning", "run command `whoami`"],
  },
  ar: {
    tagline: "وكيل ذكي مستقل · عقل Transformer مخصص",
    safe: "الوضع الآمن", command_room: "غرفة قيادة الوكيل", studio: "استوديو التدريب العصبي",
    train: "تدريب / تطوير النموذج", training: "جارٍ التدريب…", epoch: "الحقبة", val_acc: "دقة التحقق",
    time: "الوقت", files: "مراقب المهام والملفات", placeholder: "أعطِ NEXUS-1 مهمة…",
    model_ready: "العقل يعمل", model_missing: "العقل غير مدرب", no_files: "لا توجد ملفات بعد — اطلب من الوكيل إنشاء ملف.",
    gate_title: "أدخل رمز الدخول", gate_ph: "الرمز من ملف .nexus_token", gate_btn: "دخول",
    done: (r) => `تم: ${r.params.toLocaleString()} معامل خلال ${r.seconds} ثانية`,
    busy: "التدريب يعمل بالفعل", welcome: "مرحباً بك في **NEXUS-1**. أعطني مهمة — سأخطط لها، أختار الأداة، أتحقق منها بالمدقق الداخلي، ثم أجيب.",
    stages: { plan: "تخطيط", tool: "أداة", critic: "تدقيق", result: "النتيجة" },
    suggestions: ["احسب 2**20", "انشئ ملف ideas.txt", "اعرض الملفات", "ابحث عن الذكاء الاصطناعي", "نفذ الامر `hostname`"],
  },
};
