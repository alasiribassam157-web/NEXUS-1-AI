"""Prayer times for any city (Open-Meteo geocoding + api.aladhan.com), with the next prayer highlighted."""
import re
from datetime import datetime
from zoneinfo import ZoneInfo

import httpx

from agent.live_skills import _CITY_PATTERNS, _NOISE, HEADERS, AR_DAYS, AR_MONTHS
from agent.tools import ToolResult

# country code -> aladhan calculation method (default 3 = Muslim World League)
METHODS = {"SA": 4, "EG": 5, "AE": 16, "KW": 9, "QA": 10, "TR": 13, "JO": 3, "PK": 1, "US": 2, "CA": 2}
PRAYERS = [("Fajr", "الفجر"), ("Sunrise", "الشروق"), ("Dhuhr", "الظهر"), ("Asr", "العصر"),
           ("Maghrib", "المغرب"), ("Isha", "العشاء")]
_ASKED = {"فجر": "Fajr", "شروق": "Sunrise", "ظهر": "Dhuhr", "عصر": "Asr", "مغرب": "Maghrib", "عشاء": "Isha",
          "fajr": "Fajr", "sunrise": "Sunrise", "dhuhr": "Dhuhr", "zuhr": "Dhuhr", "asr": "Asr",
          "maghrib": "Maghrib", "isha": "Isha"}
_STRIP = re.compile(r"(?:مواقيت|موعد|وقت|اوقات|أوقات|اذان|أذان|الصلاة|الصلاه|صلاة|صلاه|prayer|prayers|times?|"
                    r"الفجر|الشروق|الظهر|العصر|المغرب|العشاء|fajr|dhuhr|asr|maghrib|isha|متى|كم|when is|what)\s*",
                    re.IGNORECASE)


def _city(question: str, lang: str) -> str:
    text = " ".join(_NOISE.sub(" ", question).split())
    match = next((m for p in _CITY_PATTERNS if (m := p.search(text))), None)
    city = match.group(1) if match else _STRIP.sub("", text)
    return city.strip() or ("مكة" if lang == "ar" else "Mecca")


def _12h(hhmm: str, lang: str) -> str:
    h, m = (int(x) for x in hhmm[:5].split(":"))
    suffix = ("ص" if h < 12 else "م") if lang == "ar" else ("AM" if h < 12 else "PM")
    return f"{(h % 12) or 12}:{m:02d} {suffix}"


def prayer_times(question: str) -> ToolResult:
    lang = "ar" if re.search(r"[؀-ۿ]", question) else "en"
    city = _city(question, lang)
    asked = next((v for k, v in _ASKED.items() if k in question.lower()), None)
    try:
        with httpx.Client(timeout=10, headers=HEADERS, follow_redirects=True) as http:  # aladhan redirects to a dated URL
            places = http.get("https://geocoding-api.open-meteo.com/v1/search",
                              params={"name": city, "count": 1, "language": lang}).json().get("results")
            if not places:
                return ToolResult(False, f"ما لقيت مدينة باسم «{city}»." if lang == "ar" else f"City not found: {city}")
            p = places[0]
            data = http.get("https://api.aladhan.com/v1/timings", params={
                "latitude": p["latitude"], "longitude": p["longitude"],
                "method": METHODS.get(p.get("country_code", ""), 3)}).json()["data"]
    except (httpx.HTTPError, ValueError, KeyError) as exc:
        return ToolResult(False, f"Prayer-times service error: {exc}")
    timings, tz = data["timings"], ZoneInfo(data["meta"]["timezone"])
    now = datetime.now(tz)
    minutes_now = now.hour * 60 + now.minute
    upcoming = next(((en, ar) for en, ar in PRAYERS if en != "Sunrise" and
                     int(timings[en][:2]) * 60 + int(timings[en][3:5]) > minutes_now), PRAYERS[0])
    rows = []
    for en, ar in PRAYERS:
        name = ar if lang == "ar" else en
        line = f"{name}  **{_12h(timings[en], lang)}**"
        if en == asked or (not asked and en == upcoming[0]):
            line += "  ← " + (("المطلوبة" if lang == "ar" else "asked") if asked else ("القادمة" if lang == "ar" else "next"))
        rows.append(line)
    if lang == "ar":
        head = f"🕌 **مواقيت الصلاة في {p['name']}** · {AR_DAYS[now.weekday()]} {now.day} {AR_MONTHS[now.month - 1]}"
    else:
        head = f"🕌 **Prayer times in {p['name']}** · {now:%A, %B} {now.day}"
    return ToolResult(True, head + "\n" + "\n".join(rows) + "\n\n🔗 https://aladhan.com", entity=p["name"])
