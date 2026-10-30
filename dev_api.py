"""Developer-only API. Reachable only from the developer's own machine.

Anyone else (the public cloud link, the tunnel) gets 404, as if it did not exist.
The laptop can also read the cloud's stats through /api/dev/cloud using a private key
kept in .nexus_cloud.json (gitignored); the same key is set on Render as NEXUS_ACCESS_TOKEN.
"""
import json
import os
import secrets
from pathlib import Path

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from agent.tools import WORKSPACE
from core import trainer
from core.dataset_builder import INTENTS, add_custom, load_custom

ROOT = Path(__file__).resolve().parent
CLOUD_KEY = os.getenv("NEXUS_ACCESS_TOKEN", "").strip()
CLOUD_CFG = ROOT / ".nexus_cloud.json"
# Tunnels and cloud proxies add these; a request carrying any of them is not from this machine.
_PROXY_HEADERS = ("x-forwarded-for", "cf-connecting-ip", "x-real-ip", "forwarded")


def is_local(request: Request) -> bool:
    host = request.client.host if request.client else ""
    return host in ("127.0.0.1", "::1") and not any(h in request.headers for h in _PROXY_HEADERS)


def require_dev(request: Request):
    key = request.headers.get("x-nexus-key", "").strip()
    if is_local(request) or (CLOUD_KEY and key and secrets.compare_digest(key, CLOUD_KEY)):
        return
    raise HTTPException(status_code=404)


class TrainIn(BaseModel):
    size: str = "small"
    epochs: int = 12


class TeachIn(BaseModel):
    text: str
    intent: str


def build_router(agent, stats, job) -> APIRouter:
    router = APIRouter(prefix="/api/dev", dependencies=[Depends(require_dev)])

    @router.get("/overview")
    def overview():
        return {"brain": agent.brain.info, "usage": stats.snapshot(), "versions": trainer.load_versions(),
                "taught": len(load_custom()), "intents": INTENTS, "sizes": list(trainer.SIZES)}

    @router.post("/train")
    def train(body: TrainIn):
        if body.size not in trainer.SIZES:
            raise HTTPException(400, f"size must be one of {list(trainer.SIZES)}")
        return {"started": job.start(body.size, max(1, min(body.epochs, 60)))}

    @router.get("/train/status")
    def train_status():
        return job.state

    @router.post("/teach")
    def teach(body: TeachIn):
        if body.intent not in INTENTS or not body.text.strip():
            raise HTTPException(400, f"intent must be one of {INTENTS} and text non-empty")
        return {"taught": add_custom(body.text, body.intent)}

    @router.get("/files")
    def files():
        items = [{"name": str(p.relative_to(WORKSPACE)).replace("\\", "/"), "size": p.stat().st_size,
                  "mtime": p.stat().st_mtime} for p in WORKSPACE.rglob("*") if p.is_file()]
        return sorted(items, key=lambda f: -f["mtime"])[:200]

    @router.get("/cloud")
    def cloud(request: Request):
        """Laptop only: fetch the live cloud platform's overview with the private key."""
        if not is_local(request):
            raise HTTPException(404)
        try:
            cfg = json.loads(CLOUD_CFG.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {"configured": False}
        try:
            res = httpx.get(cfg["url"].rstrip("/") + "/api/dev/overview",
                            headers={"x-nexus-key": cfg["key"]}, timeout=70)
            res.raise_for_status()
        except httpx.HTTPError as exc:
            return {"configured": True, "url": cfg["url"], "error": str(exc)}
        return {"configured": True, "url": cfg["url"], **res.json()}

    return router
