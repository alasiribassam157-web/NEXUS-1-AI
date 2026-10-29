---
title: NEXUS-1
emoji: 🧠
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# NEXUS-1 — Autonomous AI Platform

A self-contained AI platform built from scratch:

- **`core/`** — a custom mini-Transformer (multi-head self-attention, feed-forward,
  LayerNorm, positional encoding, custom Arabic/English tokenizer) trained in
  under 15 seconds on CPU to classify user intent and route tasks.
- **`agent/`** — an orchestrator that plans → picks a tool → runs a critic check →
  self-corrects → answers. Tools: Python executor, file manager, web research,
  system commands (all confined to `workspace/`).
- **`ui/` + `app.py`** — FastAPI server + glassmorphism dashboard (AR/EN, RTL),
  live training studio (Chart.js) and workspace file monitor.
- **`deploy/`** — Dockerfile, Render and Hugging Face Spaces config, and a
  one-click local launcher with a public tunnel.

## Quick start (Windows)

```bat
launch_platform.bat
```

Or manually:

```bash
py -m pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu
py -m core.trainer          # ~10 s micro-training -> checkpoints/nexus_brain.pt
py app.py                   # http://localhost:8000
```

## Security

All API routes require the access token stored in `.nexus_token` (auto-generated
on first run, or set `NEXUS_ACCESS_TOKEN`). The links written to
`PERMANENT_LINK.txt` already include it. Set `NEXUS_SAFE_MODE=1` to disable the
Python and system-command tools; this is the default in the Docker image.

## Permanent cloud link

See [deploy/DEPLOY.md](deploy/DEPLOY.md) for Hugging Face Spaces (recommended)
and Render.
