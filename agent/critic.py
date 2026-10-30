"""Internal critic: validates plans before execution and results after, with self-repair."""
import re

from agent.tools import WORKSPACE, ToolResult, _BLOCKED

CONFIDENCE_FLOOR = 0.60

# Independent keyword router used to cross-check low-confidence neural predictions.
_KEYWORDS = {
    "python": ["calculate", "compute", "python", "code", "احسب", "كود", "بايثون", "```", "كم يساوي"],
    "file": ["file", "folder", "directory", ".txt", ".md", ".csv", ".py", ".json", "ملف", "مجلد", "الملفات"],
    "web": ["search", "who is", "tell me about", "news", "ابحث", "معلومات عن", "من هو", "اخبار"],
    "system": ["command", "terminal", "ipconfig", "tasklist", "systeminfo", "الامر", "الأمر", "النظام"],
    "chat": ["hello", "hi", "thanks", "who are you", "مرحبا", "شكرا", "من انت", "كيف حالك"],
}


def keyword_intent(msg: str) -> str | None:
    low = msg.lower()
    scores = {k: sum(w in low for w in words) for k, words in _KEYWORDS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else None


def review_intent(msg: str, intent: str, confidence: float) -> tuple[str, str]:
    """Return (final_intent, note). Overrides the network only when it is unsure."""
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
    if plan["tool"] == "web" and "Source:" not in result.output:
        return False, "No verifiable source returned."
    return True, "Result validated."
