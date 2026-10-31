"""Live data for the home dashboard tiles (weather, next prayer, dollar rate, code of the day), cached."""
import re
import time
from datetime import date, datetime
from zoneinfo import ZoneInfo

import httpx

from agent.code_kb import LANGS, TASKS, snippet
from agent.live_skills import _WMO, HEADERS
from agent.prayer import METHODS, PRAYERS

CACHE_SECONDS = 600
_cache: dict[tuple[str, str], tuple[float, dict]] = {}
_SHORT_TASKS = ["reverse_string", "sort_list", "function", "split_string", "random_number", "sum_max", "for_loop"]
_DAY_LANGS = ["python", "javascript", "go", "csharp", "java"]


def _weather(http: httpx.Client, place: dict, lang: str) -> dict:
    w = http.get("https://api.open-meteo.com/v1/forecast", params={
        "latitude": place["latitude"], "longitude": place["longitude"], "timezone": "auto", "forecast_days": 1,
        "current": "temperature_2m,weather_code", "daily": "temperature_2m_max,temperature_2m_min"}).json()
    code = w["current"]["weather_code"]
    desc = next(((ar if lang == "ar" else en) for codes, ar, en in _WMO if code in codes), "")
    return {"temp": round(w["current"]["temperature_2m"]), "desc": re.sub(r"\s*\S+$", "", desc) or desc,
            "high": round(w["daily"]["temperature_2m_max"][0]), "low": round(w["daily"]["temperature_2m_min"][0])}


def _next_prayer(http: httpx.Client, place: dict, lang: str) -> dict:
    data = http.get("https://api.aladhan.com/v1/timings", follow_redirects=True, params={
        "latitude": place["latitude"], "longitude": place["longitude"],
        "method": METHODS.get(place.get("country_code", ""), 3)}).json()["data"]
    timings, now = data["timings"], datetime.now(ZoneInfo(data["meta"]["timezone"]))
    minutes_now = now.hour * 60 + now.minute
    for en, ar in PRAYERS:
        if en == "Sunrise":
            continue
        h, m = int(timings[en][:2]), int(timings[en][3:5])
        if h * 60 + m > minutes_now:
            left = h * 60 + m - minutes_now
            break
    else:  # after Isha: tomorrow's Fajr
        en, ar = PRAYERS[0]
        h, m = int(timings[en][:2]), int(timings[en][3:5])
        left = h * 60 + m + 24 * 60 - minutes_now
    suffix = ("ص" if h < 12 else "م") if lang == "ar" else ("AM" if h < 12 else "PM")
    return {"name": ar if lang == "ar" else en, "time": f"{(h % 12) or 12}:{m:02d} {suffix}",
            "in_hours": left // 60, "in_minutes": left % 60}


def _code_of_day(lang: str) -> dict:
    day = date.today().toordinal()
    task, code_lang = _SHORT_TASKS[day % len(_SHORT_TASKS)], _DAY_LANGS[day % len(_DAY_LANGS)]
    title = TASKS[task][0 if lang == "ar" else 1]
    name = LANGS[code_lang][0]
    lines = [line for line in snippet(task, code_lang).strip().splitlines() if line.strip()][:5]
    question = f"{title} في {name}" if lang == "ar" else f"{title} in {name}"
    return {"title": title, "language": name, "code": "\n".join(lines), "question": question}


def home(city: str, lang: str) -> dict:
    """Everything the dashboard shows. Each part degrades to None on its own if a service is down."""
    key = (city, lang)
    if key in _cache and time.time() - _cache[key][0] < CACHE_SECONDS:
        return _cache[key][1]
    data: dict = {"city": city, "weather": None, "prayer": None, "usd_sar": None, "code": _code_of_day(lang)}
    try:
        with httpx.Client(timeout=12, headers=HEADERS) as http:
            places = http.get("https://geocoding-api.open-meteo.com/v1/search",
                              params={"name": city, "count": 1, "language": lang}).json().get("results")
            if places:
                data["city"] = places[0]["name"]
                for part, fetch in (("weather", _weather), ("prayer", _next_prayer)):
                    try:
                        data[part] = fetch(http, places[0], lang)
                    except (httpx.HTTPError, KeyError, ValueError):
                        pass
            try:
                data["usd_sar"] = round(http.get("https://open.er-api.com/v6/latest/USD").json()["rates"]["SAR"], 2)
            except (httpx.HTTPError, KeyError, ValueError):
                pass
    except httpx.HTTPError:
        pass
    _cache[key] = (time.time(), data)
    return data
