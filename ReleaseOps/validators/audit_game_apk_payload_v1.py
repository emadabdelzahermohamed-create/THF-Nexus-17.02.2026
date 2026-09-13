#!/usr/bin/env python3
"""Fail-closed APK payload audit for THF game-like Android candidates.

This gate is intentionally independent of source/build success. It inspects packaged
DEX/assets and rejects WebView/offline fallback shells presented as games.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import zipfile


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def printable(data: bytes) -> str:
    # DEX string data remains searchable as ASCII/UTF-8 byte runs for our explicit
    # Android framework/runtime symbols; do not decode arbitrary binary wholesale.
    return '\n'.join(m.group(0).decode('utf-8', 'ignore') for m in re.finditer(rb'[\x20-\x7e]{4,}', data))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('apk', type=pathlib.Path)
    ap.add_argument('--profile', choices=['learning', 'fitness'], required=True)
    ap.add_argument('--expected-sha256')
    ap.add_argument('--json-out', type=pathlib.Path)
    ns = ap.parse_args()

    actual = sha256(ns.apk)
    if ns.expected_sha256 and actual.lower() != ns.expected_sha256.lower():
        raise SystemExit(f'exact APK SHA mismatch: {actual}')

    with zipfile.ZipFile(ns.apk) as z:
        names = z.namelist()
        dex_names = [n for n in names if re.fullmatch(r'classes(?:\d+)?\.dex', n)]
        if not dex_names:
            raise SystemExit('APK has no classes.dex payload')
        dex = b'\n'.join(z.read(n) for n in dex_names)
        text = printable(dex)
        asset_names = [n for n in names if n.startswith('assets/') and not n.endswith('/')]

    def has(*needles: str) -> bool:
        low = text.lower()
        return any(n.lower() in low for n in needles)

    webview_shell = has('android/webkit/WebView', 'android.webkit.WebView', 'WebViewClient') and has('loadUrl')
    offline_html = any(n.lower().endswith('offline.html') for n in asset_names)
    frame_loop = has('Choreographer', 'doFrame')
    canvas_render = has('android/graphics/Canvas', 'android.graphics.Canvas', 'drawCanvas', 'onDraw')
    touch_input = has('MotionEvent', 'onTouchEvent')
    learning_state = has('score', 'streak', 'level', 'nextQuestion', 'LearningGame')
    sensor_runtime = has('SensorManager') and has('SensorEvent', 'TYPE_ACCELEROMETER', 'TYPE_LINEAR_ACCELERATION')
    fitness_state = has('reps', 'lastRep', 'motion', 'FitnessGame')

    common_real_game = frame_loop and canvas_render and touch_input
    if ns.profile == 'learning':
        domain = learning_state
    else:
        domain = sensor_runtime and fitness_state

    real_game_payload = common_real_game and domain
    wrapper_only = (webview_shell or offline_html) and not real_game_payload
    status = 'PASS' if real_game_payload and not wrapper_only else 'FAIL'

    out = {
        'schema': 'thf-game-apk-payload-v1',
        'profile': ns.profile,
        'apk_sha256': actual,
        'zip_entry_count': len(names),
        'dex_count': len(dex_names),
        'asset_count': len(asset_names),
        'signals': {
            'webview_shell': webview_shell,
            'offline_html': offline_html,
            'frame_loop': frame_loop,
            'canvas_render': canvas_render,
            'touch_input': touch_input,
            'learning_state': learning_state,
            'sensor_runtime': sensor_runtime,
            'fitness_state': fitness_state,
            'real_game_payload': real_game_payload,
            'wrapper_only': wrapper_only,
        },
        'payload_status': status,
        'physical_device_required': True,
        'final_status': 'NOT_FINAL',
    }
    rendered = json.dumps(out, indent=2, sort_keys=True) + '\n'
    if ns.json_out:
        ns.json_out.parent.mkdir(parents=True, exist_ok=True)
        ns.json_out.write_text(rendered, encoding='utf-8')
    print(rendered, end='')
    return 0 if status == 'PASS' else 2


if __name__ == '__main__':
    raise SystemExit(main())
