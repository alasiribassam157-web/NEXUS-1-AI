"""Training templates for the coder brain: which programming task is being asked for."""
from agent.code_kb import TASKS

CODE_TASKS = list(TASKS)

SLOTS = {
    "lang": ["python", "javascript", "java", "c++", "c#", "go", "golang", "js", "بايثون", "جافاسكربت",
             "جافا", "سي بلس بلس", "سي شارب", ""],
}

_WRAP = ["how to {x} in {lang}", "how do i {x} in {lang}", "{lang} {x}", "{x} in {lang}", "{x} {lang} example",
         "show me how to {x} with {lang}", "كيف {x} في {lang}", "كيف {x} بلغة {lang}", "{x} بال{lang}",
         "ابغى كود {x} {lang}", "علمني {x} في {lang}", "مثال على {x} {lang}", "{x}"]

# task -> core phrasings (English and Arabic) that get wrapped by _WRAP
PHRASES = {
    "hello_world": ["print hello world", "write hello world", "hello world program", "اطبع hello world",
                    "برنامج hello world", "اول برنامج"],
    "variables": ["declare a variable", "create variables", "define variables", "تعريف متغير", "اعرف متغير",
                  "المتغيرات"],
    "if_else": ["use if else", "write an if statement", "conditional statements", "جملة if", "الشروط",
                "استخدم if else"],
    "for_loop": ["write a for loop", "loop through a list", "iterate over items", "حلقة for", "تكرار for",
                 "اسوي لوب"],
    "while_loop": ["write a while loop", "loop while a condition is true", "while loop", "حلقة while",
                   "تكرار while", "لوب while"],
    "function": ["define a function", "create a function", "write a method", "اعرف دالة", "انشئ دالة",
                 "اكتب فنكشن"],
    "list": ["create a list", "use an array", "add to an array", "append to a list", "array", "list", "arrays",
             "انشئ قائمة", "المصفوفات", "مصفوفة", "قائمة", "اضيف عنصر للقائمة"],
    "dict": ["use a dictionary", "create a map", "key value pairs", "hashmap", "dictionary", "map", "dict",
             "القاموس", "قاموس", "مفتاح وقيمة", "استخدم dictionary"],
    "class": ["create a class", "define a class", "object oriented class", "make an object", "انشئ كلاس",
              "الكلاسات", "اسوي كلاس", "البرمجة الكائنية"],
    "read_file": ["read a file", "open and read a text file", "load file content", "اقرا ملف", "قراءة ملف",
                  "افتح ملف واقراه"],
    "write_file": ["write to a file", "save text to a file", "create a text file", "اكتب في ملف",
                   "احفظ نص في ملف", "الكتابة في ملف"],
    "reverse_string": ["reverse a string", "reverse text", "flip a string backwards", "اعكس نص", "عكس نص",
                       "اقلب الكلمة"],
    "sort_list": ["sort a list", "sort an array", "order numbers", "رتب قائمة", "ترتيب مصفوفة",
                  "رتب الارقام"],
    "try_catch": ["handle exceptions", "try catch", "catch errors", "error handling", "معالجة الاخطاء",
                  "try except", "امسك الخطا"],
    "http_request": ["make an http request", "call an api", "send a get request", "fetch a url",
                     "طلب http", "استدعي api", "اجيب بيانات من رابط"],
    "json_parse": ["parse json", "read json", "convert json to object", "work with json", "التعامل مع json",
                   "اقرا json", "حول json"],
    "random_number": ["generate a random number", "random integer", "pick a random item", "رقم عشوائي",
                      "اطلع رقم عشوائي", "random"],
    "current_date": ["get the current date", "current time", "today's date", "format a date",
                     "التاريخ الحالي", "الوقت الحالي", "اجيب تاريخ اليوم"],
    "split_string": ["split a string", "join strings", "split text by comma", "قسم نص", "تقسيم النص",
                     "ادمج النصوص"],
    "sum_max": ["sum a list", "find the max of a list", "largest number in array", "average of a list",
                "مجموع قائمة", "اكبر رقم في القائمة", "اوجد المجموع"],
}

TEMPLATES = {task: [w.replace("{x}", p) for p in PHRASES[task] for w in _WRAP] for task in CODE_TASKS}
