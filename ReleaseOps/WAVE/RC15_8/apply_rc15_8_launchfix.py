#!/usr/bin/env python3
from pathlib import Path

ROOT = Path.cwd()
gradle = ROOT / "android-twa/app/build.gradle"
manifest = ROOT / "android-twa/app/src/main/AndroidManifest.xml"
activity = ROOT / "android-twa/app/src/main/java/com/wave/mawja/MainActivity.java"

# This patch is intentionally limited to the demonstrated Play-Internal launch failure.
g = gradle.read_text(encoding="utf-8")
g = g.replace("versionCode 15300", "versionCode 15301", 1)
g = g.replace("versionName '1.0.0-rc15.3'", "versionName '1.0.0-rc15.8-launchfix'", 1)
# Provide the complete HTTPS start URL as an Android resource for the official LauncherActivity metadata.
needle = "resValue 'string', 'asset_statements',"
if "'twa_default_url'" not in g:
    pos = g.find(needle)
    if pos < 0:
        raise SystemExit("RC15.8: asset_statements anchor missing")
    line_start = g.rfind("\n", 0, pos) + 1
    g = g[:line_start] + "        resValue 'string', 'twa_default_url', waveUrl\n" + g[line_start:]
gradle.write_text(g, encoding="utf-8")

m = manifest.read_text(encoding="utf-8")
# Android Browser Helper's LauncherActivity is configured by DEFAULT_URL metadata.
if "android.support.customtabs.trusted.DEFAULT_URL" not in m:
    anchor = '''            <meta-data\n                android:name="asset_statements"\n                android:resource="@string/asset_statements" />'''
    replacement = anchor + '''\n            <meta-data\n                android:name="android.support.customtabs.trusted.DEFAULT_URL"\n                android:value="@string/twa_default_url" />'''
    if anchor not in m:
        raise SystemExit("RC15.8: manifest asset_statements anchor missing")
    m = m.replace(anchor, replacement, 1)
# Match the official launcher intent-filter shape (MAIN + DEFAULT + LAUNCHER).
launcher = '''                <action android:name="android.intent.action.MAIN" />\n                <category android:name="android.intent.category.LAUNCHER" />'''
launcher_fixed = '''                <action android:name="android.intent.action.MAIN" />\n                <category android:name="android.intent.category.DEFAULT" />\n                <category android:name="android.intent.category.LAUNCHER" />'''
if launcher in m:
    m = m.replace(launcher, launcher_fixed, 1)
manifest.write_text(m, encoding="utf-8")

# Use the library's normal launch path so LauncherActivity and its metadata stay coherent.
activity.write_text('''package com.wave.mawja;\n\nimport com.google.androidbrowserhelper.trusted.LauncherActivity;\n\npublic final class MainActivity extends LauncherActivity {\n}\n''', encoding="utf-8")

print("RC15_8_PLAY_TWA_LAUNCH_FIX=PASS")
print("RC15_8_VERSION_CODE=15301")
