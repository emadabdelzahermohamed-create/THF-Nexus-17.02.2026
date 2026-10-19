from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional

SUPPORTED_NETWORKS = {"facebook", "instagram", "threads", "youtube", "tiktok", "x"}

@dataclass(frozen=True)
class PostIntent:
    network: str
    text: str
    media_url: Optional[str] = None
    link_url: Optional[str] = None
    topic: str = "ecosystem"
    source_evidence: Optional[str] = None
    created_at: str = ""

    def normalized(self) -> "PostIntent":
        network = self.network.strip().lower()
        if network not in SUPPORTED_NETWORKS:
            raise ValueError(f"unsupported network: {network}")
        created_at = self.created_at or datetime.now(timezone.utc).isoformat()
        return PostIntent(network, self.text.strip(), self.media_url, self.link_url,
                          self.topic.strip() or "ecosystem", self.source_evidence, created_at)

    def to_dict(self) -> dict:
        return asdict(self.normalized())
