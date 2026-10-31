"""Build the finished CV as one print-ready HTML page (the browser saves it as PDF).

Printing from the browser shapes Arabic text perfectly and needs no PDF library
on the server.  Every value is HTML-escaped: the CV is built from user files.
"""
from html import escape

LABELS = {
    "ar": {"summary": "نبذة", "experience": "الخبرات العملية", "education": "التعليم",
           "skills": "المهارات", "certificates": "الدورات والشهادات", "languages": "اللغات",
           "projects": "المشاريع", "contact": "التواصل", "print": "حفظ PDF / طباعة"},
    "en": {"summary": "Profile", "experience": "Experience", "education": "Education",
           "skills": "Skills", "certificates": "Courses & Certificates", "languages": "Languages",
           "projects": "Projects", "contact": "Contact", "print": "Save PDF / Print"},
}
MAIN = ["summary", "experience", "projects", "education"]
SIDE = ["skills", "languages", "certificates"]

CSS = """
@page{size:A4;margin:0}*{box-sizing:border-box}
body{margin:0;background:#e9e7e2;font-family:Alexandria,Sora,Tahoma,sans-serif;color:#1d2330}
.sheet{width:210mm;min-height:297mm;margin:16px auto;background:#fff;display:grid;
grid-template-columns:68mm 1fr;box-shadow:0 8px 30px #0002}
aside{background:#17233b;color:#e8ecf4;padding:16mm 8mm}
main{padding:16mm 12mm}
h1{font-size:25px;margin:0 0 4px;line-height:1.25}.role{color:#b98a2e;font-weight:600;margin:0 0 18px}
h2{font-size:13px;letter-spacing:.06em;text-transform:uppercase;color:#b98a2e;margin:20px 0 8px;
border-bottom:1px solid #d9cfba;padding-bottom:4px}aside h2{border-color:#33415e}
ul{margin:0;padding-inline-start:18px}li{margin:3px 0;font-size:12.5px;line-height:1.55}
p{font-size:12.5px;line-height:1.7;margin:0}
.chips{display:flex;flex-wrap:wrap;gap:5px}.chips span{background:#26355a;border-radius:4px;
padding:3px 7px;font-size:11.5px}.contact div{font-size:11.5px;margin:4px 0;word-break:break-all}
[dir=rtl] .contact div{direction:ltr;text-align:right}
.bar{text-align:center;margin:12px}.bar button{font:inherit;padding:9px 22px;border:0;
border-radius:8px;background:#17233b;color:#fff;cursor:pointer}
@media print{body{background:#fff}.sheet{margin:0;box-shadow:none}.bar{display:none}}
@media (max-width:820px){.sheet{width:100%;grid-template-columns:1fr}}
"""


def _list(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{escape(i)}</li>" for i in items) + "</ul>"


def auto_summary(f: dict, lang: str) -> str:
    """A short profile written from the person's own fields when they gave none."""
    skills = "، ".join(f.get("skills", [])[:4]) if lang == "ar" else ", ".join(f.get("skills", [])[:4])
    title = f.get("title") or ("محترف" if lang == "ar" else "Professional")
    worked = bool(f.get("experience"))
    if lang == "ar":
        s = f"{title} يسعى لتقديم قيمة حقيقية وتطوير مهاراته باستمرار"
        s += f"، يمتلك خبرة في {skills}" if skills else ""
        s += "، مع خبرة عملية ميدانية." if worked else "."
    else:
        s = f"{title} focused on delivering real value and continuous growth"
        s += f", experienced in {skills}" if skills else ""
        s += ", with hands-on work experience." if worked else "."
    return s


def render(f: dict, lang: str = "ar") -> str:
    lang = "en" if lang == "en" else "ar"
    t = LABELS[lang]
    summary = " ".join(f.get("summary") or []) or auto_summary(f, lang)
    main = f"<h1>{escape(f.get('name', ''))}</h1><p class='role'>{escape(f.get('title', ''))}</p>"
    main += f"<h2>{t['summary']}</h2><p>{escape(summary)}</p>"
    for key in MAIN[1:]:
        if f.get(key):
            main += f"<h2>{t[key]}</h2>{_list(f[key])}"
    contact = [f.get("email", ""), f.get("phone", ""), *f.get("links", [])]
    side = f"<h2>{t['contact']}</h2><div class='contact'>"
    side += "".join(f"<div>{escape(c)}</div>" for c in contact if c) + "</div>"
    for key in SIDE:
        if not f.get(key):
            continue
        body = ("<div class='chips'>" + " ".join(f"<span>{escape(s)}</span>" for s in f[key]) + "</div>"
                if key == "skills" else _list(f[key]))
        side += f"<h2>{t[key]}</h2>{body}"
    direction = "rtl" if lang == "ar" else "ltr"
    title = escape(f.get("name") or "CV")
    return (f"<!doctype html><html lang='{lang}' dir='{direction}'><head><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width,initial-scale=1'><title>{title}</title>"
            "<link href='https://fonts.googleapis.com/css2?family=Alexandria:wght@400;600;700&display=swap'"
            f" rel='stylesheet'><style>{CSS}</style></head><body>"
            f"<div class='bar'><button onclick='print()'>{t['print']}</button></div>"
            f"<div class='sheet'><aside>{side}</aside><main>{main}</main></div></body></html>")
