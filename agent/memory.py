"""Short conversation memory: resolve follow-ups like «وكم عدد سكانها؟» to the last subject."""
import re
import time
from collections import OrderedDict

MAX_SESSIONS = 2000
TTL_SECONDS = 2 * 3600

# (pattern for a follow-up without its subject, rewrite using {e} = remembered subject)
_FOLLOW_UPS = [
    (r"عاصمت(?:ها|ه)", "عاصمة {e}"), (r"سكان(?:ها|ه)", "سكان {e}"), (r"عملت(?:ها|ه)", "عملة {e}"),
    (r"لغت(?:ها|ه) الرسمية|لغت(?:ها|ه)", "اللغة الرسمية في {e}"), (r"(?:تأسست|تاسست|تأسس|تاسس)\s*$", "تأسست {e}"),
    (r"(?:الجو|الطقس|الحرارة) (?:فيها|فيه|هناك)", "الطقس في {e}"),
    (r"\bits capital\b", "capital of {e}"), (r"\bits population\b|how many people live there", "population of {e}"),
    (r"\bits currency\b", "currency of {e}"), (r"\bwhen was it founded\b", "when was {e} founded"),
    (r"\bweather there\b", "weather in {e}"),
    (r"\bwhen was (?:he|she|it) born\b", "when was {e} born"), (r"\bwhere was (?:he|she) born\b", "where was {e} born"),
    (r"^و?\s*متى (?:ولد|ولدت|انولد)\s*$", "متى ولد {e}"), (r"^و?\s*(?:اين|أين|وين) (?:ولد|ولدت)\s*$", "أين ولد {e}"),
    (r"^(?:و\s*)?(?:المزيد|اكثر|أكثر|تكلم اكثر|زدني)\s*$", "معلومات عن {e}"),
    (r"^(?:tell me )?more\s*$", "tell me about {e}"),
]


class ConversationMemory:
    def __init__(self):
        self._sessions: OrderedDict[str, tuple[float, str]] = OrderedDict()

    def subject(self, session: str) -> str:
        stamp, entity = self._sessions.get(session, (0.0, ""))
        return entity if time.time() - stamp < TTL_SECONDS else ""

    def remember(self, session: str, entity: str) -> None:
        if not session or not entity:
            return
        self._sessions[session] = (time.time(), entity)
        self._sessions.move_to_end(session)
        while len(self._sessions) > MAX_SESSIONS:
            self._sessions.popitem(last=False)

    def resolve(self, session: str, message: str) -> str:
        """Rewrite a follow-up question to include the remembered subject (or return it unchanged)."""
        entity = self.subject(session)
        if not entity:
            return message
        text = re.sub(r"[؟?]+\s*$", "", message.strip())
        for pattern, rewrite in _FOLLOW_UPS:
            if re.search(pattern, text, re.IGNORECASE):
                return re.sub(pattern, rewrite.format(e=entity), text, count=1, flags=re.IGNORECASE)
        return message
