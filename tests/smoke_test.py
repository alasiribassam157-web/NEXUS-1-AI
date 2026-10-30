"""Fast end-to-end checks run before every push.  Run:  py -m tests.smoke_test"""
import sys

from core import trainer

if not trainer.CHECKPOINT.exists():
    trainer.train()

from agent.orchestrator import NexusAgent  # noqa: E402  (needs the checkpoint)
from agent.tools import SAFE_MODE, WORKSPACE  # noqa: E402

agent = NexusAgent()
failures = []


def check(name: str, message: str, intent: str, expect_in_answer: str = "", allow_exec: bool = False):
    result = agent.handle(message, allow_exec=allow_exec)
    ok = result.get("intent") == intent and expect_in_answer in result["answer"]
    print(f"{'PASS' if ok else 'FAIL'}  {name}")
    if not ok:
        failures.append(f"{name}: intent={result.get('intent')} answer={result['answer'][:120]!r}")


check("chat (en)", "hello there", "chat", "NEXUS-1")
check("chat (ar)", "مرحبا كيف حالك", "chat", "NEXUS-1")
check("file create", "create file _smoke.txt with content ok123", "file", "Created")
check("file read", "read _smoke.txt", "file", "ok123")
# Public visitors: math runs through the safe evaluator, never as code.
check("safe calc", "calculate 2 ** 10", "python", "1024")
check("safe ^ power", "what is 3^4 + 2", "python", "83")
check("safe arabic", "احسب مضروب 5", "python", "120")
check("no code for public", "run command `whoami`", "system", "developer's machine")
if not SAFE_MODE:
    check("python calc", "calculate 2 ** 10", "python", "1024", allow_exec=True)
    check("arabic math", "احسب مضروب 5", "python", "120", allow_exec=True)

(WORKSPACE / "_smoke.txt").unlink(missing_ok=True)
for leftover in WORKSPACE.glob("run_*.py"):
    leftover.unlink()

if failures:
    print("\n".join(["", "FAILED:"] + failures))
    sys.exit(1)
print("\nAll smoke tests passed.")
