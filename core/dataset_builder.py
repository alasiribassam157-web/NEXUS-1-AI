"""Synthetic bilingual training data generator for intent routing."""
import random

INTENTS = ["chat", "python", "file", "web", "system"]

SLOTS = {
    "expr": ["2 + 2", "15 * 7", "sqrt(144)", "2 ** 10", "100 / 3", "sum of 1 to 100",
             "factorial of 10", "average of 4, 8, 15", "fibonacci 20", "prime numbers under 50"],
    "fname": ["notes.txt", "report.md", "data.csv", "todo.txt", "script.py", "summary.json"],
    "folder": ["projects", "reports", "images", "backup", "docs", "data"],
    "topic": ["artificial intelligence", "python language", "quantum computing", "Egypt",
              "the moon", "climate change", "machine learning", "Albert Einstein",
              "الذكاء الاصطناعي", "مصر", "الفضاء", "تاريخ الحاسوب", "الطاقة الشمسية"],
    "cmd": ["dir", "ipconfig", "whoami", "systeminfo", "tasklist", "echo hello",
            "ping google.com", "hostname", "date /t", "ver"],
}

TEMPLATES = {
    "chat": [
        "hello", "hi there", "hey nexus", "good morning", "how are you", "who are you",
        "what can you do", "thanks", "thank you so much", "help", "tell me about yourself",
        "مرحبا", "اهلا", "السلام عليكم", "كيف حالك", "من انت", "ماذا تستطيع ان تفعل",
        "شكرا", "شكرا جزيلا", "ساعدني", "صباح الخير", "عرفني بنفسك",
    ],
    "python": [
        "calculate {expr}", "compute {expr}", "what is {expr}", "solve {expr}",
        "run python code to find {expr}", "write a python script for {expr}",
        "execute this python code", "run this code", "analyze this data with python",
        "plot {expr} using python", "evaluate {expr}",
        "احسب {expr}", "كم يساوي {expr}", "حل {expr}", "اكتب كود بايثون يحسب {expr}",
        "شغل كود بايثون", "نفذ هذا الكود", "حلل هذه البيانات ببايثون",
    ],
    "file": [
        "create a file named {fname}", "create file {fname} with content hello",
        "read the file {fname}", "open {fname}", "show content of {fname}",
        "delete file {fname}", "list files", "list all files in {folder}",
        "make a folder called {folder}", "create directory {folder}",
        "write hello world to {fname}", "save this text in {fname}", "organize my files",
        "انشئ ملف {fname}", "اقرا الملف {fname}", "اعرض محتوى {fname}", "احذف الملف {fname}",
        "اعرض الملفات", "انشئ مجلد {folder}", "اكتب مرحبا في الملف {fname}",
        "احفظ هذا النص في {fname}", "نظم ملفاتي",
    ],
    "web": [
        "search for {topic}", "search the web for {topic}", "find information about {topic}",
        "who is {topic}", "tell me about {topic}", "look up {topic}", "latest news on {topic}",
        "research {topic}", "google {topic}", "what do you know about {topic}",
        "ابحث عن {topic}", "ابحث في الانترنت عن {topic}", "معلومات عن {topic}",
        "من هو {topic}", "ما هو {topic}", "اخبرني عن {topic}", "اخر اخبار {topic}",
    ],
    "system": [
        "run command {cmd}", "execute {cmd}", "run {cmd} in terminal", "system command {cmd}",
        "show system info", "check my ip address", "list running processes",
        "what is my computer name", "open terminal and run {cmd}", "automate task {cmd}",
        "نفذ الامر {cmd}", "شغل الامر {cmd}", "اعرض معلومات النظام", "اعرض العمليات الجارية",
        "ما هو عنوان ip", "نفذ امر نظام {cmd}", "شغل في التيرمنال {cmd}",
    ],
}

_PREFIXES = ["", "", "please ", "can you ", "nexus ", "من فضلك ", "لو سمحت "]
_SUFFIXES = ["", "", " please", " now", " ?", " الان", " بسرعة"]


def _fill(template: str, rng: random.Random) -> str:
    out = template
    for slot, values in SLOTS.items():
        token = "{" + slot + "}"
        while token in out:
            out = out.replace(token, rng.choice(values), 1)
    return out


def build_dataset(per_intent: int = 400, seed: int = 7) -> list[tuple[str, int]]:
    """Return a shuffled list of (text, label_index) pairs, balanced per intent."""
    rng = random.Random(seed)
    data = []
    for label, intent in enumerate(INTENTS):
        templates = TEMPLATES[intent]
        for _ in range(per_intent):
            text = rng.choice(_PREFIXES) + _fill(rng.choice(templates), rng) + rng.choice(_SUFFIXES)
            data.append((text.strip(), label))
    rng.shuffle(data)
    return data


def train_val_split(data: list, val_ratio: float = 0.15):
    cut = int(len(data) * (1 - val_ratio))
    return data[:cut], data[cut:]


if __name__ == "__main__":
    for text, label in build_dataset(per_intent=3):
        print(f"{INTENTS[label]:>7} | {text}")
