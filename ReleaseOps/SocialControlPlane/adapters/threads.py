from __future__ import annotations
import os
from .base import Adapter, PublishResult
from .http import post_form
from ..models import PostIntent

class ThreadsAdapter(Adapter):
    network = "threads"
    def __init__(self, user_id: str | None = None, token: str | None = None, api_version: str = "v1.0"):
        self.user_id = user_id or os.getenv("THF_THREADS_USER_ID", "")
        self.token = token or os.getenv("THF_THREADS_ACCESS_TOKEN", "")
        self.api_version = api_version
    def publish(self, intent: PostIntent) -> PublishResult:
        self.validate(intent)
        if not self.user_id or not self.token: raise RuntimeError("missing Threads credentials")
        base = f"https://graph.threads.net/{self.api_version}"
        create = post_form(f"{base}/{self.user_id}/threads", {}, {"media_type":"TEXT","text":intent.text,"access_token":self.token})
        cid = create.get("id")
        if not cid: raise RuntimeError(f"Threads create failed: {create}")
        result = post_form(f"{base}/{self.user_id}/threads_publish", {}, {"creation_id":cid,"access_token":self.token})
        eid = str(result.get("id", ""))
        if not eid: raise RuntimeError(f"Threads publish failed: {result}")
        return PublishResult("threads_direct", eid, "published")
