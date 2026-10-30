"""Programming knowledge base: verified snippets for common tasks in six languages."""
import re
from importlib import import_module

# task key -> (Arabic title, English title); order defines the coder brain's labels
TASKS = {
    "hello_world": ("طباعة Hello World", "Print Hello World"),
    "variables": ("تعريف المتغيرات", "Declare variables"),
    "if_else": ("الشروط if / else", "If / else conditions"),
    "for_loop": ("حلقة for", "For loop"),
    "while_loop": ("حلقة while", "While loop"),
    "function": ("تعريف دالة", "Define a function"),
    "list": ("القوائم والمصفوفات", "Lists / arrays"),
    "dict": ("القواميس (مفتاح وقيمة)", "Dictionaries / maps"),
    "class": ("الكلاسات والكائنات", "Classes and objects"),
    "read_file": ("قراءة ملف", "Read a file"),
    "write_file": ("الكتابة في ملف", "Write to a file"),
    "reverse_string": ("عكس نص", "Reverse a string"),
    "sort_list": ("ترتيب قائمة", "Sort a list"),
    "try_catch": ("معالجة الأخطاء", "Error handling"),
    "http_request": ("طلب HTTP / API", "HTTP request"),
    "json_parse": ("التعامل مع JSON", "Parse JSON"),
    "random_number": ("رقم عشوائي", "Random number"),
    "current_date": ("التاريخ والوقت الحالي", "Current date and time"),
    "split_string": ("تقسيم ودمج النصوص", "Split and join strings"),
    "sum_max": ("المجموع والأكبر في قائمة", "Sum and max of a list"),
}

# language key -> (display name, fence tag, detection regex)
LANGS = {
    "python": ("Python", "python", r"python|بايثون|بايتون|\bpy\b"),
    "javascript": ("JavaScript", "javascript", r"javascript|جافا ?سكربت|جافا ?سكريبت|\bjs\b|node"),
    "java": ("Java", "java", r"\bjava\b(?!\s*script)|جافا(?!\s*سكر)"),
    "cpp": ("C++", "cpp", r"c\+\+|\bcpp\b|سي ?بلس"),
    "csharp": ("C#", "csharp", r"c#|c sharp|csharp|سي ?شارب"),
    "go": ("Go", "go", r"\bgolang\b|\bgo\b|لغة جو|بلغة جو|\bجو\b"),
}


def detect_language(text: str) -> str | None:
    low = text.lower()
    for key, (_, _, pattern) in LANGS.items():
        if re.search(pattern, low):
            return key
    return None


def snippet(task: str, lang: str) -> str:
    module = import_module(f"agent.code_kb.{lang}_kb")
    return module.SNIPPETS[task]


def render(task: str, lang: str, ui_lang: str, confidence: float) -> str:
    title_ar, title_en = TASKS[task]
    name, fence, _ = LANGS[lang]
    others = ", ".join(n for k, (n, _, _) in LANGS.items() if k != lang)
    if ui_lang == "ar":
        head = f"**{title_ar}** بلغة **{name}**:"
        tail = f"\n\n💡 متوفر أيضاً بـ: {others}. اكتب مثلاً «{title_ar} في Java»."
    else:
        head = f"**{title_en}** in **{name}**:"
        tail = f"\n\n💡 Also available in: {others}. Try «{title_en.lower()} in Java»."
    return f"{head}\n\n```{fence}\n{snippet(task, lang).strip()}\n```{tail}"
