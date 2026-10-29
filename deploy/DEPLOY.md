# Permanent 24/7 link

The local tunnel (`launch_platform.bat`) only works while your laptop is on, and
its `trycloudflare.com` address changes on every launch. For a fixed `https://`
address that stays up with the laptop closed, deploy the GitHub repo to one of
these free hosts. Both build the same `Dockerfile`.

## Option A: Hugging Face Spaces (recommended: 16 GB RAM, free)

1. Create an account at https://huggingface.co and go to **New Space**.
2. Name it `NEXUS-1-AI`, choose **SDK: Docker** and **Blank** template.
3. In the Space **Settings → Variables and secrets**, add a secret
   `NEXUS_ACCESS_TOKEN` with any long random value.
4. Push the code to the Space:
   ```bash
   git remote add space https://huggingface.co/spaces/<your-user>/NEXUS-1-AI
   git push space main
   ```
   The YAML header in `README.md` already configures the Space (docker, port 7860).
   Alternatively, you can sync from GitHub with a GitHub Action.
5. Your permanent link: `https://<your-user>-nexus-1-ai.hf.space/?token=<secret>`

## Option B: Render (free, sleeps after 15 min idle, 512 MB RAM)

1. Sign in at https://render.com with GitHub.
2. **New → Blueprint** and pick the `NEXUS-1-AI` repo. `render.yaml` is detected.
3. After the deploy, open the service's **Environment** tab and copy the generated
   `NEXUS_ACCESS_TOKEN`.
4. Your permanent link: `https://nexus-1-ai.onrender.com/?token=<token>`
   Every `git push` to `main` redeploys automatically.

## Safe mode in the cloud

The Docker image sets `NEXUS_SAFE_MODE=1`, which disables the Python-executor and
system-command tools on a public server. File management (inside the container's
`workspace/`) and web research keep working. To enable everything, set the
variable to `0` in your host's settings, but only with a strong token.
