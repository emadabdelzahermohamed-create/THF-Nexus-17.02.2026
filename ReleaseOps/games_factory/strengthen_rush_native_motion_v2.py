#!/usr/bin/env python3
"""Harden Rush native motion overlay and apply phone-safe responsive HUD.

Runs only on an extracted authoritative RC4 tree. Canonical archives are never
modified. Repetitions remain sensor-derived/local/non-rewarding. The HUD uses
measured text fitting and multi-line rows so narrow phones cannot clip status text.
"""
from __future__ import annotations
import argparse, hashlib, pathlib
import xml.etree.ElementTree as ET

ANDROID_NS='http://schemas.android.com/apk/res/android'
ET.register_namespace('android',ANDROID_NS)

MOTION_ICON='''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp" android:height="108dp"
    android:viewportWidth="108" android:viewportHeight="108">
    <path android:fillColor="#0B1824" android:pathData="M0,0h108v108h-108z"/>
    <path android:fillColor="#2ED39A" android:pathData="M60,8L30,58H50L44,100L80,46H58Z"/>
    <path android:fillColor="#FFFFFF" android:fillAlpha="0.92" android:pathData="M16,76H30L36,64L44,88L51,72H66"/>
</vector>
'''

def sha256(p:pathlib.Path)->str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('root',type=pathlib.Path); ap.add_argument('--evidence-out',type=pathlib.Path,required=True); ns=ap.parse_args()
    root=ns.root.resolve(); package=pathlib.Path('com/topherofit/thf/rush')
    candidates=list(root.rglob(str(pathlib.Path('android/app/src/main/java')/package/'RushFitnessGameView.java')))
    if len(candidates)!=1: raise SystemExit(f'expected exactly one generated RushFitnessGameView.java, found {len(candidates)}')
    p=candidates[0]; s=p.read_text(encoding='utf-8'); before=sha256(p)
    old='''    private int reps = 0, streak = 0;\n    private float motion = 0f, filtered = 0f;\n    private boolean armed = true;\n    private long lastRepMs = 0L;'''
    new='''    private int reps = 0, streak = 0, trustedSensorEvents = 0, rejectedSensorEvents = 0;\n    private float motion = 0f, filtered = 0f;\n    private boolean armed = true;\n    private long lastRepMs = 0L, lastSensorTimestampNs = 0L;'''
    if old not in s: raise SystemExit('native Rush V1 field anchor missing')
    s=s.replace(old,new,1)
    start='''    @Override public void onSensorChanged(SensorEvent e) {\n        float x=e.values[0], y=e.values[1], z=e.values[2];\n        float mag=(float)Math.sqrt(x*x+y*y+z*z);\n        if (e.sensor.getType()==Sensor.TYPE_ACCELEROMETER) mag=Math.abs(mag-SensorManager.GRAVITY_EARTH);\n        motion=mag;\n        long now=SystemClock.elapsedRealtime();\n        if (armed && mag>3.2f && now-lastRepMs>450L) {\n            reps++; streak++; lastRepMs=now; armed=false; performHapticFeedback(android.view.HapticFeedbackConstants.KEYBOARD_TAP);\n        }\n        if (mag<1.35f) armed=true;\n    }'''
    hardened='''    @Override public void onSensorChanged(SensorEvent e) {\n        if (e == null || accel == null || e.sensor == null || e.sensor != accel || e.values == null || e.values.length < 3) { rejectedSensorEvents++; return; }\n        final float x=e.values[0], y=e.values[1], z=e.values[2];\n        if (!Float.isFinite(x) || !Float.isFinite(y) || !Float.isFinite(z)) { rejectedSensorEvents++; return; }\n        if (e.timestamp <= 0L || (lastSensorTimestampNs != 0L && e.timestamp <= lastSensorTimestampNs)) { rejectedSensorEvents++; return; }\n        lastSensorTimestampNs=e.timestamp; trustedSensorEvents++;\n        float mag=(float)Math.sqrt(x*x+y*y+z*z);\n        if (!Float.isFinite(mag)) { rejectedSensorEvents++; return; }\n        if (e.sensor.getType()==Sensor.TYPE_ACCELEROMETER) mag=Math.abs(mag-SensorManager.GRAVITY_EARTH);\n        motion=mag; long now=SystemClock.elapsedRealtime();\n        if (armed && mag>3.2f && now-lastRepMs>450L) { reps++; streak++; lastRepMs=now; armed=false; performHapticFeedback(android.view.HapticFeedbackConstants.KEYBOARD_TAP); }\n        if (mag<1.35f) armed=true;\n    }'''
    if start not in s: raise SystemExit('native Rush V1 sensor method anchor missing')
    s=s.replace(start,hardened,1)
    draw_start=s.index('    @Override protected void onDraw(Canvas c) {')
    draw_end=s.index('\n    @Override public boolean onTouchEvent',draw_start)
    responsive='''    private void fitText(String text, float preferred, float min, float maxWidth) {\n        paint.setTextSize(preferred);\n        while (paint.getTextSize() > min && paint.measureText(text) > maxWidth) paint.setTextSize(paint.getTextSize()-2f);\n    }\n\n    private void drawFit(Canvas c, String text, float x, float y, float preferred, float min, float maxWidth) {\n        fitText(text, preferred, min, maxWidth); c.drawText(text,x,y,paint);\n    }\n\n    @Override protected void onDraw(Canvas c) {\n        super.onDraw(c); final float w=getWidth(), h=getHeight(); if(w<=0||h<=0)return;\n        final float pad=Math.max(18f,w*.045f), max=w-pad*2f;\n        paint.setColor(0xC80B1824); c.drawRect(0,0,w,h,paint); paint.setColor(Color.WHITE);\n        drawFit(c,"THF Motion Games",pad,h*.09f,Math.max(28f,h*.046f),22f,max);\n        drawFit(c,"Local verified-motion session",pad,h*.145f,Math.max(18f,h*.027f),15f,max);\n        drawFit(c,"Reps  "+reps+"    Motion  "+String.format(java.util.Locale.US,"%.1f",filtered),pad,h*.215f,Math.max(22f,h*.033f),17f,max);\n        drawFit(c,"Verified samples  "+trustedSensorEvents+"    Rejected  "+rejectedSensorEvents,pad,h*.26f,Math.max(16f,h*.023f),13f,max);\n        float bar=Math.min(1f,filtered/6f); paint.setColor(0xFF2ED39A); c.drawRect(pad,h*.30f,pad+max*bar,h*.35f,paint); paint.setColor(Color.WHITE);\n        if(accel==null) {\n            drawFit(c,"Motion sensor unavailable",pad,h*.43f,Math.max(18f,h*.027f),15f,max);\n            drawFit(c,"This device cannot pass motion gameplay.",pad,h*.47f,Math.max(16f,h*.023f),13f,max);\n        } else {\n            drawFit(c,"Move the phone/body rhythmically.",pad,h*.43f,Math.max(18f,h*.027f),15f,max);\n            drawFit(c,"Reps come only from verified sensor events.",pad,h*.47f,Math.max(16f,h*.023f),13f,max);\n        }\n        drawFit(c,"Offline: local training only; no rewards or ranked state.",pad,h*.88f,Math.max(15f,h*.021f),12f,max);\n        drawFit(c,"Touch anywhere to reset this local session.",pad,h*.93f,Math.max(15f,h*.021f),12f,max);\n    }'''
    s=s[:draw_start]+responsive+s[draw_end:]
    p.write_text(s,encoding='utf-8'); after=sha256(p)
    required=['e.sensor != accel','Float.isFinite(x)','e.timestamp <= lastSensorTimestampNs','trustedSensorEvents++','rejectedSensorEvents++','reps++','paint.measureText(text) > maxWidth','THF Motion Games','no rewards or ranked state']
    for x in required:
        if x not in s: raise SystemExit('postcondition missing: '+x)
    touch=s[s.index('@Override public boolean onTouchEvent'):s.index('@Override public boolean performClick')]
    if 'reps++' in touch or 'reps +=' in touch: raise SystemExit('touch repetition authority detected')
    manifest=root/'android/app/src/main/AndroidManifest.xml'; tree=ET.parse(manifest); app=tree.getroot().find('application')
    if app is None: raise SystemExit('application missing')
    app.set(f'{{{ANDROID_NS}}}label','THF Motion Games'); app.set(f'{{{ANDROID_NS}}}icon','@drawable/thf_motion_games_icon'); app.set(f'{{{ANDROID_NS}}}roundIcon','@drawable/thf_motion_games_icon'); tree.write(manifest,encoding='utf-8',xml_declaration=True)
    drawable=root/'android/app/src/main/res/drawable'; drawable.mkdir(parents=True,exist_ok=True); icon=drawable/'thf_motion_games_icon.xml'; icon.write_text(MOTION_ICON,encoding='utf-8')
    ev=ns.evidence_out; ev.parent.mkdir(parents=True,exist_ok=True)
    ev.write_text('\n'.join(['schema=thf-rush-native-verified-motion-v3-phone-ui',f'file={p.relative_to(root).as_posix()}',f'sha256_before={before}',f'sha256_after={after}','motion_source=Android_SensorManager_SensorEvent','registered_sensor_identity_required=true','finite_three_axis_required=true','monotonic_hardware_timestamp_required=true','manual_activity_values_accepted=false','touch_repetition_increment=false','local_repetitions_reward_authorized=false','reward_bearing_health_evidence=BACKEND_REQUIRED','responsive_phone_hud=true','measured_text_fit=true','hud_multiline=true','user_facing_name=THF Motion Games','canonical_package_id=com.topherofit.thf.rush','launcher_icon=@drawable/thf_motion_games_icon',f'launcher_icon_sha256={sha256(icon)}','product_specific_icon=true','canonical_archive_mutated=false','device_status=PENDING','final_status=NOT_FINAL'])+'\n',encoding='utf-8')
    print(ev.read_text(),end=''); return 0
if __name__=='__main__': raise SystemExit(main())
