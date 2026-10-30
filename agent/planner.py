"""Turns (message, intent) into a concrete tool call: {tool, action, args}."""
import re

_AR_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩×÷", "0123456789*/")
_FNAME = re.compile(r"[\w\-./\\]+\.[A-Za-z0-9]{1,6}")
_CODE_BLOCK = re.compile(r"```(?:python|py)?\s*\n?(.*?)```", re.DOTALL)

SYSTEM_SHORTCUTS = [
    (("system info", "معلومات النظام"), "systeminfo | findstr /B /C:\"OS\" /C:\"System\" /C:\"Total Physical\""),
    (("ip", "عنوان ip", "my ip"), "ipconfig"),
    (("process", "العمليات"), "tasklist"),
    (("computer name", "اسم الجهاز"), "hostname"),
]

# (pattern, python template, safe_math recipe used when code execution is not allowed)
_MATH_PATTERNS = [
    (r"sum of (\d+) to (\d+)|مجموع (?:الاعداد )?من (\d+) (?:الى|إلى) (\d+)",
     "print(sum(range({0}, {1} + 1)))", "sum_range"),
    (r"factorial (?:of )?(\d+)|مضروب (?:العدد )?(\d+)", "import math\nprint(math.factorial({0}))", "factorial"),
    (r"fibonacci (\d+)|فيبوناتشي (\d+)",
     "a, b = 0, 1\nseq = []\nfor _ in range({0}):\n    seq.append(a)\n    a, b = b, a + b\nprint(seq)", "fibonacci"),
    (r"prime(?:s| numbers)? (?:under|below|less than) (\d+)|الاعداد الاولية (?:حتى|اقل من) (\d+)",
     "print([n for n in range(2, {0}) if all(n % d for d in range(2, int(n ** 0.5) + 1))])", "primes"),
    (r"average of ([\d.,\s]+)|متوسط ([\d.,\s]+)",
     "nums = [{0}]\nprint(sum(nums) / len(nums))", "average"),
]


def _after(text: str, markers: list[str]) -> str:
    low = text.lower()
    for m in markers:
        idx = low.find(m)
        if idx != -1:
            return text[idx + len(m):].strip(" :?؟.")
    return ""


_NUM = r"(\d+(?:\.\d+)?)"
_WORD_OPS = [  # spoken operators between two numbers -> symbols
    (r"ضرب|مضروب في|×|x|times|multiplied by", "*"), (r"زائد|plus", "+"),
    (r"ناقص|minus", "-"), (r"قسمة|مقسوم على|على|÷|divided by", "/"), (r"اس|أس|to the power of", "**"),
]
_FUNCS = {"sqrt", "pi", "e", "sin", "cos", "tan", "log", "log10", "exp", "abs", "round", "pow", "floor", "ceil"}


def to_expression(text: str) -> str:
    """'كم يساوي 15 ضرب 7' -> '15*7';  'what is 25% of 80' -> '(25/100*80)'."""
    text = text.lower()
    text = re.sub(_NUM + r"\s*[%٪]\s*(?:of|من)\s*" + _NUM, r"(\1/100*\2)", text)
    text = re.sub(r"(?:square root of|sqrt of|الجذر التربيعي\s*(?:لـ|ل|للعدد|ل\s)?)\s*" + _NUM, r"sqrt(\1)", text)
    for words, op in _WORD_OPS:
        text = re.sub(_NUM + r"\s*(?:" + words + r")\s*" + _NUM, r"\1" + op + r"\2", text)
        text = re.sub(_NUM + r"\s*(?:" + words + r")\s*" + _NUM, r"\1" + op + r"\2", text)  # chains: 1+2+3
    tokens = re.findall(r"[a-z_][a-z_0-9]*|\d+(?:\.\d+)?|[+\-*/().%^,]", text)
    kept = [t for t in tokens if not t[0].isalpha() or t in _FUNCS]
    return "".join(kept).strip(",")


def plan_python(msg: str) -> dict:
    block = _CODE_BLOCK.search(msg)
    if block:
        return {"tool": "python", "action": "run", "args": {"code": block.group(1).strip()}}
    text = msg.translate(_AR_DIGITS)
    for pattern, tpl, recipe in _MATH_PATTERNS:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            groups = [g.strip().strip(",") for g in m.groups() if g]
            return {"tool": "python", "action": "run", "args": {"code": tpl.format(*groups)},
                    "safe": {"op": recipe, "args": groups}}
    expr = to_expression(text)
    if not expr:
        return {"tool": "python", "action": "run", "args": {"code": "print('No computable expression found')"}}
    return {"tool": "python", "action": "run", "args": {"code": f"from math import *\nprint({expr})"},
            "source": "expr", "safe": {"op": "expr", "args": [expr]}}


def plan_file(msg: str) -> dict:
    low = msg.lower()
    fname_match = _FNAME.search(msg)
    fname = fname_match.group(0) if fname_match else ""
    if any(k in low for k in ("delete", "remove", "احذف", "امسح")):
        return {"tool": "file", "action": "delete", "args": {"name": fname}}
    if any(k in low for k in ("folder", "directory", "مجلد")) and not fname:
        folder = _after(msg, ["folder called", "folder named", "directory", "folder", "مجلد"])
        return {"tool": "file", "action": "mkdir", "args": {"name": folder.split()[0] if folder else "new_folder"}}
    if any(k in low for k in ("create", "write", "save", "انشئ", "أنشئ", "اكتب", "احفظ")) and fname:
        content = _after(msg, ["with content", "content:", "containing", "بالمحتوى", "يحتوي على"])
        if not content:
            m = re.search(r"(?:write|اكتب|احفظ|save)\s+(.+?)\s+(?:to|in|into|في)\s+(?:the file |file |الملف )?"
                          + re.escape(fname), msg, re.IGNORECASE)
            content = m.group(1).strip("\"'") if m else ""
        return {"tool": "file", "action": "create", "args": {"name": fname, "content": content}}
    if fname:
        return {"tool": "file", "action": "read", "args": {"name": fname}}
    folder = _after(msg, ["files in", "الملفات في"])
    return {"tool": "file", "action": "list", "args": {"folder": folder}}


def plan_web(msg: str) -> dict:
    # The research tool cleans the question itself (facts need the full phrasing, e.g. "عاصمة فرنسا").
    return {"tool": "web", "action": "search", "args": {"query": msg.strip()}}


def plan_system(msg: str) -> dict:
    tick = re.search(r"`([^`]+)`", msg)
    command = tick.group(1) if tick else _after(
        msg, ["run command", "system command", "execute", "run", "نفذ امر نظام", "نفذ الامر",
              "نفذ الأمر", "شغل الامر", "شغل في التيرمنال", "automate task"])
    command = re.sub(r"\s+(in terminal|please|now)$", "", command, flags=re.IGNORECASE)
    if not command:
        low = msg.lower()
        for keys, shortcut in SYSTEM_SHORTCUTS:
            if any(k in low for k in keys):
                command = shortcut
                break
    return {"tool": "system", "action": "run", "args": {"command": command}}


PLANNERS = {"python": plan_python, "file": plan_file, "web": plan_web, "system": plan_system}
SKILLS = ("code", "weather", "currency", "datetime", "units", "prayer", "translate")  # answered by dedicated skills


def make_plan(msg: str, intent: str) -> dict:
    if intent in SKILLS:
        return {"tool": intent, "action": "answer", "args": {"query": msg.strip()}}
    planner = PLANNERS.get(intent)
    return planner(msg) if planner else {"tool": "chat", "action": "reply", "args": {}}
