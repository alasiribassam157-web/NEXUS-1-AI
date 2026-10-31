"""Rules the critic uses to double-check the brain: keyword lists and unmistakable patterns."""
import re

CONFIDENCE_FLOOR = 0.60

# Independent keyword router used to cross-check low-confidence neural predictions.
_KEYWORDS = {
    "python": ["calculate", "compute", "احسب", "```", "كم يساوي"],
    "file": ["file", "folder", "directory", ".txt", ".md", ".csv", ".json", "ملف", "مجلد", "الملفات"],
    "web": ["search", "who is", "tell me about", "news", "ابحث", "معلومات عن", "من هو", "اخبار"],
    "system": ["command", "terminal", "ipconfig", "tasklist", "systeminfo", "الامر", "الأمر", "النظام"],
    "chat": ["hello", "hi", "thanks", "who are you", "مرحبا", "شكرا", "من انت", "كيف حالك"],
    "code": ["code", "كود", "function", "دالة", "loop", "لوب", "حلقة", "class", "كلاس", "array", "مصفوفة", "string",
             "برمجة", "sort", "رتب", "reverse", "اعكس", "json", "http", "api", "dictionary", "قاموس", "variable",
             "متغير", "exception", "try catch", "hello world", "list", "قائمة", "فنكشن", "random", "عشوائي"],
    "weather": ["weather", "temperature", "الطقس", "طقس", "الجو", "درجة الحرارة", "مطر", "rain"],
    "currency": ["exchange rate", "سعر صرف", "سعر الدولار", "دولار", "ريال", "يورو", "currency", "usd", "eur"],
    "datetime": ["what time", "الساعة", "الساعه", "التاريخ اليوم", "هجري", "الهجري", "today's date", "hijri"],
    "prayer": ["الصلاة", "صلاة", "اذان", "أذان", "prayer", "fajr", "maghrib", "الفجر", "المغرب", "العشاء"],
    "translate": ["ترجم", "translate", "بالانجليزي", "بالإنجليزي", "بالعربي", "in arabic", "in english", "معنى"],
    "units": ["convert", "حول", "كيلومتر", "ميل", "رطل", "فهرنهايت", "mile", "km", "kg", "feet", "pounds"],
}


def keyword_intent(msg: str) -> str | None:
    low = msg.lower()
    scores = {k: sum(w in low for w in words) for k, words in _KEYWORDS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else None


_MATH = re.compile(r"```|\d\s*([+\-*/^%×÷٪]|\*\*)\s*\d|\d\s*[%٪]|(\d.*(ضرب|زائد|ناقص|قسمة|على|times|plus|minus|divided))|"
                   r"(calculate|compute|solve|احسب|حل|كم يساوي|factorial|مضروب|sqrt|جذر|square root|fibonacci|"
                   r"فيبوناتشي|prime|الاولية|average|متوسط|sum of|مجموع)", re.IGNORECASE)
_CODE_TASK = re.compile(r"\b(?:for|while) loop\b|\btry catch\b|\bhello world\b|حلقة (?:for|while)|لوب", re.IGNORECASE)
# Unmistakable arithmetic: "15*7", "3 ^ 4", "25% of 80".
_STRONG_MATH = re.compile(r"\d\s*([+*/^×÷]|\*\*)\s*\d|\d\s*[%٪]\s*(of|من)\s*\d", re.IGNORECASE)
