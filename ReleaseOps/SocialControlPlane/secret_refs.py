from __future__ import annotations
import os
import re

_REF = re.compile(r'^env:([A-Z][A-Z0-9_]*)$')

class SecretRefError(ValueError): pass

def resolve(ref: str) -> str:
    """Resolve a secret by reference only. Raw secrets are deliberately rejected."""
    m = _REF.match(ref or '')
    if not m:
        raise SecretRefError('secret must be an env:NAME reference')
    value = os.getenv(m.group(1))
    if not value:
        raise SecretRefError(f'missing secret environment variable: {m.group(1)}')
    return value
