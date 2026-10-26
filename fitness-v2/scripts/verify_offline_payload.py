#!/usr/bin/env python3
"""Verify that the APK contains exactly the offline demo assets its catalog references."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile


CATALOG_PREFIX = b"window.THF_EXERCISES = "
CATALOG_ENTRY = "assets/pulse/data/exercises.js"
APK_MEDIA_PREFIX = "assets/pulse/"
DEMO_PATTERN = re.compile(r"^media/free-exercise-db/.+/[01]\.jpg$")


def load_catalog(content: bytes) -> list[dict]:
    if not content.startswith(CATALOG_PREFIX):
        raise ValueError("exercise catalog does not start with the canonical assignment")
    payload = content[len(CATALOG_PREFIX) :].strip()
    if not payload.endswith(b";"):
        raise ValueError("exercise catalog does not end with a semicolon")
    catalog = json.loads(payload[:-1])
    if not isinstance(catalog, list) or not catalog:
        raise ValueError("exercise catalog must be a non-empty list")
    return catalog


def referenced_demo_assets(catalog: list[dict]) -> list[str]:
    assets: list[str] = []
    for exercise in catalog:
        demo = exercise.get("demo")
        if not isinstance(demo, dict) or demo.get("offline") is not True:
            raise ValueError(f"{exercise.get('id', '<unknown>')}: demo must be offline")
        exercise_assets = demo.get("assets")
        if not isinstance(exercise_assets, list) or not exercise_assets:
            raise ValueError(f"{exercise.get('id', '<unknown>')}: demo assets are missing")
        for asset in exercise_assets:
            if not isinstance(asset, str) or not DEMO_PATTERN.fullmatch(asset):
                raise ValueError(f"{exercise.get('id', '<unknown>')}: invalid demo asset {asset!r}")
            assets.append(asset)
    if len(assets) != len(set(assets)):
        raise ValueError("exercise catalog contains duplicate demo asset references")
    return assets


def verify(apk_path: Path, source_catalog_path: Path) -> dict:
    source_catalog_bytes = source_catalog_path.read_bytes()
    source_catalog = load_catalog(source_catalog_bytes)
    expected = set(referenced_demo_assets(source_catalog))

    with zipfile.ZipFile(apk_path) as apk:
        names = apk.namelist()
        if any("stage16a" in name.lower() for name in names):
            raise ValueError("APK contains a retired Stage16A payload entry")
        try:
            packaged_catalog_bytes = apk.read(CATALOG_ENTRY)
        except KeyError as exc:
            raise ValueError(f"APK is missing {CATALOG_ENTRY}") from exc
        packaged_catalog = load_catalog(packaged_catalog_bytes)
        packaged_expected = set(referenced_demo_assets(packaged_catalog))
        actual = {
            name.removeprefix(APK_MEDIA_PREFIX)
            for name in names
            if name.startswith(APK_MEDIA_PREFIX)
            and DEMO_PATTERN.fullmatch(name.removeprefix(APK_MEDIA_PREFIX))
        }

    source_hash = hashlib.sha256(source_catalog_bytes).hexdigest()
    packaged_hash = hashlib.sha256(packaged_catalog_bytes).hexdigest()
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)
    catalog_delta = sorted(expected ^ packaged_expected)
    report = {
        "exercise_count": len(source_catalog),
        "referenced_demo_assets": len(expected),
        "packaged_demo_assets": len(actual),
        "source_catalog_sha256": source_hash,
        "packaged_catalog_sha256": packaged_hash,
        "catalog_matches_source": source_catalog_bytes == packaged_catalog_bytes,
        "missing_assets": missing,
        "unexpected_assets": unexpected,
        "catalog_asset_delta": catalog_delta,
        "stage16a_entries": 0,
    }
    if not report["catalog_matches_source"] or missing or unexpected or catalog_delta:
        raise ValueError(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apk", type=Path, required=True)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    report = verify(args.apk, args.catalog)
    args.evidence.parent.mkdir(parents=True, exist_ok=True)
    args.evidence.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
