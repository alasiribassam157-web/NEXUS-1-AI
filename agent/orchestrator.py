"""NEXUS-1 agent loop: Perceive → Plan → Critic → Act → Verify → Answer."""
import re
import time

from agent import critic, safe_math
from agent.planner import make_plan
from agent.tools import (FileManagerTool, PythonExecutorTool, SystemTaskTool, ToolResult,
                         WebResearchTool)
from core.inference import BrainInference

EXEC_ONLY_LOCAL = "This needs code/system execution, which is available only on the developer's machine."

CHAT_REPLIES = {
    "en": "I'm **NEXUS-1**, an autonomous agent with a custom Transformer brain. I can:\n"
          "• compute / run Python (`calculate 2**10`, or paste a ```python block)\n"
          "• manage files (`create file notes.txt with content hi`, `list files`)\n"
          "• research the web (`search for quantum computing`)\n"
          "• run system commands (`run command `ipconfig``)",
    "ar": "أنا **NEXUS-1**، وكيل ذكي مستقل بعقل Transformer مخصص. أستطيع:\n"
          "• الحساب وتشغيل بايثون (`احسب 2**10`)\n"
          "• إدارة الملفات (`انشئ ملف notes.txt`، `اعرض الملفات`)\n"
          "• البحث في الإنترنت (`ابحث عن الذكاء الاصطناعي`)\n"
          "• تنفيذ أوامر النظام (`نفذ الامر `dir``)",
}


class NexusAgent:
    def __init__(self):
        self.brain = BrainInference()
        self.python, self.files = PythonExecutorTool(), FileManagerTool()
        self.web, self.system = WebResearchTool(), SystemTaskTool()

    def _execute(self, plan: dict, allow_exec: bool) -> ToolResult:
        tool, action, args = plan["tool"], plan["action"], plan["args"]
        if tool == "python":
            if allow_exec:
                return self.python.run(args["code"])
            if plan.get("safe"):
                try:
                    return ToolResult(True, safe_math.evaluate(plan["safe"]["op"], plan["safe"]["args"]))
                except (ValueError, ArithmeticError, SyntaxError, TypeError) as exc:
                    return ToolResult(False, f"Could not calculate: {exc}")
            return ToolResult(False, EXEC_ONLY_LOCAL)
        if tool == "file":
            return getattr(self.files, action)(**args)
        if tool == "web":
            return self.web.search(args["query"])
        if tool == "system":
            return self.system.run(args["command"]) if allow_exec else ToolResult(False, EXEC_ONLY_LOCAL)
        raise ValueError(f"Unknown tool {tool}")

    def handle(self, message: str, allow_exec: bool = False) -> dict:
        """allow_exec: run real Python/system commands (only for the developer's own machine)."""
        t0 = time.time()
        lang = "ar" if re.search(r"[؀-ۿ]", message) else "en"
        steps = []

        def step(stage: str, title: str, detail: str = "", status: str = "ok"):
            steps.append({"stage": stage, "title": title, "detail": detail, "status": status})

        # 1. Perceive — neural intent classification
        if not self.brain.ready and not self.brain.reload():
            step("plan", "Brain not trained", "Open the Training Studio and train first.", "error")
            return {"steps": steps, "answer": "⚠️ Model not trained yet.", "files": []}
        intent, conf, dist = self.brain.predict(message)
        step("plan", f"Intent: {intent} ({conf:.0%})",
             " · ".join(f"{k} {v:.0%}" for k, v in sorted(dist.items(), key=lambda kv: -kv[1])))

        # 2. Critic reviews the classification itself
        intent, note = critic.review_intent(message, intent, conf)
        step("critic", "Intent review", note)

        if intent == "chat":
            step("result", "Direct reply", "No tool needed.")
            return {"steps": steps, "answer": CHAT_REPLIES[lang], "files": [], "intent": intent,
                    "confidence": round(conf, 3), "ms": int((time.time() - t0) * 1000)}

        # 3. Plan the tool call and let the critic approve / repair it
        plan = make_plan(message, intent)
        tool_name = {"python": "PythonExecutorTool", "file": "FileManagerTool",
                     "web": "WebResearchTool", "system": "SystemTaskTool"}[plan["tool"]]
        step("tool", f"{tool_name}.{plan['action']}", _preview(plan["args"]))
        approved, plan, notes = critic.review_plan(plan)
        step("critic", "Pre-execution check", "\n".join(notes), "ok" if approved else "error")
        if not approved:
            return {"steps": steps, "answer": "❌ " + notes[-1], "files": [], "intent": intent,
                    "confidence": round(conf, 3), "ms": int((time.time() - t0) * 1000)}

        # 4. Act, then verify; one self-correcting retry for Python runtime errors
        result = self._execute(plan, allow_exec)
        valid, verdict = critic.review_result(plan, result)
        if not valid and allow_exec and plan["tool"] == "python" and "Traceback" in result.output:
            fixed = "from math import *\nimport statistics, json, re\n" + plan["args"]["code"]
            step("critic", "Self-correction", "Runtime error — retrying with standard imports.", "warn")
            plan["args"]["code"] = fixed
            result = self._execute(plan, allow_exec)
            valid, verdict = critic.review_result(plan, result)
        step("critic", "Post-execution verification", verdict, "ok" if valid else "warn")

        short = "\n" not in result.output and len(result.output) < 160
        if plan["tool"] == "web" or not result.ok:
            answer = result.output
        else:
            answer = f"**{result.output}**" if short else f"```\n{result.output}\n```"
        step("result", "Final answer", "Verified ✓" if valid else "Unverified — review output",
             "ok" if valid else "warn")
        return {"steps": steps, "answer": answer, "files": result.files, "intent": intent,
                "confidence": round(conf, 3), "ms": int((time.time() - t0) * 1000)}


def _preview(args: dict) -> str:
    return "\n".join(f"{k}: {str(v)[:300]}" for k, v in args.items())
