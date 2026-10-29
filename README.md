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

## 🔗 Live platform

**https://nexus-1-ai.onrender.com**: hosted 24/7 on Render and redeployed
on every deploy of `main`. The cloud copy runs in safe mode (no code or system
execution), so it opens without an access token. Local full-tools mode still requires one.

> If the link shows a loading screen, the free instance is waking from sleep
> (about one minute after 15 idle minutes).

## 👥 Two experiences

- **`/`**: the public chat, a minimal ChatGPT-style page.
- **`/dev`**: the developer dashboard (password = `NEXUS_ACCESS_TOKEN`). It shows brain size,
  layers, vocabulary, cumulative training steps, version history, usage statistics,
  and intent distribution. From it you can train small / medium / large brains and
  **teach** the brain by correcting misunderstood questions. Corrections are stored in
  `data/custom_examples.jsonl` and oversampled in the next training run.
  On the free cloud tier the disk resets on redeploy, so teach on your laptop's `/dev`
  and run `update.bat` to keep the corrections in git.

## 🛠 Development workflow

1. Edit the code (VS Code / Claude Code).
2. Double-click **`update.bat`**. It runs the smoke tests (`py -m tests.smoke_test`),
   asks for a short description, commits, and pushes to GitHub.
3. Render rebuilds and the live link serves the new version within a few minutes.

If tests fail, nothing is pushed, so the live link never breaks.

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
