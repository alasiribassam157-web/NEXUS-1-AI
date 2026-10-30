"""Official NEXUS benchmark: 254 realistic questions with the expected skill and answer.

Run:  py -m tests.benchmark      (writes models/benchmark.json, shown in the developer dashboard)
"""
import json
import sys
import time

from agent.orchestrator import NexusAgent
from core.trainer import MODELS

from tests.benchmark_cases import CASES_V3
from tests.benchmark_cases_v4 import CASES_V4

# Run `py -m tests.benchmark v3` to score only the NEXUS-3 questions.
CASES = CASES_V3 if "v3" in sys.argv[1:] else CASES_V3 + CASES_V4


def run(verbose: bool = True) -> dict:
    agent, failures, by_intent = NexusAgent(), [], {}
    start = time.time()
    for question, intent, expect in CASES:
        r = agent.handle(question)
        ok = r.get("intent") == intent and expect.lower() in r["answer"].lower()
        bucket = by_intent.setdefault(intent, [0, 0])
        bucket[0] += ok
        bucket[1] += 1
        if not ok:
            failures.append({"q": question, "want": intent, "got": r.get("intent"), "answer": r["answer"][:160]})
        if verbose:
            print(f"{'PASS' if ok else 'FAIL'}  [{r.get('intent')}] {question}", flush=True)
    passed = len(CASES) - len(failures)
    report = {"date": time.strftime("%Y-%m-%d %H:%M"), "total": len(CASES), "passed": passed,
              "accuracy": round(passed / len(CASES), 4), "seconds": round(time.time() - start, 1),
              "by_intent": {k: {"passed": v[0], "total": v[1]} for k, v in by_intent.items()}, "failures": failures}
    (MODELS / "benchmark.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    return report


if __name__ == "__main__":
    result = run()
    print(f"\nBenchmark: {result['passed']}/{result['total']} = {result['accuracy']:.1%}  ({result['seconds']}s)")
    for f in result["failures"]:
        print(f"  ✗ {f['q']}  want={f['want']} got={f['got']}  → {f['answer'][:90]!r}")
    sys.exit(0)
