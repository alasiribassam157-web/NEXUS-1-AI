"""Synthetic bilingual training data for both brains, plus the developer's taught corrections."""
import json
import random
from pathlib import Path

from core import templates_code, templates_router

INTENTS = templates_router.INTENTS
CUSTOM_FILE = Path(__file__).resolve().parent.parent / "data" / "custom_examples.jsonl"
CUSTOM_WEIGHT = 8

# brain name -> (labels, templates, slots, examples per label)
BRAINS = {
    "router": (templates_router.INTENTS, templates_router.TEMPLATES, templates_router.SLOTS, 1100),
    "coder": (templates_code.CODE_TASKS, templates_code.TEMPLATES, templates_code.SLOTS, 330),
}

_PREFIXES = ["", "", "", "please ", "can you ", "nexus ", "من فضلك ", "لو سمحت ", "ابغى ", "i want to "]
_SUFFIXES = ["", "", "", " please", " now", " ?", "؟", " الان", " بسرعة", " لو سمحت"]


def _fill(template: str, slots: dict, rng: random.Random) -> str:
    out = template
    for slot, values in slots.items():
        token = "{" + slot + "}"
        while token in out:
            out = out.replace(token, rng.choice(values), 1)
    return " ".join(out.split())


def load_custom(brain: str = "router") -> list[dict]:
    """Examples the developer taught from the dashboard (data/custom_examples.jsonl)."""
    if not CUSTOM_FILE.exists():
        return []
    labels = BRAINS[brain][0]
    rows = [json.loads(line) for line in CUSTOM_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]
    return [r for r in rows if r.get("brain", "router") == brain and r.get("intent") in labels]


def add_custom(text: str, label: str, brain: str = "router") -> int:
    if label not in BRAINS[brain][0]:
        raise ValueError(f"Unknown label for {brain}: {label}")
    CUSTOM_FILE.parent.mkdir(exist_ok=True)
    row = {"text": text.strip(), "intent": label}
    if brain != "router":
        row["brain"] = brain
    with CUSTOM_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return len(load_custom(brain))


def build_dataset(brain: str = "router", seed: int = 7) -> tuple[list[tuple[str, int]], int]:
    """Return (shuffled (text, label) pairs, number of taught examples)."""
    labels, templates, slots, per_label = BRAINS[brain]
    rng = random.Random(seed)
    data = []
    for label, name in enumerate(labels):
        for _ in range(per_label):
            text = rng.choice(_PREFIXES) + _fill(rng.choice(templates[name]), slots, rng) + rng.choice(_SUFFIXES)
            data.append((text.strip(), label))
    custom = load_custom(brain)
    for row in custom:
        # Oversample taught examples so a handful of corrections actually move the model.
        data += [(row["text"], labels.index(row["intent"]))] * CUSTOM_WEIGHT
    rng.shuffle(data)
    return data, len(custom)


def train_val_split(data: list, val_ratio: float = 0.15):
    cut = int(len(data) * (1 - val_ratio))
    return data[:cut], data[cut:]


if __name__ == "__main__":
    for brain_name, (names, *_rest) in BRAINS.items():
        sample, _ = build_dataset(brain_name)
        print(f"== {brain_name}: {len(sample)} examples")
        for text, label in sample[:5]:
            print(f"{names[label]:>14} | {text}")
