"""In-memory usage statistics for the developer dashboard (reset on restart)."""
import threading
import time
from collections import Counter, deque


class UsageStats:
    def __init__(self, keep_recent: int = 200):
        self.started = time.time()
        self.questions = 0
        self.agent_steps = 0
        self.total_ms = 0
        self.intents: Counter = Counter()
        self.verified = 0
        self.recent: deque = deque(maxlen=keep_recent)
        self._lock = threading.Lock()

    def record(self, message: str, result: dict) -> None:
        with self._lock:
            self.questions += 1
            self.agent_steps += len(result.get("steps", []))
            self.total_ms += result.get("ms", 0)
            intent = result.get("intent", "unknown")
            self.intents[intent] += 1
            ok = all(s["status"] == "ok" for s in result.get("steps", []))
            self.verified += ok
            self.recent.appendleft({"text": message[:200], "intent": intent, "neural": result.get("neural_intent"), "ok": ok,
                                    "confidence": result.get("confidence"),
                                    "time": time.strftime("%H:%M:%S"), "date": time.strftime("%Y-%m-%d")})

    def snapshot(self) -> dict:
        with self._lock:
            n = self.questions or 1
            return {"questions": self.questions, "agent_steps": self.agent_steps,
                    "avg_ms": round(self.total_ms / n), "verified_rate": round(self.verified / n, 3),
                    "intents": dict(self.intents), "uptime_s": int(time.time() - self.started),
                    "recent": list(self.recent)}
