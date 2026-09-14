#!/usr/bin/env python3
from __future__ import annotations
import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
OVERLAY = ROOT / 'ReleaseOps/scripts/thf_spark_rush_verified_motion_overlay_v2.py'


def make_fixture(base: pathlib.Path) -> pathlib.Path:
    root = base / 'candidate'
    asset = root / 'android/app/src/main/assets/offline.html'
    asset.parent.mkdir(parents=True)
    asset.write_text('<html>canonical placeholder</html>')
    gradle = root / 'android/app/build.gradle'
    gradle.parent.mkdir(parents=True, exist_ok=True)
    gradle.write_text('android { defaultConfig { applicationId "com.topherofit.thf.old" } }\n')
    return root


def run_overlay(kind: str) -> tuple[str, str]:
    with tempfile.TemporaryDirectory() as td:
        root = make_fixture(pathlib.Path(td))
        ev = pathlib.Path(td) / 'evidence.txt'
        subprocess.run([sys.executable, str(OVERLAY), str(root), '--kind', kind, '--evidence-out', str(ev)], check=True)
        html = (root / 'android/app/src/main/assets/offline.html').read_text()
        evidence = ev.read_text()
        return html, evidence


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def main() -> int:
    spark, sev = run_overlay('spark')
    require("THF Learn Games" in spark, 'Spark approved user-facing name missing')
    require('domain_loop=learning' in sev, 'Spark learning domain evidence missing')
    require('com.topherofit.thf.spark' in sev, 'Spark package identity missing')

    rush, rev = run_overlay('rush')
    require('THF Motion Games' in rush, 'Rush approved user-facing name missing')
    require("window.addEventListener('devicemotion',onVerifiedMotionEvent" in rush, 'device motion listener missing')
    require('if(!e.isTrusted)' in rush, 'trusted-event boundary missing')
    require('finite3(e.accelerationIncludingGravity)' in rush, 'finite motion vector validation missing')
    require("rush.phase==='LOW'&&mag>=MOTION_HIGH" in rush, 'high-threshold rep phase missing')
    require("rush.phase==='HIGH'&&mag<=MOTION_LOW" in rush, 'low-threshold completion phase missing')
    require('REP_COOLDOWN_MS=450' in rush, 'rep debounce/cooldown missing')
    require('touch never counts repetitions' in rush, 'touch non-authority disclosure missing')
    touch = re.search(r'function onLocalTouch\(p\)\{([^}]*)\}', rush, re.S)
    require(touch is not None, 'Rush touch handler missing')
    body = touch.group(1)
    require('rush.reps++' not in body and 'playerState.score++' not in body, 'touch can increment Rush progression')
    require('manual_activity_values_accepted=false' in rev, 'manual values must fail closed')
    require('verified_motion_required=true' in rev, 'verified motion requirement missing')
    require('touch_repetition_increment=false' in rev, 'touch repetition rejection missing')
    require('ranked_state_written=false' in rev and 'economy_state_written=false' in rev and 'reward_state_written=false' in rev, 'local/online authority boundary missing')
    require('online_motion_reward_authority=BACKEND_REQUIRED_NOT_IMPLEMENTED_HERE' in rev, 'online reward authority boundary missing')
    require('server_verifiable_health_evidence_claimed=false' in rev, 'must not overclaim server-verifiable health evidence')
    require('com.topherofit.thf.rush' in rev, 'Rush package identity missing')
    require('final_status=NOT_FINAL' in rev and 'device_status=PENDING' in rev, 'physical-device truth boundary missing')

    print('THF_SPARK_RUSH_VERIFIED_MOTION_OVERLAY_V2=PASS')
    print('THF_RUSH_MANUAL_ACTIVITY_AUTHORITY=REJECTED')
    print('THF_RUSH_LOCAL_REPS_SOURCE=TRUSTED_DEVICE_MOTION_ONLY')
    print('THF_RUSH_ONLINE_REWARD_AUTHORITY=BACKEND_REQUIRED')
    print('FINAL_OR_PLAY_READY=FALSE')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
