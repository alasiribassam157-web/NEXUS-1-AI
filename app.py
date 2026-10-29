"""NEXUS-1 platform server.  Run:  py app.py   →  http://localhost:8000"""
import os
import secrets
import threading
from pathlib import Path

import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agent.orchestrator import NexusAgent
from agent.tools import SAFE_MODE, WORKSPACE, _safe_path
from core import trainer

ROOT = Path(__file__).resolve().parent
TOKEN_FILE = ROOT / ".nexus_token"


def _load_token() -> str:
    token = os.getenv("NEXUS_ACCESS_TOKEN")
    if token:
        return token
    if not TOKEN_FILE.exists():
        TOKEN_FILE.write_text(secrets.token_urlsafe(24), encoding="utf-8")
    return TOKEN_FILE.read_text(encoding="utf-8").strip()


ACCESS_TOKEN = _load_token()
app = FastAPI(title="NEXUS-1", version="1.0")
app.mount("/ui", StaticFiles(directory=ROOT / "ui"), name="ui")
agent = NexusAgent()
train_state = {"running": False, "history": [], "result": None, "error": None}
train_lock = threading.Lock()


def require_token(x_nexus_token: str = Header(default=""), token: str = Query(default="")):
    if not secrets.compare_digest(x_nexus_token or token, ACCESS_TOKEN):
        raise HTTPException(status_code=401, detail="Invalid or missing access token")


class ChatIn(BaseModel):
    message: str


def _run_training():
    try:
        result = trainer.train(on_epoch=lambda m: train_state["history"].append(m))
        agent.brain.reload()
        train_state["result"] = {k: v for k, v in result.items() if k != "history"}
    except Exception as exc:  # surfaced to the UI instead of killing the thread silently
        train_state["error"] = str(exc)
    finally:
        train_state["running"] = False


def start_training() -> bool:
    with train_lock:
        if train_state["running"]:
            return False
        train_state.update(running=True, history=[], result=None, error=None)
    threading.Thread(target=_run_training, daemon=True).start()
    return True


@app.on_event("startup")
def _bootstrap():
    if not trainer.CHECKPOINT.exists():
        start_training()  # first boot (e.g. fresh cloud container): ~10 s micro-training


@app.get("/")
def index():
    return FileResponse(ROOT / "ui" / "index.html")


@app.get("/api/health")
def health():
    return {"status": "ok", "model_ready": agent.brain.ready, "safe_mode": SAFE_MODE}


@app.post("/api/chat", dependencies=[Depends(require_token)])
def chat(body: ChatIn):
    message = body.message.strip()
    if not message:
        raise HTTPException(400, "Empty message")
    return agent.handle(message[:4000])


@app.post("/api/train", dependencies=[Depends(require_token)])
def train():
    return {"started": start_training(), "running": train_state["running"]}


@app.get("/api/train/status", dependencies=[Depends(require_token)])
def train_status():
    return train_state


@app.get("/api/files", dependencies=[Depends(require_token)])
def list_files():
    files = [{"name": str(p.relative_to(WORKSPACE)).replace("\\", "/"), "size": p.stat().st_size,
              "mtime": p.stat().st_mtime} for p in WORKSPACE.rglob("*") if p.is_file()]
    return sorted(files, key=lambda f: -f["mtime"])[:200]


@app.get("/api/files/content", dependencies=[Depends(require_token)])
def file_content(name: str):
    try:
        path = _safe_path(name)
    except PermissionError as exc:
        raise HTTPException(403, str(exc))
    if not path.is_file():
        raise HTTPException(404, "Not found")
    return {"name": name, "content": path.read_text(encoding="utf-8", errors="replace")[:20000]}


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    print(f"\n  NEXUS-1 running →  http://localhost:{port}/?token={ACCESS_TOKEN}\n")
    uvicorn.run(app, host=host, port=port, log_level="warning")
