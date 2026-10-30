"""Unit conversion (length, mass, volume, speed, data, area, temperature) in Arabic and English."""
import re

from agent.tools import ToolResult

# unit -> (category, factor to the category's base unit, Arabic name, English name, aliases)
UNITS = {
    "km": ("length", 1000, "كيلومتر", "kilometers", ["km", "kilometer", "kilometers", "kilometre", "كيلومتر", "كيلو متر", "كيلومترات"]),
    "m": ("length", 1, "متر", "meters", ["m", "meter", "meters", "metre", "متر", "امتار", "أمتار"]),
    "cm": ("length", 0.01, "سنتيمتر", "centimeters", ["cm", "centimeter", "centimeters", "سم", "سنتيمتر", "سنتي"]),
    "mm": ("length", 0.001, "مليمتر", "millimeters", ["mm", "millimeter", "millimeters", "ملم", "مليمتر"]),
    "mi": ("length", 1609.344, "ميل", "miles", ["mile", "miles", "mi", "ميل", "اميال", "أميال"]),
    "yd": ("length", 0.9144, "ياردة", "yards", ["yard", "yards", "yd", "ياردة", "يارده", "يارد"]),
    "ft": ("length", 0.3048, "قدم", "feet", ["foot", "feet", "ft", "قدم", "اقدام", "أقدام"]),
    "in": ("length", 0.0254, "بوصة", "inches", ["inch", "inches", "انش", "إنش", "بوصة", "بوصه"]),
    "kg": ("mass", 1, "كيلوجرام", "kilograms", ["kg", "kilogram", "kilograms", "kilo", "kilos", "كيلوجرام", "كيلو جرام",
                                               "كيلوغرام", "كيلو غرام", "كجم", "كيلو"]),
    "g": ("mass", 0.001, "جرام", "grams", ["g", "gram", "grams", "جرام", "غرام", "جم"]),
    "mg": ("mass", 1e-6, "مليجرام", "milligrams", ["mg", "milligram", "milligrams", "ملغ", "مليجرام"]),
    "lb": ("mass", 0.45359237, "رطل", "pounds", ["lb", "lbs", "pound", "pounds", "رطل", "باوند", "ارطال"]),
    "oz": ("mass", 0.028349523, "أونصة", "ounces", ["oz", "ounce", "ounces", "اونصة", "أونصة", "اونصه"]),
    "t": ("mass", 1000, "طن", "tonnes", ["ton", "tons", "tonne", "tonnes", "طن", "اطنان"]),
    "l": ("volume", 1, "لتر", "liters", ["l", "liter", "liters", "litre", "litres", "لتر", "لترات"]),
    "ml": ("volume", 0.001, "مليلتر", "milliliters", ["ml", "milliliter", "milliliters", "مل", "ملليلتر", "مليلتر"]),
    "gal": ("volume", 3.785411784, "جالون", "gallons", ["gallon", "gallons", "gal", "جالون", "غالون"]),
    "cup": ("volume", 0.2365882365, "كوب", "cups", ["cup", "cups", "كوب", "اكواب"]),
    "kmh": ("speed", 1 / 3.6, "كم/س", "km/h", ["km/h", "kph", "kmh", "كم/س", "كيلومتر في الساعة"]),
    "mph": ("speed", 0.44704, "ميل/س", "mph", ["mph", "ميل في الساعة"]),
    "ms": ("speed", 1, "م/ث", "m/s", ["m/s", "متر في الثانية"]),
    "knot": ("speed", 0.514444, "عقدة", "knots", ["knot", "knots", "عقدة", "عقده"]),
    "kb": ("data", 1024, "كيلوبايت", "KB", ["kb", "kilobyte", "kilobytes", "كيلوبايت"]),
    "mb": ("data", 1024 ** 2, "ميجابايت", "MB", ["mb", "megabyte", "megabytes", "ميجابايت", "ميغابايت", "ميجا"]),
    "gb": ("data", 1024 ** 3, "جيجابايت", "GB", ["gb", "gigabyte", "gigabytes", "جيجابايت", "غيغابايت", "جيجا", "قيقا"]),
    "tb": ("data", 1024 ** 4, "تيرابايت", "TB", ["tb", "terabyte", "terabytes", "تيرابايت", "تيرا"]),
    "m2": ("area", 1, "متر مربع", "square meters", ["m2", "sqm", "square meter", "square meters", "متر مربع"]),
    "km2": ("area", 1e6, "كيلومتر مربع", "square kilometers", ["km2", "square kilometer", "square kilometers", "كيلومتر مربع"]),
    "ha": ("area", 1e4, "هكتار", "hectares", ["hectare", "hectares", "ha", "هكتار"]),
    "acre": ("area", 4046.8564224, "فدان إنجليزي (acre)", "acres", ["acre", "acres", "ايكر"]),
    "c": ("temp", None, "درجة مئوية", "°C", ["celsius", "°c", "c", "مئوية", "مئويه", "سيلزيوس", "درجة مئوية"]),
    "f": ("temp", None, "فهرنهايت", "°F", ["fahrenheit", "°f", "f", "فهرنهايت"]),
    "k": ("temp", None, "كلفن", "K", ["kelvin", "كلفن"]),
}
_ALIASES = sorted(((a, u) for u, spec in UNITS.items() for a in spec[4]), key=lambda x: -len(x[0]))
_NUM = re.compile(r"-?\d+(?:[.,]\d+)?")


def _find_units(text: str) -> list[tuple[int, str]]:
    low, spans = text.lower(), []
    for alias, unit in _ALIASES:
        prefix = r"(?:ال|بال|لل)?" if re.match(r"[؀-ۿ]", alias) else ""  # الميل، بالكيلو
        for m in re.finditer(rf"(?<![\w]){prefix}{re.escape(alias)}(?![\w/])", low):
            if not any(s <= m.start() < e for s, e, _ in spans):
                spans.append((m.start(), m.end(), unit))
    # "كم" means km only right after a number ("10 كم"); otherwise it is the word "how many".
    for m in re.finditer(r"\d\s*(كم)(?![\w/])", low):
        spans.append((m.start(1), m.end(1), "km"))
    return sorted((s, u) for s, _, u in spans)


def is_conversion(question: str) -> bool:
    """A number plus two different units of the same kind, e.g. «1 inch to cm»."""
    text = question.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789"))
    found = list(dict.fromkeys(u for _, u in _find_units(text)))
    return bool(_NUM.search(text)) and len(found) >= 2 and UNITS[found[0]][0] == UNITS[found[1]][0]


def _to_temp(value: float, src: str, dst: str) -> float:
    c = value if src == "c" else (value - 32) * 5 / 9 if src == "f" else value - 273.15
    return c if dst == "c" else c * 9 / 5 + 32 if dst == "f" else c + 273.15


def convert(question: str) -> ToolResult:
    lang = "ar" if re.search(r"[؀-ۿ]", question) else "en"
    text = question.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789"))
    num = _NUM.search(text)
    value = float(num.group().replace(",", ".")) if num else 1.0
    found = _find_units(text)
    units = list(dict.fromkeys(u for _, u in found))
    if num and found:
        # The source unit is the first one written after the number ("10 km to miles", "كم ميل في 10 كم").
        after = [u for pos, u in found if pos >= num.end()]
        if after:
            units = [after[0]] + [u for u in units if u != after[0]]
    if len(units) < 2:
        return ToolResult(False, "اكتب الوحدتين، مثلاً: حول 10 كيلومتر الى ميل" if lang == "ar"
                          else "Name both units, e.g. convert 10 km to miles")
    src, dst = units[0], units[1]
    if UNITS[src][0] != UNITS[dst][0]:
        return ToolResult(False, "ما أقدر أحول بين نوعين مختلفين من الوحدات." if lang == "ar"
                          else "Those units measure different things.")
    if UNITS[src][0] == "temp":
        result = _to_temp(value, src, dst)
    else:
        result = value * UNITS[src][1] / UNITS[dst][1]
    shown = f"{result:,.4f}".rstrip("0").rstrip(".")
    i = 2 if lang == "ar" else 3
    return ToolResult(True, f"📏 **{value:g} {UNITS[src][i]} = {shown} {UNITS[dst][i]}**")
