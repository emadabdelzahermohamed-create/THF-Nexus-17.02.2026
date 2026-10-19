from __future__ import annotations
import os
from .base import Adapter, PublishResult
from .http import post_form
from ..models import PostIntent

class FacebookPageAdapter(Adapter):
    network = "facebook"
    def __init__(self, page_id: str | None = None, token: str | None = None, api_version: str = "v24.0"):
        self.page_id = page_id or os.getenv("THF_FACEBOOK_PAGE_ID", "")
        self.token = token or os.getenv("THF_FACEBOOK_PAGE_TOKEN", "")
        self.api_version = api_version
    def publish(self, intent: PostIntent) -> PublishResult:
        self.validate(intent)
        if not self.page_id or not self.token: raise RuntimeError("missing Facebook page credentials")
        payload = {"message": intent.text, "access_token": self.token}
        if intent.link_url: payload["link"] = intent.link_url
        result = post_form(f"https://graph.facebook.com/{self.api_version}/{self.page_id}/feed", {}, payload)
        eid = str(result.get("id", ""))
        if not eid: raise RuntimeError(f"Facebook publish failed: {result}")
        return PublishResult("facebook_direct", eid, "published")
