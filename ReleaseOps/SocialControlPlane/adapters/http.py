from __future__ import annotations
import json, urllib.request, urllib.parse

def post_json(url: str, headers: dict[str,str], payload: dict, timeout: int = 30) -> dict:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type":"application/json", **headers}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode() or "{}")

def post_form(url: str, headers: dict[str,str], payload: dict, timeout: int = 30) -> dict:
    data = urllib.parse.urlencode(payload).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode() or "{}")
