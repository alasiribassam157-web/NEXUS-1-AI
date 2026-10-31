"""Read uploaded files (PDF / Word / text) into plain text, entirely in memory.

Files are streamed in chunks with a hard size cap and never written to disk, so
people's documents are gone as soon as the request ends.
"""
import asyncio
import gc
import io
import re
import unicodedata
import zipfile

from fastapi import HTTPException, UploadFile

MAX_FILES = 5
MAX_BYTES = 5 * 1024 * 1024       # per file
MAX_PDF_PAGES = 15
CHUNK = 64 * 1024
KINDS = {".pdf": "pdf", ".docx": "docx", ".txt": "txt", ".md": "txt"}
ARABIC = re.compile(r"[؀-ۿ]")


async def read_upload(file: UploadFile) -> bytes:
    """Stream one upload in chunks and stop as soon as it passes the cap."""
    buf = bytearray()
    while chunk := await file.read(CHUNK):
        buf.extend(chunk)
        if len(buf) > MAX_BYTES:
            raise HTTPException(413, f"{file.filename}: larger than 5 MB")
    return bytes(buf)


def _kind(name: str) -> str:
    ext = "." + name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if ext not in KINDS:
        raise HTTPException(415, f"{name}: only PDF, Word (.docx) or text files")
    return KINDS[ext]


def _pdf_line(line: str) -> str:
    """PDFs store right-to-left lines in visual order with presentation-form glyphs:
    normalise the glyphs, then put the words back in reading order."""
    line = unicodedata.normalize("NFKC", line)
    words = line.split()
    if ARABIC.search(line) or (words and words[-1].endswith("+") and line.replace(" ", "").strip("+").isdigit()):
        words.reverse()
        words = [w[1:] + w[0] if len(w) > 1 and w[0] in "،.:؛" else w for w in words]
        words = ["+" + w[:-1] if len(w) > 1 and w.endswith("+") else w for w in words]
    return " ".join(words)


def _pdf_text(data: bytes) -> str:
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(data))
    pages = reader.pages[:MAX_PDF_PAGES]
    text = "\n".join((p.extract_text() or "") for p in pages)
    return "\n".join(_pdf_line(l) for l in text.split("\n"))


def _docx_text(data: bytes) -> str:
    """A .docx is a zip of XML: paragraphs are <w:p>, text runs are <w:t>."""
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        xml = z.read("word/document.xml").decode("utf-8", "ignore")
    xml = re.sub(r"</w:p>|<w:br/>|<w:tab/>", "\n", xml)
    text = "".join(run or nl for run, nl in re.findall(r"<w:t[^>]*>([^<]*)</w:t>|(\n)", xml))
    for ent, ch in (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'), ("&apos;", "'")):
        text = text.replace(ent, ch)
    return text


def _to_text(kind: str, data: bytes) -> str:
    if kind == "pdf":
        return _pdf_text(data)
    if kind == "docx":
        return _docx_text(data)
    return data.decode("utf-8", "ignore")


async def files_to_text(files: list[UploadFile]) -> str:
    """Pipeline: validate → stream → parse in a worker thread → free memory."""
    if not files:
        raise HTTPException(400, "No files")
    if len(files) > MAX_FILES:
        raise HTTPException(400, f"At most {MAX_FILES} files")
    parts = []
    for f in files:
        kind = _kind(f.filename or "")
        data = await read_upload(f)
        try:
            # parsing is CPU work: keep the event loop free for other visitors
            parts.append(await asyncio.to_thread(_to_text, kind, data))
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(422, f"{f.filename}: could not read this file")
        finally:
            del data
            await f.close()
    gc.collect()
    text = "\n\n".join(p for p in parts if p.strip())
    if len(text.strip()) < 20:
        raise HTTPException(422, "No readable text found (scanned images are not supported yet)")
    return text[:60_000]
