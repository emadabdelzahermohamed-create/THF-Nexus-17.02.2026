from __future__ import annotations
import json
from pathlib import Path
from .models import PostIntent
from .policy import evaluate

class JsonlQueue:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def enqueue(self, intent: PostIntent) -> dict:
        intent = intent.normalized()
        decision = evaluate(intent)
        if not decision.allowed:
            raise ValueError("policy blocked: " + ",".join(decision.reasons))
        record = {"status": "queued", "intent": intent.to_dict()}
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        return record
