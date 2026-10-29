# NEXUS-1 — works on Hugging Face Spaces (port 7860) and Render ($PORT)
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=7860 \
    NEXUS_SAFE_MODE=1

# Hugging Face Spaces runs containers as uid 1000
RUN useradd -m -u 1000 nexus && mkdir -p /app && chown nexus:nexus /app
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
 && pip install --no-cache-dir -r requirements.txt

COPY --chown=nexus:nexus . .
USER nexus

# Bake the trained brain into the image (~10 s micro-training)
RUN python -m core.trainer

EXPOSE 7860
CMD ["python", "app.py"]
