"""NEXUS-1 platform server.  Run:  py app.py   →  http://localhost:8000"""
import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import dev_api
from agent.orchestrator import NexusAgent
from agent.stats import UsageStats
from agent.tools import SAFE_MODE
from core import trainer
from core.training_job import TrainingJob

ROOT = Path(__file__).resolve().parent
DEVTOOLS = ROOT / "devtools"  # developer dashboard: kept on the laptop only (gitignored)

app = FastAPI(title="NEXUS-1", version="3.0")
app.mount("/ui", StaticFiles(directory=ROOT / "ui"), name="ui")
agent = NexusAgent()
stats = UsageStats()
job = TrainingJob(on_done=agent.brain.reload)
app.include_router(dev_api.build_router(agent, stats, job))


class ChatIn(BaseModel):
    message: str


@app.on_event("startup")
def _bootstrap():
    if not trainer.CHECKPOINT.exists():
        job.start()  # first boot (e.g. fresh cloud container): ~10 s micro-training


@app.get("/")
def index():
    return FileResponse(ROOT / "ui" / "index.html")


@app.get("/dev")
@app.get("/dev/{name}")
def dev_page(request: Request, name: str = "dev.html"):
    path = DEVTOOLS / Path(name).name
    if not dev_api.is_local(request) or not path.is_file():
        raise HTTPException(404)
    return FileResponse(path)


@app.get("/api/health")
def health():
    return {"status": "ok", "model_ready": agent.brain.ready}


@app.post("/api/chat")
def chat(body: ChatIn, request: Request):
    message = body.message.strip()[:4000]
    if not message:
        raise HTTPException(400, "Empty message")
    # Real code/system execution only for the developer sitting at this machine.
    allow_exec = not SAFE_MODE and dev_api.is_local(request)
    result = agent.handle(message, allow_exec=allow_exec)
    stats.record(message, result)
    return result


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    print(f"\n  NEXUS-1 →  http://localhost:{port}    developer: http://localhost:{port}/dev\n")
    uvicorn.run(app, host=host, port=port, log_level="warning")
