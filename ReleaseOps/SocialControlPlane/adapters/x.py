from __future__ import annotations
import os
from .base import Adapter, PublishResult
from .http import post_json
from ..models import PostIntent

class XAdapter(Adapter):
    network = "x"
    def __init__(self, bearer: str | None = None):
        self.bearer = bearer or os.getenv("THF_X_USER_ACCESS_TOKEN", "")
    def publish(self, intent: PostIntent) -> PublishResult:
        self.validate(intent)
        if not self.bearer: raise RuntimeError("missing X user access token")
        result = post_json("https://api.x.com/2/tweets", {"Authorization": f"Bearer {self.bearer}"}, {"text": intent.text})
        eid = str((result.get("data") or {}).get("id", ""))
        if not eid: raise RuntimeError(f"X publish failed: {result}")
        return PublishResult("x_direct", eid, "published")
