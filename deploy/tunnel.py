"""Expose the local platform through a free public HTTPS tunnel and save the link.

Order: Cloudflare quick tunnel (auto-downloads cloudflared.exe) → localhost.run (ssh).
Note: quick-tunnel URLs change on every launch. For a truly permanent URL use the
cloud deployment described in deploy/DEPLOY.md.
"""
import os
import re
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIN = ROOT / "deploy" / "bin"
PORT = int(os.getenv("PORT", "8000"))
LOCAL = f"http://localhost:{PORT}"
CLOUDFLARED_URL = ("https://github.com/cloudflare/cloudflared/releases/latest/download/"
                   "cloudflared-windows-amd64.exe")


def wait_for_server(timeout: int = 90) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(f"{LOCAL}/api/health", timeout=2)
            return True
        except OSError:
            time.sleep(1)
    return False


def desktop_dir() -> Path:
    home = Path(os.environ.get("USERPROFILE", Path.home()))
    for candidate in (home / "Desktop", home / "OneDrive" / "Desktop"):
        if candidate.is_dir():
            return candidate
    return ROOT


def save_links(public_url: str | None) -> None:
    token = (ROOT / ".nexus_token").read_text(encoding="utf-8").strip()
    lines = ["NEXUS-1 Platform links", "=" * 40,
             f"Local (this PC):   {LOCAL}/?token={token}"]
    if public_url:
        lines.append(f"Public (anywhere): {public_url}/?token={token}")
        lines.append("  (public tunnel link changes each launch; keep this window open)")
    lines += ["", f"Access token: {token}", f"Updated: {time.strftime('%Y-%m-%d %H:%M:%S')}"]
    text = "\n".join(lines) + "\n"
    for folder in {ROOT, desktop_dir()}:
        (folder / "PERMANENT_LINK.txt").write_text(text, encoding="utf-8")
    print("\n" + text)


def _scan(proc: subprocess.Popen, pattern: str, timeout: int = 40) -> str | None:
    regex, deadline = re.compile(pattern), time.time() + timeout
    while time.time() < deadline and proc.poll() is None:
        line = proc.stdout.readline()
        match = regex.search(line or "")
        if match:
            return match.group(0)
    return None


def cloudflare() -> tuple[subprocess.Popen, str] | None:
    exe = BIN / "cloudflared.exe"
    if not exe.exists():
        print("Downloading cloudflared (one-time)...")
        BIN.mkdir(parents=True, exist_ok=True)
        try:
            urllib.request.urlretrieve(CLOUDFLARED_URL, exe)
        except OSError as exc:
            print(f"cloudflared download failed: {exc}")
            return None
    proc = subprocess.Popen([str(exe), "tunnel", "--no-autoupdate", "--url", LOCAL],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    url = _scan(proc, r"https://[a-z0-9-]+\.trycloudflare\.com")
    return (proc, url) if url else (proc.kill(), None)[1]


def localhost_run() -> tuple[subprocess.Popen, str] | None:
    try:
        proc = subprocess.Popen(["ssh", "-o", "StrictHostKeyChecking=no", "-o", "ServerAliveInterval=30",
                                 "-R", f"80:localhost:{PORT}", "nokey@localhost.run"],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                stdin=subprocess.DEVNULL)
    except FileNotFoundError:
        return None
    url = _scan(proc, r"https://[a-z0-9-]+\.(?:lhr\.life|localhost\.run)")
    return (proc, url) if url else (proc.kill(), None)[1]


def main() -> int:
    print(f"Waiting for NEXUS-1 on {LOCAL} ...")
    if not wait_for_server():
        print("Server did not start. Check the 'NEXUS-1 Server' window for errors.")
        return 1
    tunnel = cloudflare() or localhost_run()
    save_links(tunnel[1] if tunnel else None)
    token = (ROOT / ".nexus_token").read_text(encoding="utf-8").strip()
    webbrowser.open(f"{LOCAL}/?token={token}")
    if not tunnel:
        print("No public tunnel available - local link only.")
        return 0
    print("Tunnel active. Press Ctrl+C to stop.")
    try:
        tunnel[0].wait()
    except KeyboardInterrupt:
        tunnel[0].terminate()
    return 0


if __name__ == "__main__":
    sys.exit(main())
