from __future__ import annotations
from .base import Adapter, PublishResult
from ..secret_refs import resolve

class YouTubeAdapter(Adapter):
    network = 'youtube'
    def __init__(self, oauth_token_ref: str): self.oauth_token_ref = oauth_token_ref
    def publish(self, intent):
        self.validate(intent)
        resolve(self.oauth_token_ref)
        # Uploads require a local/resumable media stream, not a public media URL.
        # Keep fail-closed until the worker supplies that stream and explicit metadata.
        raise RuntimeError('youtube upload worker not provisioned: resumable media stream required')
