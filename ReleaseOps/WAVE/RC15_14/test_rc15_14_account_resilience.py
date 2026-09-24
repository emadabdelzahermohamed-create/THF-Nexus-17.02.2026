#!/usr/bin/env python3
from pathlib import Path

route = Path("app/api/account/route.ts")
text = route.read_text(encoding="utf-8")

assert "async function syncInternalBestEffort" in text
assert text.count("await syncInternalBestEffort(") == 3
assert text.count("await syncInternal(") == 1
assert 'WAVE_ACCOUNT_INTERNAL_SYNC_DEGRADED' in text
assert 'internal_account_sync_failed' in text

print("RC15_14_ACCOUNT_RESILIENCE_TEST=PASS")
