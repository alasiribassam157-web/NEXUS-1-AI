"""NEXUS-1 platform server.  Run:  py app.py   →  http://localhost:8000  (developer: /dev)"""
import os
import secrets
from pathlib import Path

import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agent.orchestrator import NexusAgent
from agent.stats import UsageStats
from agent.tools import SAFE_MODE, WORKSPACE, _safe_path
from core import trainer
from core.dataset_builder import INTENTS, add_custom, load_custom
from core.training_job import TrainingJob

ROOT = Path(__file__).resolve().parent
TOKEN_FILE = ROOT / ".nexus_token"


def _load_token() -> str:
    # Strip: dashboard text boxes often add a trailing newline/space when pasting.
    token = os.getenv("NEXUS_ACCESS_TOKEN", "").strip()
    if token:
        return token
    if not TOKEN_FILE.exists():
        TOKEN_FILE.write_text(secrets.token_urlsafe(24), encoding="utf-8")
    return TOKEN_FILE.read_text(encoding="utf-8").strip()


ACCESS_TOKEN = _load_token()
PUBLIC_CHAT = SAFE_MODE  # a laptop with full tools behind a tunnel must stay token-protected
app = FastAPI(title="NEXUS-1", version="2.0")
app.mount("/ui", StaticFiles(directory=ROOT / "ui"), name="ui")
agent = NexusAgent()
stats = UsageStats()
job = TrainingJob(on_done=agent.brain.reload)


def _token_ok(header: str, query: str) -> bool:
    return secrets.compare_digest((header or query).strip(), ACCESS_TOKEN)


def require_dev(x_nexus_token: str = Header(default=""), token: str = Query(default="")):
    if not _token_ok(x_nexus_token, token):
        raise HTTPException(status_code=401, detail="Invalid or missing developer password")


def require_chat(x_nexus_token: str = Header(default=""), token: str = Query(default="")):
    if not PUBLIC_CHAT and not _token_ok(x_nexus_token, token):
        raise HTTPException(status_code=401, detail="Invalid or missing access token")


class ChatIn(BaseModel):
    message: str


class TrainIn(BaseModel):
    size: str = "small"
    epochs: int = 12


class TeachIn(BaseModel):
    text: str
    intent: str


@app.on_event("startup")
def _bootstrap():
    if not trainer.CHECKPOINT.exists():
        job.start()  # first boot (e.g. fresh cloud container): ~10 s micro-training


@app.get("/")
def index():
    return FileResponse(ROOT / "ui" / "index.html")


@app.get("/dev")
def dev_page():
    return FileResponse(ROOT / "ui" / "dev.html")


@app.get("/api/health")
def health():
    return {"status": "ok", "model_ready": agent.brain.ready, "safe_mode": SAFE_MODE,
            "auth": not PUBLIC_CHAT}


@app.post("/api/chat", dependencies=[Depends(require_chat)])
def chat(body: ChatIn):
    message = body.message.strip()[:4000]
    if not message:
        raise HTTPException(400, "Empty message")
    result = agent.handle(message)
    stats.record(message, result)
    return result


@app.get("/api/dev/overview", dependencies=[Depends(require_dev)])
def dev_overview():
    return {"brain": agent.brain.info, "usage": stats.snapshot(), "versions": trainer.load_versions(),
            "taught": len(load_custom()), "intents": INTENTS, "sizes": list(trainer.SIZES)}


@app.post("/api/dev/train", dependencies=[Depends(require_dev)])
def train(body: TrainIn):
    if body.size not in trainer.SIZES:
        raise HTTPException(400, f"size must be one of {list(trainer.SIZES)}")
    return {"started": job.start(body.size, max(1, min(body.epochs, 60)))}


@app.get("/api/dev/train/status", dependencies=[Depends(require_dev)])
def train_status():
    return job.state


@app.post("/api/dev/teach", dependencies=[Depends(require_dev)])
def teach(body: TeachIn):
    if body.intent not in INTENTS or not body.text.strip():
        raise HTTPException(400, f"intent must be one of {INTENTS} and text non-empty")
    return {"taught": add_custom(body.text, body.intent)}


@app.get("/api/dev/files", dependencies=[Depends(require_dev)])
def list_files():
    files = [{"name": str(p.relative_to(WORKSPACE)).replace("\\", "/"), "size": p.stat().st_size,
              "mtime": p.stat().st_mtime} for p in WORKSPACE.rglob("*") if p.is_file()]
    return sorted(files, key=lambda f: -f["mtime"])[:200]


@app.get("/api/dev/files/content", dependencies=[Depends(require_dev)])
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
    print(f"\n  NEXUS-1 →  http://localhost:{port}/?token={ACCESS_TOKEN}   (developer: /dev)\n")
    uvicorn.run(app, host=host, port=port, log_level="warning")
