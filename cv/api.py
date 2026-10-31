"""CV builder endpoints.

POST /api/cv/extract  (multipart files)  → editable fields read from the documents
POST /api/cv/render   (JSON fields)      → finished CV page (HTML, print to PDF)
"""
import asyncio

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from cv.extract import files_to_text
from cv.parse import parse
from cv.render import auto_summary, render

LIST_KEYS = ["summary", "experience", "education", "skills", "certificates", "languages",
             "projects", "links"]
TEXT_KEYS = ["name", "title", "email", "phone"]


class CVIn(BaseModel):
    fields: dict
    lang: str = "ar"


def _clean(raw: dict) -> dict:
    """Keep only known keys, as short strings / short lists: the input is untrusted."""
    out = {k: str(raw.get(k) or "")[:120] for k in TEXT_KEYS}
    for k in LIST_KEYS:
        items = raw.get(k) or []
        if isinstance(items, str):
            items = items.split("\n")
        out[k] = [str(i).strip()[:300] for i in items if str(i).strip()][:30]
    return out


def build_router() -> APIRouter:
    router = APIRouter(prefix="/api/cv")

    @router.post("/extract")
    async def extract(files: list[UploadFile] = File(...), lang: str = Form("ar")):
        text = await files_to_text(files)
        fields = await asyncio.to_thread(parse, text)
        if not fields["summary"]:
            fields["summary"] = [auto_summary(fields, "en" if lang == "en" else "ar")]
        return {"fields": fields, "chars": len(text)}

    @router.post("/render", response_class=HTMLResponse)
    async def make(body: CVIn):
        return render(_clean(body.fields), body.lang)

    return router
