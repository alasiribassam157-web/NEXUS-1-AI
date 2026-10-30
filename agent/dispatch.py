"""Runs an approved plan with the right tool or skill."""
from agent import live_skills, safe_math, units
from agent.coder import CoderSkill
from agent.tools import FileManagerTool, PythonExecutorTool, SystemTaskTool, ToolResult, WebResearchTool

EXEC_ONLY_LOCAL = "This needs code/system execution, which is available only on the developer's machine."
TOOL_NAMES = {"python": "PythonExecutorTool", "file": "FileManagerTool", "web": "WebResearchTool",
              "system": "SystemTaskTool", "code": "CoderSkill", "weather": "WeatherSkill",
              "currency": "CurrencySkill", "datetime": "DateTimeSkill", "units": "UnitsSkill"}


class Dispatcher:
    def __init__(self):
        self.python, self.files = PythonExecutorTool(), FileManagerTool()
        self.web, self.system = WebResearchTool(), SystemTaskTool()
        self.coder = CoderSkill()
        self.last_code_task: tuple[str, float] = ("", 0.0)

    def execute(self, plan: dict, allow_exec: bool) -> ToolResult:
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
        if tool == "code":
            result, task, conf = self.coder.answer(args["query"])
            self.last_code_task = (task, conf)
            return result
        if tool == "weather":
            return live_skills.weather(args["query"])
        if tool == "currency":
            return live_skills.currency(args["query"])
        if tool == "datetime":
            return live_skills.date_time(args["query"])
        if tool == "units":
            return units.convert(args["query"])
        raise ValueError(f"Unknown tool {tool}")
