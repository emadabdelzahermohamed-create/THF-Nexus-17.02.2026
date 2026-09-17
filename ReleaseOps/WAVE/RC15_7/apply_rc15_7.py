#!/usr/bin/env python3
from pathlib import Path

ROOT = Path.cwd()
page = ROOT / "app/downloads/page.tsx"
text = page.read_text(encoding="utf-8")

if "/downloads/WAVE_MAWJA_ANDROID.apk" not in text:
    anchor_start = text.find("<InstallAppButton")
    if anchor_start < 0:
        raise SystemExit("RC15.7: InstallAppButton anchor missing")
    anchor_end = text.find("/>", anchor_start)
    if anchor_end < 0:
        raise SystemExit("RC15.7: InstallAppButton closing marker missing")
    anchor_end += 2
    block = '''\n        <a\n          className="primary-button"\n          href="/downloads/WAVE_MAWJA_ANDROID.apk"\n          download="WAVE_MAWJA_ANDROID.apk"\n        >\n          تحميل تطبيق WAVE للأندرويد APK\n        </a>\n        <p className="muted">نسخة Android للاختبار المباشر على الهاتف — SHA-256: 0403bc725b16301ceadc9934aa22ebb529ce82f115e10fdbf12b53810ad547c9</p>'''
    text = text[:anchor_end] + block + text[anchor_end:]
    page.write_text(text, encoding="utf-8")

print("RC15_7_APK_DOWNLOAD_PAGE=PASS")
