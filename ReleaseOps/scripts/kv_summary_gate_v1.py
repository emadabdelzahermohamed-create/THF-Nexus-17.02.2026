#!/usr/bin/env python3
"""Fail-closed verifier for ReleaseOps key=value summary evidence.

Unlike brittle exact-count shell greps, this accepts explicitly declared minimum
counts so duplicated evidence emitted by layered tooling cannot turn a valid
candidate into a false negative. Missing or forbidden truth markers still fail.
"""
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path


def parse_requirement(value: str) -> tuple[str, int]:
    marker, sep, count = value.rpartition(":")
    if not sep or not marker or not count.isdigit() or int(count) < 1:
        raise argparse.ArgumentTypeError("expected MARKER:MIN_COUNT")
    return marker, int(count)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("summary", type=Path)
    ap.add_argument("--require", action="append", default=[], type=parse_requirement)
    ap.add_argument("--forbid", action="append", default=[])
    ns = ap.parse_args()

    lines = [line.strip() for line in ns.summary.read_text(encoding="utf-8").splitlines() if line.strip()]
    counts = Counter(lines)
    failures: list[str] = []

    for marker, minimum in ns.require:
        actual = counts[marker]
        if actual < minimum:
            failures.append(f"required marker {marker!r}: expected >= {minimum}, got {actual}")
    for marker in ns.forbid:
        actual = counts[marker]
        if actual:
            failures.append(f"forbidden marker {marker!r}: got {actual}")

    if failures:
        print("KV_SUMMARY_GATE=FAIL")
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print("KV_SUMMARY_GATE=PASS")
    for marker, minimum in ns.require:
        print(f"PASS: {marker} count={counts[marker]} minimum={minimum}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
