"""Turn the raw text of someone's documents into CV fields.

Pipeline: contacts (regex) → section headings (Arabic + English) → skills that
appear anywhere in the text → a best guess for the name and job title.
"""
import re

SECTIONS = {
    "summary": ["نبذة", "ملخص", "الملف الشخصي", "عني", "الهدف الوظيفي", "summary", "profile",
                "about me", "objective", "career objective"],
    "experience": ["الخبرات", "الخبرة", "الخبرات العملية", "الخبرة العملية", "الخبرة المهنية",
                   "experience", "work experience", "professional experience", "employment history"],
    "education": ["التعليم", "المؤهلات", "المؤهل العلمي", "المؤهلات العلمية", "الشهادات العلمية",
                  "education", "academic background", "qualifications"],
    "skills": ["المهارات", "المهارات التقنية", "المهارات الشخصية", "skills", "technical skills",
               "core skills", "competencies"],
    "certificates": ["الدورات", "الدورات التدريبية", "الشهادات", "الشهادات المهنية", "certificates",
                     "certifications", "courses", "training", "licenses"],
    "languages": ["اللغات", "languages"],
    "projects": ["المشاريع", "projects"],
    "contact": ["التواصل", "معلومات التواصل", "بيانات التواصل", "contact", "contact info",
                "contact information", "personal information", "البيانات الشخصية"],
}
SKILL_WORDS = [
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "SQL", "HTML", "CSS", "React",
    "Node.js", "Django", "FastAPI", "Flask", "Git", "Docker", "Linux", "AWS", "Azure",
    "Machine Learning", "Deep Learning", "PyTorch", "TensorFlow", "Data Analysis", "Power BI",
    "Excel", "Word", "PowerPoint", "Photoshop", "Figma", "AutoCAD", "SAP", "Scrum",
    "تحليل البيانات", "إدارة المشاريع", "العمل الجماعي", "مهارات التواصل", "القيادة", "حل المشكلات",
    "خدمة العملاء", "المبيعات", "التسويق", "المحاسبة", "إدارة الوقت", "التفاوض",
]
TITLE_HINTS = ["مهندس", "مطور", "محاسب", "مدير", "أخصائي", "اخصائي", "مصمم", "معلم", "طبيب",
               "محلل", "مشرف", "فني", "engineer", "developer", "manager", "analyst", "designer",
               "specialist", "accountant", "teacher", "consultant", "officer", "student", "طالب"]

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE = re.compile(r"(?:\+|00)?\d[\d\s-]{7,15}\d")
LINK = re.compile(r"(?:https?://)?(?:www\.)?(?:linkedin\.com|github\.com)/[\w\-/]+", re.I)
BULLET = re.compile(r"^[\s•●▪◦\-\*–·]+")


def _heading(line: str) -> str | None:
    clean = BULLET.sub("", line).strip().strip(":：").strip().lower()
    if not clean or len(clean) > 40:
        return None
    for key, names in SECTIONS.items():
        if clean in names:
            return key
    return None


def _lines(text: str) -> list[str]:
    text = text.replace("\r", "\n").replace("‏", "").replace("‎", "")
    return [re.sub(r"\s+", " ", l).strip() for l in text.split("\n") if l.strip()]


def _looks_like_name(line: str) -> bool:
    words = line.split()
    return (2 <= len(words) <= 5 and len(line) < 45 and "@" not in line and not _heading(line)
            and not any(ch.isdigit() for ch in line) and not re.search(r"[A-Z][a-z]+[A-Z]", line))


def _title_at(lines: list[str]) -> int:
    for i, line in enumerate(lines[:40]):
        if len(line) < 60 and len(line.split()) <= 6 and any(h in line.lower() for h in TITLE_HINTS):
            return i
    return -1


def _name_title(lines: list[str], email: str) -> tuple[str, str]:
    """The name usually sits right above the job title (also in two-column PDFs)."""
    t = _title_at(lines)
    if t > 0 and _looks_like_name(lines[t - 1]):
        return lines[t - 1], lines[t]
    name = next((l for l in lines[:6] if _looks_like_name(l)), "")
    if not name and email:
        name = email.split("@")[0].replace(".", " ").title()
    return name, lines[t] if t >= 0 and lines[t] != name else ""


def _skills(text: str, listed: list[str]) -> list[str]:
    found = [s for s in SKILL_WORDS if re.search(r"(?<!\w)" + re.escape(s) + r"(?!\w)", text, re.I)]
    for line in listed:  # split "Python, SQL | Excel" style lines into single skills
        found += [p.strip() for p in re.split(r"[,،|;/•]", line)
                  if 1 < len(p.strip()) < 35 and not re.search(r"[a-z][A-Z]", p)]
    seen, out = set(), []
    for s in found:
        if s.lower() not in seen:
            seen.add(s.lower())
            out.append(s)
    return out[:24]


def parse(text: str) -> dict:
    lines = _lines(text)
    m = EMAIL.search(text)
    email = m.group(0) if m else ""
    phone = PHONE.search(text.replace(email, "") if email else text)
    links = sorted(set(LINK.findall(text)))
    buckets = {key: [] for key in SECTIONS}
    current = None
    for line in lines:
        key = _heading(line)
        if key:
            current = key
        elif current:
            buckets[current].append(BULLET.sub("", line).strip())
    name, title = _name_title(lines, email)
    buckets.pop("contact")
    fields = {
        "name": name,
        "title": title,
        "email": email,
        "phone": phone.group(0).strip() if phone else "",
        "links": links,
        "skills": _skills(text, buckets.pop("skills")),
    }
    for key, items in buckets.items():
        fields[key] = [i for i in items if i and i not in (email, name, title)][:30]
    return fields
