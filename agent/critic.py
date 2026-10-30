"""Internal critic: validates plans before execution and results after, with self-repair."""
import re

from agent.chat_replies import is_small_talk
from agent.code_kb import detect_language
from agent import units
from agent.live_skills import find_currencies
from agent.tools import WORKSPACE, ToolResult, _BLOCKED

CONFIDENCE_FLOOR = 0.60

# Independent keyword router used to cross-check low-confidence neural predictions.
_KEYWORDS = {
    "python": ["calculate", "compute", "احسب", "```", "كم يساوي"],
    "file": ["file", "folder", "directory", ".txt", ".md", ".csv", ".json", "ملف", "مجلد", "الملفات"],
    "web": ["search", "who is", "tell me about", "news", "ابحث", "معلومات عن", "من هو", "اخبار"],
    "system": ["command", "terminal", "ipconfig", "tasklist", "systeminfo", "الامر", "الأمر", "النظام"],
    "chat": ["hello", "hi", "thanks", "who are you", "مرحبا", "شكرا", "من انت", "كيف حالك"],
    "code": ["code", "كود", "function", "دالة", "loop", "لوب", "حلقة", "class", "كلاس", "array", "مصفوفة", "string",
             "برمجة", "sort", "رتب", "reverse", "اعكس", "json", "http", "api", "dictionary", "قاموس", "variable",
             "متغير", "exception", "try catch", "hello world", "list", "قائمة", "فنكشن", "random", "عشوائي"],
    "weather": ["weather", "temperature", "الطقس", "طقس", "الجو", "درجة الحرارة", "مطر", "rain"],
    "currency": ["exchange rate", "سعر صرف", "سعر الدولار", "دولار", "ريال", "يورو", "currency", "usd", "eur"],
    "datetime": ["what time", "الساعة", "الساعه", "التاريخ اليوم", "هجري", "الهجري", "today's date", "hijri"],
    "prayer": ["الصلاة", "صلاة", "اذان", "أذان", "prayer", "fajr", "maghrib", "الفجر", "المغرب", "العشاء"],
    "translate": ["ترجم", "translate", "بالانجليزي", "بالإنجليزي", "بالعربي", "in arabic", "in english", "معنى"],
    "units": ["convert", "حول", "كيلومتر", "ميل", "رطل", "فهرنهايت", "mile", "km", "kg", "feet", "pounds"],
}


def keyword_intent(msg: str) -> str | None:
    low = msg.lower()
    scores = {k: sum(w in low for w in words) for k, words in _KEYWORDS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else None


_MATH = re.compile(r"```|\d\s*([+\-*/^%×÷٪]|\*\*)\s*\d|\d\s*[%٪]|(\d.*(ضرب|زائد|ناقص|قسمة|على|times|plus|minus|divided))|"
                   r"(calculate|compute|solve|احسب|حل|كم يساوي|factorial|مضروب|sqrt|جذر|square root|fibonacci|"
                   r"فيبوناتشي|prime|الاولية|average|متوسط|sum of|مجموع)", re.IGNORECASE)
_CODE_TASK = re.compile(r"\b(?:for|while) loop\b|\btry catch\b|\bhello world\b|حلقة (?:for|while)|لوب", re.IGNORECASE)
# Unmistakable arithmetic: "15*7", "3 ^ 4", "25% of 80".
_STRONG_MATH = re.compile(r"\d\s*([+*/^×÷]|\*\*)\s*\d|\d\s*[%٪]\s*(of|من)\s*\d", re.IGNORECASE)


def review_intent(msg: str, intent: str, confidence: float) -> tuple[str, str]:
    """Return (final_intent, note). Overrides the network only when it is unsure or implausible."""
    final, note = _review_confidence(msg, intent, confidence)
    text = msg.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789"))
    if final == "python" and not _MATH.search(text):
        if detect_language(msg):
            return "code", note + " A programming language is named but no math — answering as a coding question."
        fallback = "units" if units.is_conversion(msg) else "web"  # «1 inch to cm» looks numeric but is a conversion
        return fallback, note + f" No arithmetic in the question — answering with {fallback} instead."
    if final in ("web", "chat", "currency", "units") and _STRONG_MATH.search(text):
        return "python", note + " The question contains arithmetic — calculating instead."
    if final in ("weather", "datetime", "currency", "units") and detect_language(msg):
        return "code", note + " A programming language is named — answering as a coding question."
    if final == "code" and not detect_language(msg) and keyword_intent(msg) != "code":
        return "web", note + " No programming language or coding words — answering via web search instead."
    if final in ("web", "chat") and _CODE_TASK.search(msg):
        return "code", note + " A clear coding task (loop, function, class…) — answering as a coding question."
    if final in ("web", "chat") and units.is_conversion(msg):
        return "units", note + " A number with two compatible units — converting instead of searching."
    if final == "units" and len(set(find_currencies(msg))) >= 2:
        return "currency", note + " Two currencies are named — converting money, not units."
    if final == "chat" and not is_small_talk(msg):
        return "web", note + " Not small talk — answering via web search instead."
    return final, note


def _review_confidence(msg: str, intent: str, confidence: float) -> tuple[str, str]:
    if confidence >= CONFIDENCE_FLOOR:
        return intent, f"Neural confidence {confidence:.0%} ≥ {CONFIDENCE_FLOOR:.0%} — accepted."
    alt = keyword_intent(msg)
    if alt and alt != intent:
        return alt, f"Low confidence ({confidence:.0%}); keyword cross-check prefers '{alt}'."
    if not alt and intent == "chat":
        # An unrecognised question is better answered by a search than by the canned greeting.
        return "web", f"Low confidence ({confidence:.0%}) and no keyword match — answering via web search."
    return intent, f"Low confidence ({confidence:.0%}) but no better alternative — proceeding."


def _repair_python(code: str) -> tuple[str, list[str]]:
    fixes = []
    if "^" in code and "**" not in code:
        code, fixes = code.replace("^", "**"), fixes + ["'^' → '**' (power operator)"]
    code2 = re.sub(r"(\d)\s*\(", r"\1*(", code)
    if code2 != code:
        code, fixes = code2, fixes + ["implicit multiplication made explicit"]
    return code, fixes


def review_plan(plan: dict) -> tuple[bool, dict, list[str]]:
    """Pre-execution check. Returns (approved, possibly-corrected plan, notes)."""
    tool, args, notes = plan["tool"], plan["args"], []
    if tool == "python":
        code = args["code"]
        if plan.get("source") == "expr" and "^" in code:
            # Valid Python, but in natural-language math '^' means power, not XOR.
            args["code"] = code = code.replace("^", "**")
            notes.append("Semantic fix: '^' interpreted as power (**), not bitwise XOR.")
        try:
            compile(code, "<nexus>", "exec")
            notes.append("Syntax check passed.")
        except SyntaxError as err:
            fixed, fixes = _repair_python(code)
            try:
                compile(fixed, "<nexus>", "exec")
                args["code"] = fixed
                notes.append(f"Syntax error ({err.msg}) self-corrected: " + "; ".join(fixes))
            except SyntaxError:
                return False, plan, [f"Syntax error not repairable: {err.msg} (line {err.lineno})"]
    elif tool == "file":
        if plan["action"] in ("create", "read", "delete") and not args.get("name"):
            return False, plan, ["No file name detected — please specify e.g. notes.txt"]
        notes.append(f"Target path confined to {WORKSPACE.name}/ — OK.")
    elif tool == "system":
        cmd = args.get("command", "")
        if not cmd:
            return False, plan, ["No command detected — wrap it in backticks, e.g. `dir`"]
        if _BLOCKED.search(cmd):
            return False, plan, [f"Command rejected as destructive: {cmd}"]
        notes.append("Command passed the safety filter.")
    elif tool == "web":
        if len(args.get("query", "")) < 2:
            return False, plan, ["Search query is empty."]
        notes.append(f"Query: “{args['query']}”.")
    else:
        notes.append(f"Skill input accepted: “{args.get('query', '')[:120]}”.")
    return True, plan, notes


def review_result(plan: dict, result: ToolResult) -> tuple[bool, str]:
    """Post-execution verification."""
    if not result.ok:
        return False, "Tool reported failure — output shown for diagnosis."
    if plan["tool"] == "file" and plan["action"] == "create":
        written = (WORKSPACE / plan["args"]["name"]).read_text(encoding="utf-8")
        if written != plan["args"].get("content", ""):
            return False, "Read-back mismatch: file content differs from request!"
        return True, "Read-back verified: file content matches exactly."
    if plan["tool"] == "python" and "Traceback" in result.output:
        return False, "Runtime traceback detected."
    if plan["tool"] == "web" and "🔗 http" not in result.output:
        return False, "No verifiable source returned."
    if plan["tool"] == "code" and "```" not in result.output:
        return False, "No code block in the answer."
    return True, "Result validated."
