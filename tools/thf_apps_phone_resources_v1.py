#!/usr/bin/env python3
"""Create deterministic, reversible Android phone-resource overlays for scoped THF apps.

This tool deliberately changes presentation/package resources only. It does not create auth,
network, social, economy, admin or deletion behavior. Existing functional implementations
must pass their independent real-function gates.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import zlib
from pathlib import Path
import xml.etree.ElementTree as ET

ANDROID_NS = "http://schemas.android.com/apk/res/android"
ET.register_namespace("android", ANDROID_NS)

LOCALES = [
    "en", "ar", "zh", "hi", "ko", "tr", "es", "fr", "de", "pt",
    "ru", "ja", "id", "ur", "bn", "fa", "it", "nl", "pl", "sw",
]

APP_COLORS = {
    "core": "#124E78",
    "forge": "#7A3E00",
    "echo": "#5B2C83",
    "codex": "#1E6B45",
    "vault": "#244B8A",
    "signal": "#7A244A",
    "command": "#30343B",
}


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _set_string(path: Path, key: str, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError as exc:
            raise SystemExit(f"invalid strings XML {path}: {exc}")
    else:
        root = ET.Element("resources")
    item = next((x for x in root.findall("string") if x.get("name") == key), None)
    if item is None:
        item = ET.SubElement(root, "string", {"name": key})
    item.text = value
    ET.indent(root, space="    ")
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def _update_manifest(path: Path, package_id: str) -> None:
    tree = ET.parse(path)
    root = tree.getroot()
    manifest_pkg = root.get("package")
    text = path.read_text(encoding="utf-8", errors="ignore")
    if package_id not in text and manifest_pkg not in (None, package_id):
        raise SystemExit(f"package mismatch: expected {package_id}, manifest={manifest_pkg}")
    app = root.find("application")
    if app is None:
        raise SystemExit("manifest has no application")
    app.set(f"{{{ANDROID_NS}}}label", "@string/app_name")
    app.set(f"{{{ANDROID_NS}}}icon", "@mipmap/ic_launcher")
    app.set(f"{{{ANDROID_NS}}}roundIcon", "@mipmap/ic_launcher_round")
    app.set(f"{{{ANDROID_NS}}}localeConfig", "@xml/locales_config")
    ET.indent(root, space="    ")
    tree.write(path, encoding="utf-8", xml_declaration=True)


def _png_chunk(tag: bytes, payload: bytes) -> bytes:
    return struct.pack(">I", len(payload)) + tag + payload + struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF)


def _hex_rgb(color: str) -> tuple[int, int, int]:
    c = color.lstrip("#")
    return tuple(int(c[i:i+2], 16) for i in (0, 2, 4))


def _store_icon(path: Path, color: str, app: str) -> None:
    """Generate a valid 512x512 opaque PNG with a deterministic THF geometric mark."""
    w = h = 512
    r, g, b = _hex_rgb(color)
    accent = (245, 247, 250)
    idx = list(APP_COLORS).index(app) + 1
    rows = []
    for y in range(h):
        row = bytearray([0])
        for x in range(w):
            # Safe-zone geometric mark: central diamond + app-specific bars.
            diamond = abs(x - 256) + abs(y - 256) < 132
            bar = (84 + idx * 13 <= x <= 100 + idx * 13 and 160 <= y <= 352)
            rr, gg, bb = accent if (diamond or bar) else (r, g, b)
            row.extend((rr, gg, bb, 255))
        rows.append(bytes(row))
    raw = b"".join(rows)
    png = b"\x89PNG\r\n\x1a\n"
    png += _png_chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
    png += _png_chunk(b"IDAT", zlib.compress(raw, 9))
    png += _png_chunk(b"IEND", b"")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)


def apply(root: Path, app: str, package_id: str, display_name: str) -> dict:
    main = root / "android" / "app" / "src" / "main"
    manifest = main / "AndroidManifest.xml"
    if not manifest.is_file():
        raise SystemExit(f"missing Android main manifest under {root}")
    color = APP_COLORS[app]
    _update_manifest(manifest, package_id)
    _set_string(main / "res" / "values" / "strings.xml", "app_name", display_name)
    # Brand names are intentionally identical in Arabic resources; surrounding UX copy is
    # owned by each app's localization catalog and must not be faked by this overlay.
    _set_string(main / "res" / "values-ar" / "strings.xml", "app_name", display_name)
    _write(main / "res" / "xml" / "locales_config.xml",
           '<?xml version="1.0" encoding="utf-8"?>\n<locale-config xmlns:android="http://schemas.android.com/apk/res/android">\n' +
           ''.join(f'    <locale android:name="{x}" />\n' for x in LOCALES) + '</locale-config>\n')
    _write(main / "res" / "values" / "thf_launcher_colors.xml",
           f'<?xml version="1.0" encoding="utf-8"?>\n<resources><color name="thf_launcher_background">{color}</color></resources>\n')
    foreground = '''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="108dp" android:height="108dp" android:viewportWidth="108" android:viewportHeight="108">
    <path android:fillColor="#FFFFFFFF" android:pathData="M54,18 L90,54 L54,90 L18,54 Z" />
    <path android:fillColor="#00000000" android:strokeColor="#FF000000" android:strokeWidth="0" android:pathData="M0,0" />
</vector>
'''
    mono = '''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="108dp" android:height="108dp" android:viewportWidth="108" android:viewportHeight="108">
    <path android:fillColor="#FF000000" android:pathData="M54,18 L90,54 L54,90 L18,54 Z" />
</vector>
'''
    _write(main / "res" / "drawable" / "ic_launcher_foreground.xml", foreground)
    _write(main / "res" / "drawable" / "ic_launcher_monochrome.xml", mono)
    adaptive = '''<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/thf_launcher_background" />
    <foreground android:drawable="@drawable/ic_launcher_foreground" />
    <monochrome android:drawable="@drawable/ic_launcher_monochrome" />
</adaptive-icon>
'''
    _write(main / "res" / "mipmap-anydpi-v26" / "ic_launcher.xml", adaptive)
    _write(main / "res" / "mipmap-anydpi-v26" / "ic_launcher_round.xml", adaptive)
    store = root / "store-assets" / "google-play" / "icon-512.png"
    _store_icon(store, color, app)
    report = {
        "schema": "thf-app-phone-resources-v1",
        "app": app,
        "package_id": package_id,
        "display_name": display_name,
        "locales_declared": LOCALES,
        "locale_count": len(LOCALES),
        "adaptive_icon": True,
        "monochrome_icon": True,
        "store_icon_512_png": True,
        "store_icon_sha256": hashlib.sha256(store.read_bytes()).hexdigest(),
        "functional_behavior_synthesized": False,
        "physical_device_pass": False,
        "final_or_play_ready": False,
    }
    return report


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--app", required=True, choices=tuple(APP_COLORS))
    ap.add_argument("--package", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--report", required=True, type=Path)
    ns = ap.parse_args()
    report = apply(ns.root.resolve(), ns.app, ns.package, ns.name)
    ns.report.parent.mkdir(parents=True, exist_ok=True)
    ns.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))

if __name__ == "__main__":
    main()
