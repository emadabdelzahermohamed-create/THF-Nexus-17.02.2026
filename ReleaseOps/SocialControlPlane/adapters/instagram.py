from __future__ import annotations
from .base import Adapter, PublishResult
from .http import post_form
from ..secret_refs import resolve

class InstagramAdapter(Adapter):
    network = 'instagram'
    def __init__(self, account_id: str, token_ref: str, api_version: str = 'v24.0'):
        self.account_id, self.token_ref, self.api_version = account_id, token_ref, api_version
    def publish(self, intent):
        self.validate(intent)
        if not intent.media_url:
            raise ValueError('Instagram publishing requires media_url')
        token = resolve(self.token_ref)
        create = post_form(f'https://graph.facebook.com/{self.api_version}/{self.account_id}/media',
            {'image_url': intent.media_url, 'caption': intent.text, 'access_token': token})
        cid = create.get('id')
        if not cid: raise RuntimeError('Instagram media container was not created')
        result = post_form(f'https://graph.facebook.com/{self.api_version}/{self.account_id}/media_publish',
            {'creation_id': cid, 'access_token': token})
        return PublishResult('meta-direct', str(result.get('id','')), 'published')
