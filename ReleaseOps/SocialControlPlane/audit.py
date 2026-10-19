from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path


def append(path: str | Path, event: dict) -> dict:
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"ts": datetime.now(timezone.utc).isoformat(), **event}
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    payload["sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
    return payload
