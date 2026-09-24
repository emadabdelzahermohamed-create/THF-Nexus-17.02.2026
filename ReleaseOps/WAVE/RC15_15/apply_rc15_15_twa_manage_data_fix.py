#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path.cwd()
gradle = ROOT / "android-twa/app/build.gradle"
manifest = ROOT / "android-twa/app/src/main/AndroidManifest.xml"

g = gradle.read_text(encoding="utf-8")
if "versionCode 15302" not in g:
    if "versionCode 15301" not in g:
        raise SystemExit("RC15.15: versionCode 15301 anchor missing")
    g = g.replace("versionCode 15301", "versionCode 15302", 1)
if "1.0.0-rc15.15-twa-fix" not in g:
    if "versionName '1.0.0-rc15.8-launchfix'" not in g:
        raise SystemExit("RC15.15: versionName RC15.8 anchor missing")
    g = g.replace("versionName '1.0.0-rc15.8-launchfix'", "versionName '1.0.0-rc15.15-twa-fix'", 1)
gradle.write_text(g, encoding="utf-8")

m = manifest.read_text(encoding="utf-8")
component = "com.google.androidbrowserhelper.trusted.ManageDataLauncherActivity"

if 'android:manageSpaceActivity="' + component + '"' not in m:
    match = re.search(r"<application\b[^>]*>", m, flags=re.S)
    if not match:
        raise SystemExit("RC15.15: application element missing")
    tag = match.group(0)
    updated = tag[:-1] + '\n        android:manageSpaceActivity="' + component + '">'
    m = m[:match.start()] + updated + m[match.end():]

if f'<activity android:name="{component}"' not in m and f'android:name="{component}"' not in m:
    activity = f'''
        <activity
            android:name="{component}"
            android:exported="false"
            android:enabled="true"
            android:excludeFromRecents="true">
            <meta-data
                android:name="android.support.customtabs.trusted.MANAGE_SPACE_URL"
                android:value="@string/twa_default_url" />
            <intent-filter>
                <action android:name="android.intent.action.APPLICATION_PREFERENCES" />
                <category android:name="android.intent.category.DEFAULT" />
            </intent-filter>
        </activity>
'''
    if "</application>" not in m:
        raise SystemExit("RC15.15: application closing tag missing")
    m = m.replace("</application>", activity + "\n    </application>", 1)

manifest.write_text(m, encoding="utf-8")

print("RC15_15_TWA_MANAGE_DATA_FIX=PASS")
print("RC15_15_VERSION_CODE=15302")
