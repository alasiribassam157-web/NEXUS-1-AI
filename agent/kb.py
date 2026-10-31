"""Local knowledge library (AI research, markets, Python/Java, math): BM25 search over full articles.

Answers come from data/kb/kb.jsonl.gz before going online, and can reach any paragraph of an
article, not only its introduction.  Built lazily on first use (~2 s, a few MB of RAM).
"""
import gzip
import json
import math
import re
import threading
from collections import Counter, defaultdict
from pathlib import Path

KB_FILE = Path(__file__).resolve().parent.parent / "data" / "kb" / "kb.jsonl.gz"
STOP = set("""ما هو هي هل في من الى إلى على عن او أو ان أن كان كيف لماذا ليش وش ايش شو متى اين أين الذي التي
ذلك هذا هذه بين مع كل اي أي لي لك عند ثم قد لا ال اشرح عرف وضح يعني الفرق معنى تعريف اعطني ابي ابغى
the a an of in on to for is are was were what who how why when where which does do did and or with by
as at from that this it its be explain define difference between meaning tell me about vs""".split())
_lock = threading.Lock()
_index: dict | None = None


def norm_word(w: str) -> str:
    w = re.sub(r"[ً-ْـ]", "", w.lower())
    w = w.translate(str.maketrans("أإآىة", "ااايه"))
    if re.match(r"[؀-ۿ]", w):
        for p in ("وال", "بال", "كال", "فال", "لل", "ال"):
            if w.startswith(p) and len(w) - len(p) >= 3:
                w = w[len(p):]
                break
        if w[:1] in "وب" and len(w) > 4:
            w = w[1:]
    elif len(w) > 4 and w.endswith("s") and not w.endswith("ss"):
        w = w[:-1]
    return w


# what people say -> how Wikipedia titles it («التعلم الآلي» → «تعلم الآلة», «العصبية» → «العصبونية»)
SYNONYMS = {"الي": "اله", "عصبيه": "عصبونيه"}


def terms(text: str) -> list[str]:
    words = (norm_word(w) for w in re.findall(r"[\w+#]+", text))
    return [SYNONYMS.get(t, t) for t in words if t and t not in STOP and len(t) > 1]


def _build() -> dict:
    arts, paras = [], []
    try:  # a missing or half-written library must never break answering
        with gzip.open(KB_FILE, "rt", encoding="utf-8") as f:
            for line in f:
                a = json.loads(line)
                a["key"] = " ".join(terms(re.sub(r"\(.*?\)", "", a["title"])))
                arts.append(a)
                for heading, ps in a["sections"]:
                    for p in ps:
                        paras.append((len(arts) - 1, heading, p, Counter(terms(heading + " " + p))))
    except (OSError, EOFError, ValueError, KeyError):
        pass
    df = Counter(t for *_, tf in paras for t in tf)
    postings = defaultdict(list)
    for i, (*_, tf) in enumerate(paras):
        for t in tf:
            postings[t].append(i)
    avg = sum(sum(tf.values()) for *_, tf in paras) / max(len(paras), 1)
    return {"arts": arts, "paras": paras, "df": df, "post": postings, "avg": avg, "n": len(paras)}


def _get() -> dict:
    global _index
    with _lock:
        if _index is None:
            _index = _build()
    return _index


def _sentences(text: str, n: int) -> str:
    parts = re.split(r"(?<=[.!؟?])\s+", text)
    return " ".join(parts[:n])


def _bm25(ix: dict, q: list[str], lang: str) -> list[tuple[float, int]]:
    scores = defaultdict(float)
    for t in set(q):
        idf = math.log(1 + (ix["n"] - ix["df"][t] + 0.5) / (ix["df"][t] + 0.5))
        for i in ix["post"].get(t, ()):
            tf = ix["paras"][i][3]
            if ix["arts"][ix["paras"][i][0]]["lang"] != lang:
                continue
            length = sum(tf.values())
            scores[i] += idf * tf[t] * 2.2 / (tf[t] + 1.2 * (0.25 + 0.75 * length / ix["avg"]))
    return sorted(((s, i) for i, s in scores.items()), reverse=True)


def lookup(question: str, topic: str, lang: str, sentences: int = 3) -> tuple[str, str, str] | None:
    """(title, answer, url) from the library, or None to let the caller go online."""
    ix = _get()
    if not ix["n"]:
        return None
    q = set(terms(question)) | set(terms(topic))
    # 1) which article is this about?  Its whole topic must be named in the question; the one whose
    #    full title covers most of the question wins («transformer in deep learning» → Transformer (…)).
    best, best_score = None, 0
    for a in ix["arts"]:
        key = set(a["key"].split())
        if a["lang"] != lang or not key or not key <= q:
            continue
        score = len(set(terms(a["title"])) & q) + 0.5 * (len(key) / len(q))
        if score > best_score:
            best, best_score = a, score
    if not best:
        return None   # not in the library: go online rather than guess
    extra = q - set(terms(best["title"]))
    if extra:  # 2) a specific question inside the topic: the paragraph that covers the extra words
        own = [(s, i) for s, i in _bm25(ix, list(q), lang) if ix["arts"][ix["paras"][i][0]] is best]
        for _, i in own[:1]:
            _, heading, text, tf = ix["paras"][i]
            if sum(t in tf for t in extra) / len(extra) >= 0.5:
                title = f"{best['title']} · {heading}" if heading else best["title"]
                return title, _sentences(text, max(sentences, 3)), best["url"]
    intro = " ".join(best["sections"][0][1][:3]) if best["sections"] else ""
    if sentences > 3:
        intro = " ".join(p for _, ps in best["sections"][:3] for p in ps)
    return best["title"], _sentences(intro, sentences), best["url"]
