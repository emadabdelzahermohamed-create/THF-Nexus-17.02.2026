from __future__ import annotations
from dataclasses import dataclass
from ..models import PostIntent

@dataclass(frozen=True)
class PublishResult:
    provider: str
    external_id: str
    raw_status: str

class Adapter:
    network: str
    def validate(self, intent: PostIntent) -> None:
        if intent.normalized().network != self.network:
            raise ValueError("network mismatch")
    def publish(self, intent: PostIntent) -> PublishResult:
        raise NotImplementedError
