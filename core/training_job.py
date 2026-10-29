"""Runs training in a background thread and exposes live progress to the API."""
import threading
from typing import Callable

from core import trainer


class TrainingJob:
    def __init__(self, on_done: Callable[[], None]):
        self.on_done = on_done
        self.state = {"running": False, "history": [], "result": None, "error": None}
        self._lock = threading.Lock()

    def start(self, size: str = "small", epochs: int = 12) -> bool:
        with self._lock:
            if self.state["running"]:
                return False
            self.state.update(running=True, history=[], result=None, error=None)
        threading.Thread(target=self._run, args=(size, epochs), daemon=True).start()
        return True

    def _run(self, size: str, epochs: int) -> None:
        try:
            result = trainer.train(size=size, epochs=epochs,
                                   on_epoch=lambda m: self.state["history"].append(m))
            self.on_done()
            self.state["result"] = {k: v for k, v in result.items() if k != "history"}
        except Exception as exc:  # surfaced to the UI instead of killing the thread silently
            self.state["error"] = str(exc)
        finally:
            self.state["running"] = False
