#!/usr/bin/env python3
"""Fail-closed source auditor for THF Spark/Rush game-like Android experiences.

This intentionally proves only source-level contracts. It never promotes a candidate to
runtime/device PASS and never treats static strings as proof of physical interaction.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SKIP = {'.git', '.gradle', 'build', 'node_modules', 'tests', 'test', 'androidTest', '__pycache__'}
SOURCE_EXT = {'.kt', '.java', '.xml', '.js', '.ts', '.tsx'}

SIGNALS = {
    'interactive_input': re.compile(r'\b(onTouchEvent|MotionEvent|pointerInput|detectTapGestures|clickable\s*\{|setOnClickListener|onClick\s*=|GestureDetector|KeyEvent)\b'),
    'timed_or_frame_loop': re.compile(r'\b(Choreographer|doFrame|postFrameCallback|requestAnimationFrame|CountDownTimer|TimerTask|withFrameNanos|LaunchedEffect|delay\s*\(|tick\b|update\s*\()'),
    'state_or_progression': re.compile(r'\b(score|points|level|progress|streak|combo|xp|experience|completed|correct|incorrect|reps?|sets?)\b', re.I),
    'render_or_motion': re.compile(r'\b(Canvas|SurfaceView|TextureView|draw\s*\(|graphicsLayer|animate\w*AsState|Animatable|ObjectAnimator|ValueAnimator|translate|velocity|position)\b'),
    'learning_domain': re.compile(r'\b(quiz|question|answer|lesson|learn|vocabulary|math|correctAnswer|choice|mastery)\b', re.I),
    'fitness_domain': re.compile(r'\b(workout|exercise|fitness|reps?|repetitions?|sets?|timer|calorie|movement|motion|sensor|accelerometer|squat|pushup|run|pace)\b', re.I),
}


def runtime_files(root: Path):
    for p in root.rglob('*'):
        if not p.is_file() or p.suffix not in SOURCE_EXT:
            continue
        rel = p.relative_to(root)
        if any(part in SKIP for part in rel.parts):
            continue
        yield p


def audit(root: Path, profile: str) -> dict:
    evidence: dict[str, list[str]] = {k: [] for k in SIGNALS}
    scanned = 0
    for p in runtime_files(root):
        scanned += 1
        text = p.read_text(errors='replace')
        rel = str(p.relative_to(root))
        for name, pattern in SIGNALS.items():
            if pattern.search(text):
                evidence[name].append(rel)

    required = ['interactive_input', 'state_or_progression']
    loop_or_motion = bool(evidence['timed_or_frame_loop'] or evidence['render_or_motion'])
    domain_key = 'learning_domain' if profile == 'learning' else 'fitness_domain'
    missing = [name for name in required if not evidence[name]]
    if not loop_or_motion:
        missing.append('timed_or_frame_loop_OR_render_or_motion')
    if not evidence[domain_key]:
        missing.append(domain_key)

    return {
        'schema': 1,
        'profile': profile,
        'root': str(root),
        'files_scanned': scanned,
        'source_contract': 'PASS' if not missing else 'FAIL',
        'missing_required_signals': missing,
        'evidence_files': {k: sorted(set(v))[:40] for k, v in evidence.items() if v},
        'truth_boundary': {
            'source_contract_is_not_runtime_pass': True,
            'ui_only_shell_is_not_accepted': True,
            'exact_apk_inspection_required': True,
            'physical_device_acceptance_required': True,
            'offline_mode_must_not_fake_online_state': True,
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('root', type=Path)
    ap.add_argument('--profile', required=True, choices=['learning', 'fitness'])
    ap.add_argument('--json-out', type=Path)
    args = ap.parse_args()
    result = audit(args.root.resolve(), args.profile)
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    print(rendered)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(rendered + '\n')
    return 0 if result['source_contract'] == 'PASS' else 2


if __name__ == '__main__':
    raise SystemExit(main())
