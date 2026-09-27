#!/usr/bin/env python3
from pathlib import Path
import argparse, shutil

parser = argparse.ArgumentParser()
parser.add_argument("--source-root", type=Path, required=True)
args = parser.parse_args()
root = args.source_root.resolve()
overlay = Path(__file__).resolve().parent / "android"
target = root / "android"
if not (root / "static/assets/avatar/thf_mpfb_stage16a_ual12_animated.glb").is_file():
    raise SystemExit("canonical Stage16A asset missing")
for src in overlay.rglob("*"):
    if src.is_dir():
        continue
    rel = src.relative_to(overlay)
    dest = target / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
canonical = root / "static/assets/avatar/thf_mpfb_stage16a_ual12_animated.glb"
packaged = target / "app/src/main/assets/offline/thf_mpfb_stage16a_ual12_animated.glb"
packaged.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(canonical, packaged)
print("Android50002 overlay applied with canonical Stage16A payload")
