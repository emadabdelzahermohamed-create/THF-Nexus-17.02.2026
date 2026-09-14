#!/usr/bin/env python3
"""Harden the disposable Rush native game overlay against client/manual rep injection.

Run only after apply_spark_rush_real_game_overlay_v1.py on an extracted authoritative
RC4 tree. Canonical archives are never modified. Repetitions remain local/non-rewarding.
"""
from __future__ import annotations
import argparse, hashlib, pathlib


def sha256(p: pathlib.Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('root', type=pathlib.Path)
    ap.add_argument('--evidence-out', type=pathlib.Path, required=True)
    ns=ap.parse_args()
    root=ns.root.resolve()
    package=pathlib.Path('com/topherofit/thf/rush')
    candidates=list(root.rglob(str(pathlib.Path('android/app/src/main/java')/package/'RushFitnessGameView.java')))
    if len(candidates)!=1:
        raise SystemExit(f'expected exactly one generated RushFitnessGameView.java, found {len(candidates)}')
    p=candidates[0]
    s=p.read_text(encoding='utf-8')
    before=sha256(p)

    old_fields='''    private int reps = 0, streak = 0;\n    private float motion = 0f, filtered = 0f;\n    private boolean armed = true;\n    private long lastRepMs = 0L;'''
    new_fields='''    private int reps = 0, streak = 0, trustedSensorEvents = 0, rejectedSensorEvents = 0;\n    private float motion = 0f, filtered = 0f;\n    private boolean armed = true;\n    private long lastRepMs = 0L, lastSensorTimestampNs = 0L;'''
    if old_fields not in s:
        raise SystemExit('native Rush V1 field anchor missing; refusing stale/unknown overlay')
    s=s.replace(old_fields,new_fields,1)

    start='''    @Override public void onSensorChanged(SensorEvent e) {\n        float x=e.values[0], y=e.values[1], z=e.values[2];\n        float mag=(float)Math.sqrt(x*x+y*y+z*z);\n        if (e.sensor.getType()==Sensor.TYPE_ACCELEROMETER) mag=Math.abs(mag-SensorManager.GRAVITY_EARTH);\n        motion=mag;\n        long now=SystemClock.elapsedRealtime();\n        if (armed && mag>3.2f && now-lastRepMs>450L) {\n            reps++; streak++; lastRepMs=now; armed=false; performHapticFeedback(android.view.HapticFeedbackConstants.KEYBOARD_TAP);\n        }\n        if (mag<1.35f) armed=true;\n    }'''
    hardened='''    @Override public void onSensorChanged(SensorEvent e) {\n        // Android framework SensorEvent is the sole local repetition input. No manual/touch\n        // activity total can enter this state machine. Reward-bearing evidence stays server-side.\n        if (e == null || accel == null || e.sensor == null || e.sensor != accel || e.values == null || e.values.length < 3) { rejectedSensorEvents++; return; }\n        final float x=e.values[0], y=e.values[1], z=e.values[2];\n        if (!Float.isFinite(x) || !Float.isFinite(y) || !Float.isFinite(z)) { rejectedSensorEvents++; return; }\n        if (e.timestamp <= 0L || (lastSensorTimestampNs != 0L && e.timestamp <= lastSensorTimestampNs)) { rejectedSensorEvents++; return; }\n        lastSensorTimestampNs=e.timestamp; trustedSensorEvents++;\n        float mag=(float)Math.sqrt(x*x+y*y+z*z);\n        if (!Float.isFinite(mag)) { rejectedSensorEvents++; return; }\n        if (e.sensor.getType()==Sensor.TYPE_ACCELEROMETER) mag=Math.abs(mag-SensorManager.GRAVITY_EARTH);\n        motion=mag;\n        long now=SystemClock.elapsedRealtime();\n        if (armed && mag>3.2f && now-lastRepMs>450L) {\n            reps++; streak++; lastRepMs=now; armed=false; performHapticFeedback(android.view.HapticFeedbackConstants.KEYBOARD_TAP);\n        }\n        if (mag<1.35f) armed=true;\n    }'''
    if start not in s:
        raise SystemExit('native Rush V1 sensor method anchor missing; refusing stale/unknown overlay')
    s=s.replace(start,hardened,1)

    old_draw='''        c.drawText("Reps  "+reps+"    Motion  "+String.format(java.util.Locale.US,"%.1f",filtered),w*.06f,h*.20f,paint);'''
    new_draw='''        c.drawText("Reps  "+reps+"    Motion  "+String.format(java.util.Locale.US,"%.1f",filtered)+"    Verified samples "+trustedSensorEvents,w*.06f,h*.20f,paint);'''
    if old_draw not in s: raise SystemExit('native Rush HUD anchor missing')
    s=s.replace(old_draw,new_draw,1)

    p.write_text(s,encoding='utf-8')
    after=sha256(p)
    required=[
        'e.sensor != accel', 'e.values.length < 3', 'Float.isFinite(x)',
        'e.timestamp <= lastSensorTimestampNs', 'trustedSensorEvents++',
        'rejectedSensorEvents++', 'reps++', 'Touch anywhere to reset this local session'
    ]
    for x in required:
        if x not in s: raise SystemExit('postcondition missing: '+x)
    # Touch may reset but must never increment a repetition.
    touch=s[s.index('@Override public boolean onTouchEvent'):s.index('@Override public boolean performClick')]
    if 'reps++' in touch or 'reps +=' in touch:
        raise SystemExit('touch repetition authority detected')

    ev=ns.evidence_out
    ev.parent.mkdir(parents=True,exist_ok=True)
    ev.write_text('\n'.join([
        'schema=thf-rush-native-verified-motion-v2',
        f'file={p.relative_to(root).as_posix()}',
        f'sha256_before={before}',
        f'sha256_after={after}',
        'motion_source=Android_SensorManager_SensorEvent',
        'registered_sensor_identity_required=true',
        'finite_three_axis_required=true',
        'monotonic_hardware_timestamp_required=true',
        'manual_activity_values_accepted=false',
        'touch_repetition_increment=false',
        'local_repetitions_reward_authorized=false',
        'reward_bearing_health_evidence=BACKEND_REQUIRED',
        'canonical_archive_mutated=false',
        'device_status=PENDING',
        'final_status=NOT_FINAL',
    ])+'\n',encoding='utf-8')
    print(ev.read_text(),end='')
    return 0

if __name__=='__main__': raise SystemExit(main())
