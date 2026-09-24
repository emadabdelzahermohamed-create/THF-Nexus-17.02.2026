#!/usr/bin/env python3
from pathlib import Path

ROOT = Path.cwd()
route = ROOT / "app/api/account/route.ts"
text = route.read_text(encoding="utf-8")

call_count = text.count("await syncInternal(")
if call_count != 3:
    raise SystemExit(f"RC15.14: expected 3 account sync calls, found {call_count}")

text = text.replace("await syncInternal(", "await syncInternalBestEffort(")

anchor = '''  if (!response.ok) throw new Error("internal_account_sync_failed");
}

async function anonymizedEmail'''
replacement = '''  if (!response.ok) throw new Error("internal_account_sync_failed");
}

async function syncInternalBestEffort(path: string, method: string, payload?: unknown) {
  try {
    await syncInternal(path, method, payload);
    return true;
  } catch (error) {
    console.warn("WAVE_ACCOUNT_INTERNAL_SYNC_DEGRADED", error instanceof Error ? error.message : String(error));
    return false;
  }
}

async function anonymizedEmail'''

if anchor not in text:
    raise SystemExit("RC15.14: syncInternal function anchor missing")
text = text.replace(anchor, replacement, 1)

if text.count("await syncInternalBestEffort(") != 3:
    raise SystemExit("RC15.14: best-effort call rewrite incomplete")
if text.count("await syncInternal(") != 1:
    raise SystemExit("RC15.14: syncInternal must remain only inside best-effort wrapper")

route.write_text(text, encoding="utf-8")
print("RC15_14_ACCOUNT_RESILIENCE=PASS")
print("RC15_14_ACCOUNT_SYNC_CALLS=3")
