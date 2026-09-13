#!/usr/bin/env python3
"""Fail-closed source gate for THF mobile release candidates.

This gate deliberately handles high-confidence source facts only. It does not turn source
inspection into a runtime/device PASS; its output always keeps runtime/device gates separate.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlparse

SKIP_DIRS = {'.git', '.pytest_cache', '__pycache__', 'build', '.gradle', 'node_modules'}
TEXT_EXT = {'.py', '.java', '.kt', '.kts', '.gradle', '.xml', '.html', '.htm', '.js', '.mjs', '.ts', '.tsx', '.json', '.toml', '.yaml', '.yml', '.properties', '.env', '.css'}
DOC_EXT = {'.md', '.rst', '.txt'}
LOOPBACK_RE = re.compile(r'https?://(?:localhost|127\.0\.0\.1|0\.0\.0\.0|\[?::1\]?)(?::\d+)?', re.I)
PLACEHOLDER_HOSTS = {'example.com', 'www.example.com', 'example.org', 'www.example.org', 'example.net', 'www.example.net'}
URL_RE = re.compile(r'https?://[^\s\"\'<>)}]+', re.I)


def iter_runtime_files(root: Path):
    for p in root.rglob('*'):
        if not p.is_file() or any(part in SKIP_DIRS for part in p.parts):
            continue
        rel = p.relative_to(root)
        # Negative examples in tests/docs are not product runtime destinations.
        if 'tests' in rel.parts or p.suffix.lower() in DOC_EXT:
            continue
        if p.suffix.lower() in TEXT_EXT or p.name == '.env.example':
            yield p


def audit(root: Path, expected_package: str | None = None) -> dict:
    violations = []
    files_scanned = 0
    for p in iter_runtime_files(root):
        files_scanned += 1
        try:
            text = p.read_text(errors='replace')
        except Exception:
            continue
        rel = str(p.relative_to(root))
        for match in LOOPBACK_RE.finditer(text):
            violations.append({'code': 'RUNTIME_LOOPBACK_URL', 'file': rel, 'value': match.group(0)})
        if 'usesCleartextTraffic="true"' in text or "usesCleartextTraffic='true'" in text:
            violations.append({'code': 'ANDROID_CLEARTEXT_ENABLED', 'file': rel})
        for raw in URL_RE.findall(text):
            host = (urlparse(raw.rstrip('.,;')).hostname or '').lower()
            if host in PLACEHOLDER_HOSTS:
                violations.append({'code': 'PLACEHOLDER_EXTERNAL_URL', 'file': rel, 'value': raw})

    build_files = list(root.rglob('android/app/build.gradle')) + list(root.rglob('android/app/build.gradle.kts'))
    build_text = '\n'.join(p.read_text(errors='replace') for p in build_files)
    if expected_package and expected_package not in build_text:
        violations.append({'code': 'PACKAGE_ID_NOT_BOUND', 'expected': expected_package})
    if build_files and not re.search(r'targetSdk(?:Version)?\s*(?:=\s*)?36\b', build_text):
        violations.append({'code': 'TARGET_SDK_36_NOT_PROVEN'})
    if build_files and not re.search(r'compileSdk(?:Version)?\s*(?:=\s*)?36\b', build_text):
        violations.append({'code': 'COMPILE_SDK_36_NOT_PROVEN'})

    return {
        'schema': 1,
        'root': str(root),
        'files_scanned': files_scanned,
        'expected_package': expected_package,
        'source_gate': 'PASS' if not violations else 'FAIL',
        'violations': violations,
        'truth_boundary': {
            'source_gate_is_not_runtime_pass': True,
            'exact_apk_inspection_required': True,
            'reachable_backend_health_auth_required_when_networked': True,
            'physical_device_acceptance_required': True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=Path)
    parser.add_argument('--package')
    parser.add_argument('--json-out', type=Path)
    args = parser.parse_args()
    result = audit(args.root.resolve(), args.package)
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    print(rendered)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(rendered + '\n')
    return 0 if result['source_gate'] == 'PASS' else 2


if __name__ == '__main__':
    raise SystemExit(main())
