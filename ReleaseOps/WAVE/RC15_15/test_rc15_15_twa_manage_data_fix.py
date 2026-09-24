#!/usr/bin/env python3
from pathlib import Path

gradle = Path("android-twa/app/build.gradle").read_text(encoding="utf-8")
manifest = Path("android-twa/app/src/main/AndroidManifest.xml").read_text(encoding="utf-8")

component = "com.google.androidbrowserhelper.trusted.ManageDataLauncherActivity"

assert "versionCode 15302" in gradle
assert "versionName '1.0.0-rc15.15-twa-fix'" in gradle
assert f'android:manageSpaceActivity="{component}"' in manifest
assert f'android:name="{component}"' in manifest
assert 'android.support.customtabs.trusted.MANAGE_SPACE_URL' in manifest
assert '@string/twa_default_url' in manifest
assert 'android.intent.action.APPLICATION_PREFERENCES' in manifest
assert 'android.intent.category.DEFAULT' in manifest

print("RC15_15_TWA_MANAGE_DATA_TEST=PASS")
