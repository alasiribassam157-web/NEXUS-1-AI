"""Honest held-out test: 95 freshly written questions the brain never trains on (no template phrasing).

Measures the router brain ALONE (no critic, no internet), so it shows how well the brain itself
understands new ways of asking.   Run:  py -m tests.heldout     (writes models/heldout.json)
"""
import json
import time
from collections import Counter

from core.inference import BrainInference
from core.trainer import MODELS

HELDOUT = {
    "chat": ["صباح الورد يا نكسس", "انت روبوت؟", "تسلم يا غالي", "hey buddy how's your day", "مين صممك",
             "ابي اسولف معك شوي", "good job thanks a ton", "يا هلا ومرحبا"],
    "python": ["لو ضربت 23 في 19 كم يطلع", "اقسم 900 على 12", "اجمع 45 و 78", "what do you get when you multiply 13 by 17",
               "2 أس 8 كم", "15 بالمية من 320", "ناتج 4500 ناقص 1000", "calc 99 * 99"],
    "file": ["سجل ملاحظة في ملف اسمه shopping.txt", "ورني وش فيه ملف notes.txt", "امسح ملف old.txt", "what files do I have",
             "make a new text file called plan.md", "افتح لي report.md", "جهز مجلد للصور", "store this in todo.txt"],
    "web": ["حدثني عن تاريخ الأندلس", "وش قصة سور الصين", "who discovered penicillin", "ابغى نبذة عن ابن بطوطة",
            "what's the tallest building in the world", "متى بدأت الحرب العالمية الأولى", "وين تقع جزر المالديف",
            "شو هي النظرية النسبية"],
    "system": ["شغل ipconfig", "ابي اعرف اسم جهازي", "show me the running tasks", "نفذ dir في التيرمينال"],
    "code": ["ابغى دالة بالجافا تجمع رقمين", "how can I loop over a list in python", "اكتب لي كلاس بسيط في سي شارب",
             "sort numbers javascript", "كيف اقرا ملف نصي ببايثون", "طريقة عمل try catch في جافا", "json parse in go",
             "عكس سلسلة نصية في سي بلس بلس"],
    "weather": ["هل بتمطر اليوم في أبها", "الحرارة برا كم في الدمام", "is it sunny in dubai", "وش الطقس عندكم في الكويت",
                "تتوقع الجو حلو بكرة في جدة", "how cold is london right now", "الجو غبار في الرياض؟", "حالة الطقس في تبوك"],
    "currency": ["الف ريال كم تسوى بالدولار", "سعر اليورو اليوم بالريال", "how many euros for 500 dollars",
                 "الدينار الكويتي كم ريال", "بكم الجنيه الاسترليني", "حول لي 2000 ين", "قيمة الدرهم مقابل الدولار",
                 "exchange 300 usd to eur"],
    "datetime": ["اليوم وش التاريخ", "what's the date", "الساعة الحين كم بالضبط", "كم الوقت عندكم",
                 "وش تاريخ اليوم بالهجري", "اي يوم احنا اليوم", "time now please"],
    "units": ["كم كيلو في 10 باوند", "20 ميل كم كيلو", "حرارة 40 مئوية كم فهرنهايت", "how many centimeters is 6 feet",
              "5 جالون كم لتر", "كم متر في 3 اميال", "convert 150 pounds into kilograms", "2 تيرا كم جيجا"],
    "prayer": ["متى يأذن الظهر عندنا في الرياض", "وقت المغرب اليوم في مكة", "باقي كم على صلاة العشاء",
               "fajr prayer time in dubai", "اوقات الصلوات في جدة", "متى الفجر بكرة", "salah times cairo",
               "كم الساعة اذان العصر"],
    "translate": ["وش يعني كلمة computer", "ترجم لي صباح الخير بالانجليزي", "how do i say thank you in arabic",
                  "كلمة قطة بالانجليزي وش", "what's the arabic word for book", "معنى كلمة خوارزمية بالانجليزي",
                  "translate beautiful into arabic", "مدرسة وش تصير بالانقليزي"],
}


def run(verbose: bool = True) -> dict:
    brain, hits, misses = BrainInference("router"), Counter(), []
    total = sum(len(qs) for qs in HELDOUT.values())
    for intent, questions in HELDOUT.items():
        for q in questions:
            got, conf, _ = brain.predict(q)
            if got == intent:
                hits[intent] += 1
            else:
                misses.append({"q": q, "want": intent, "got": got, "confidence": round(conf, 2)})
    correct = sum(hits.values())
    report = {"date": time.strftime("%Y-%m-%d %H:%M"), "total": total, "correct": correct,
              "accuracy": round(correct / total, 4), "brain": brain.info.get("size"), "params": brain.info.get("params"),
              "by_intent": {k: f"{hits[k]}/{len(v)}" for k, v in HELDOUT.items()}, "misses": misses}
    (MODELS / "heldout.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    if verbose:
        for m in misses:
            print(f"  ✗ {m['q']}  want={m['want']} got={m['got']} ({m['confidence']})")
        print(f"\nHeld-out (brain alone, unseen phrasing): {correct}/{total} = {correct / total:.1%}")
    return report


if __name__ == "__main__":
    run()
