"""Load a trained brain checkpoint and predict labels."""
from pathlib import Path

import torch
import torch.nn.functional as F

from core.neural_net import NexusBrain
from core.tokenizer import NexusTokenizer
from core.trainer import checkpoint


class BrainInference:
    def __init__(self, brain: str = "router"):
        self.brain = brain
        self.path: Path = checkpoint(brain)
        self.model = None
        self.tok = None
        self.intents: list[str] = []
        self.info: dict = {}
        self.reload()

    @property
    def ready(self) -> bool:
        return self.model is not None

    def reload(self) -> bool:
        if not self.path.exists():
            return False
        ckpt = torch.load(self.path, map_location="cpu", weights_only=True)
        model = NexusBrain(**ckpt["config"])
        model.load_state_dict(ckpt["state_dict"])
        model.eval()
        self.model, self.intents = model, ckpt["intents"]
        self.tok = NexusTokenizer.from_json(ckpt["tokenizer"])
        self.info = {**ckpt.get("info", {}), **ckpt["config"],
                     "params": sum(p.numel() for p in model.parameters())}
        return True

    @torch.no_grad()
    def predict(self, text: str) -> tuple[str, float, dict[str, float]]:
        """Return (label, confidence, full probability map)."""
        if not self.ready:
            raise RuntimeError(f"{self.brain} brain not trained yet - run core.trainer first")
        ids = torch.tensor([self.tok.encode(text)], dtype=torch.long)
        probs = F.softmax(self.model(ids), dim=-1)[0]
        best = int(probs.argmax())
        dist = {name: round(float(p), 4) for name, p in zip(self.intents, probs)}
        return self.intents[best], float(probs[best]), dist
