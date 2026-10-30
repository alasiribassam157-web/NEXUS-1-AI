"""Direct factual answers from Wikidata (capital, population, founding date, currency, language)."""
import re

import httpx

API = "https://www.wikidata.org/w/api.php"
HEADERS = {"User-Agent": "NEXUS-1-Agent/1.0 (https://github.com/topics/nexus-1-ai) python-httpx"}
AR_MONTHS = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر",
             "أكتوبر", "نوفمبر", "ديسمبر"]
EN_MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
             "October", "November", "December"]

# (property, regex capturing the entity, Arabic template, English template)
RELATIONS = [
    ("P36", r"عاصمة\s+(.+)|capital(?: city)? of\s+(.+)", "عاصمة {e} هي **{v}**.", "The capital of {e} is **{v}**."),
    ("P1082", r"(?:عدد\s+)?سكان\s+(.+)|population of\s+(.+)|how many people live in\s+(.+)",
     "عدد سكان {e} حوالي **{v}** نسمة{d}.", "The population of {e} is about **{v}**{d}."),
    ("P571", r"(?:تأسست|تاسست|تأسس|تاسس|نشأت|قامت)\s+(.+)|when (?:was|were) (.+?) (?:founded|established|created)",
     "تأسست {e} في **{v}**.", "{e} was founded on **{v}**."),
    ("P38", r"عملة\s+(.+)|currency (?:of|in)\s+(.+)", "عملة {e} هي **{v}**.", "The currency of {e} is **{v}**."),
    ("P37", r"اللغة الرسمية (?:في|ل|لـ)\s*(.+)|official language (?:of|in)\s+(.+)",
     "اللغة الرسمية في {e} هي **{v}**.", "The official language of {e} is **{v}**."),
]


def _clean_entity(text: str) -> str:
    text = re.sub(r"[؟?!.،,]+$", "", text.strip())
    return re.sub(r"^(the|دولة|مدينة)\s+", "", text, flags=re.IGNORECASE).strip()


def _label(http: httpx.Client, qid: str, lang: str) -> str:
    data = http.get(API, params={"action": "wbgetentities", "ids": qid, "props": "labels",
                                 "languages": f"{lang}|en", "format": "json"}).json()
    labels = data["entities"][qid]["labels"]
    return (labels.get(lang) or labels.get("en") or {"value": qid})["value"]


def _best_claim(claims: list) -> dict | None:
    preferred = [c for c in claims if c.get("rank") == "preferred"]
    pool = preferred or [c for c in claims if c.get("rank") != "deprecated"]
    return pool[-1] if pool else None


def _format(value: dict, claim: dict, http: httpx.Client, lang: str) -> tuple[str, str]:
    kind = value["type"]
    if kind == "wikibase-entityid":
        return _label(http, value["value"]["id"], lang), ""
    if kind == "quantity":
        amount = f"{int(float(value['value']['amount'])):,}"
        when = claim.get("qualifiers", {}).get("P585", [{}])[0].get("datavalue", {}).get("value", {})
        year = when.get("time", "")[1:5]
        return amount, (f" ({year})" if year else "")
    if kind == "time":
        y, m, d = re.match(r"[+-](\d+)-(\d+)-(\d+)", value["value"]["time"]).groups()
        y, m, d = int(y), int(m), int(d)
        months = AR_MONTHS if lang == "ar" else EN_MONTHS
        if m and d:
            return (f"{d} {months[m - 1]} {y}" if lang == "ar" else f"{months[m - 1]} {d}, {y}"), ""
        return str(y), ""
    return str(value["value"]), ""


def answer_fact(question: str, lang: str) -> tuple[str, str] | None:
    """Return (answer markdown, source url) or None if the question is not a known relation."""
    for prop, pattern, tpl_ar, tpl_en in RELATIONS:
        m = re.search(pattern, question, re.IGNORECASE)
        if not m:
            continue
        entity = _clean_entity(next(g for g in m.groups() if g))
        try:
            with httpx.Client(timeout=8, headers=HEADERS) as http:
                hits = http.get(API, params={"action": "wbsearchentities", "search": entity, "language": lang,
                                             "uselang": lang, "type": "item", "limit": 3, "format": "json"}).json()
                for hit in hits.get("search", []):
                    qid = hit["id"]
                    claims = http.get(API, params={"action": "wbgetentities", "ids": qid, "props": "claims",
                                                   "format": "json"}).json()["entities"][qid]["claims"]
                    claim = _best_claim(claims.get(prop, []))
                    if not claim or "datavalue" not in claim["mainsnak"]:
                        continue
                    value, detail = _format(claim["mainsnak"]["datavalue"], claim, http, lang)
                    name = _label(http, qid, lang)
                    tpl = tpl_ar if lang == "ar" else tpl_en
                    return tpl.format(e=name, v=value, d=detail), f"https://www.wikidata.org/wiki/{qid}"
        except (httpx.HTTPError, KeyError, ValueError, StopIteration, AttributeError):
            return None
        return None
    return None
