#!/usr/bin/env python3
"""Apply a reversible THF Spark/Rush real-function candidate overlay.

The script only edits an extracted disposable source tree. It never opens or writes
canonical archives. It adds an Android Application that attaches a local game View
without replacing the shipping Activity, and fails closed when an existing custom
Application is already declared.
"""
from __future__ import annotations

import argparse
import hashlib
import pathlib
import re
import xml.etree.ElementTree as ET

ANDROID_NS = "http://schemas.android.com/apk/res/android"
ET.register_namespace("android", ANDROID_NS)

COMMON = r'''package __PACKAGE__;

import android.app.Activity;
import android.app.Application;
import android.os.Bundle;
import android.view.Gravity;
import android.view.ViewGroup;
import android.widget.FrameLayout;

public final class ThfGameApplication extends Application implements Application.ActivityLifecycleCallbacks {
    private static final int OVERLAY_ID = 0x54484631;

    @Override public void onCreate() {
        super.onCreate();
        registerActivityLifecycleCallbacks(this);
    }

    @Override public void onActivityResumed(Activity activity) {
        ViewGroup decor = (ViewGroup) activity.getWindow().getDecorView();
        if (decor.findViewById(OVERLAY_ID) != null) return;
        FrameLayout.LayoutParams lp = new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT,
                Gravity.CENTER);
        __VIEW__ view = new __VIEW__(activity);
        view.setId(OVERLAY_ID);
        decor.addView(view, lp);
    }

    @Override public void onActivityPaused(Activity activity) {
        ViewGroup decor = (ViewGroup) activity.getWindow().getDecorView();
        android.view.View v = decor.findViewById(OVERLAY_ID);
        if (v instanceof ThfLifecycleGameView) ((ThfLifecycleGameView) v).setSessionActive(false);
    }
    @Override public void onActivityStarted(Activity a) {}
    @Override public void onActivityStopped(Activity a) {}
    @Override public void onActivitySaveInstanceState(Activity a, Bundle b) {}
    @Override public void onActivityDestroyed(Activity a) {}
    @Override public void onActivityCreated(Activity a, Bundle b) {}
}
'''

BASE = r'''package __PACKAGE__;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.os.SystemClock;
import android.view.Choreographer;
import android.view.MotionEvent;
import android.view.View;

abstract class ThfLifecycleGameView extends View implements Choreographer.FrameCallback {
    protected final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
    protected boolean sessionActive = true;
    protected long sessionStartMs = SystemClock.elapsedRealtime();
    protected float dtSeconds = 0f;
    private long lastFrameNs = 0L;

    ThfLifecycleGameView(Context context) {
        super(context);
        setFocusable(true);
        setClickable(true);
        Choreographer.getInstance().postFrameCallback(this);
    }

    void setSessionActive(boolean active) {
        sessionActive = active;
        if (active) Choreographer.getInstance().postFrameCallback(this);
    }

    @Override public void doFrame(long frameTimeNanos) {
        if (!sessionActive || !isAttachedToWindow()) return;
        if (lastFrameNs != 0L) dtSeconds = Math.min(0.05f, (frameTimeNanos - lastFrameNs) / 1_000_000_000f);
        lastFrameNs = frameTimeNanos;
        updateGame(dtSeconds);
        invalidate();
        Choreographer.getInstance().postFrameCallback(this);
    }

    protected abstract void updateGame(float dt);
}
'''

SPARK = r'''package __PACKAGE__;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.view.MotionEvent;
import java.util.Random;

final class SparkLearningGameView extends ThfLifecycleGameView {
    private final Random rng = new Random(0x544846L);
    private float targetX = 0.5f, targetY = 0.55f, phase = 0f;
    private int lhs = 2, rhs = 3, score = 0, streak = 0, level = 1;
    private int correct = 5;

    SparkLearningGameView(Context c) { super(c); nextQuestion(); }

    private void nextQuestion() {
        lhs = 1 + rng.nextInt(4 + level);
        rhs = 1 + rng.nextInt(4 + level);
        correct = lhs + rhs;
        targetX = 0.18f + rng.nextFloat() * 0.64f;
        targetY = 0.34f + rng.nextFloat() * 0.48f;
    }

    @Override protected void updateGame(float dt) {
        phase += dt;
        targetY += Math.sin(phase * 2.2f) * dt * 0.025f;
    }

    @Override protected void onDraw(Canvas c) {
        super.onDraw(c);
        final float w = getWidth(), h = getHeight();
        if (w <= 0 || h <= 0) return;
        paint.setColor(0xAA081C2C); c.drawRect(0, 0, w, h * 0.20f, paint);
        paint.setColor(Color.WHITE); paint.setTextSize(Math.max(28f, h * 0.043f));
        c.drawText("Spark  •  " + lhs + " + " + rhs + " = ?", w * 0.05f, h * 0.075f, paint);
        paint.setTextSize(Math.max(20f, h * 0.030f));
        c.drawText("Score " + score + "   Streak " + streak + "   Level " + level, w * 0.05f, h * 0.14f, paint);
        float cx = targetX * w, cy = targetY * h, r = Math.max(50f, Math.min(w,h) * 0.09f);
        paint.setColor(0xDD39C5BB); c.drawCircle(cx, cy, r, paint);
        paint.setColor(Color.BLACK); paint.setTextSize(r * 0.70f);
        String a = Integer.toString(correct);
        c.drawText(a, cx - paint.measureText(a)/2f, cy + r*0.24f, paint);
        paint.setColor(Color.WHITE); paint.setTextSize(Math.max(16f, h*0.024f));
        c.drawText("Local learning round — no ranked/social/economy state is simulated offline", w*0.04f, h*0.96f, paint);
    }

    @Override public boolean onTouchEvent(MotionEvent e) {
        if (e.getAction() != MotionEvent.ACTION_UP) return true;
        float dx=e.getX()-targetX*getWidth(), dy=e.getY()-targetY*getHeight();
        float r=Math.max(50f, Math.min(getWidth(),getHeight())*0.11f);
        if (dx*dx+dy*dy <= r*r) {
            score += 10 + streak * 2; streak++;
            if (streak % 5 == 0) level++;
            nextQuestion(); performClick();
        } else { streak = 0; }
        return true;
    }
    @Override public boolean performClick() { super.performClick(); return true; }
}
'''

RUSH = r'''package __PACKAGE__;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.SystemClock;
import android.view.MotionEvent;

final class RushFitnessGameView extends ThfLifecycleGameView implements SensorEventListener {
    private final SensorManager sensors;
    private final Sensor accel;
    private int reps = 0, streak = 0;
    private float motion = 0f, filtered = 0f;
    private boolean armed = true;
    private long lastRepMs = 0L;

    RushFitnessGameView(Context c) {
        super(c);
        sensors=(SensorManager)c.getSystemService(Context.SENSOR_SERVICE);
        Sensor linear=sensors.getDefaultSensor(Sensor.TYPE_LINEAR_ACCELERATION);
        accel=linear != null ? linear : sensors.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
        if (accel != null) sensors.registerListener(this, accel, SensorManager.SENSOR_DELAY_GAME);
    }

    @Override protected void onDetachedFromWindow() {
        sensors.unregisterListener(this); super.onDetachedFromWindow();
    }

    @Override protected void updateGame(float dt) { filtered += (motion-filtered)*Math.min(1f, dt*7f); }

    @Override public void onSensorChanged(SensorEvent e) {
        float x=e.values[0], y=e.values[1], z=e.values[2];
        float mag=(float)Math.sqrt(x*x+y*y+z*z);
        if (e.sensor.getType()==Sensor.TYPE_ACCELEROMETER) mag=Math.abs(mag-SensorManager.GRAVITY_EARTH);
        motion=mag;
        long now=SystemClock.elapsedRealtime();
        if (armed && mag>3.2f && now-lastRepMs>450L) {
            reps++; streak++; lastRepMs=now; armed=false; performHapticFeedback(android.view.HapticFeedbackConstants.KEYBOARD_TAP);
        }
        if (mag<1.35f) armed=true;
    }
    @Override public void onAccuracyChanged(Sensor s,int a) {}

    @Override protected void onDraw(Canvas c) {
        super.onDraw(c); float w=getWidth(), h=getHeight(); if(w<=0||h<=0)return;
        paint.setColor(0xC80B1824); c.drawRect(0,0,w,h,paint);
        paint.setColor(Color.WHITE); paint.setTextSize(Math.max(30f,h*.052f)); c.drawText("Rush Local Motion Session",w*.06f,h*.11f,paint);
        paint.setTextSize(Math.max(22f,h*.038f));
        c.drawText("Reps  "+reps+"    Motion  "+String.format(java.util.Locale.US,"%.1f",filtered),w*.06f,h*.20f,paint);
        float bar=Math.min(1f,filtered/6f); paint.setColor(0xFF2ED39A); c.drawRect(w*.06f,h*.28f,w*(.06f+.82f*bar),h*.35f,paint);
        paint.setColor(Color.WHITE); paint.setTextSize(Math.max(17f,h*.027f));
        c.drawText(accel==null?"Motion sensor unavailable — device gate must reject sensor gameplay":"Move the phone/body rhythmically; reps are detected from local motion sensor data",w*.06f,h*.44f,paint);
        c.drawText("Offline mode stores only this local training session; ranked/social/economy state is never fabricated",w*.06f,h*.91f,paint);
        c.drawText("Touch anywhere to reset this local session",w*.06f,h*.96f,paint);
    }

    @Override public boolean onTouchEvent(MotionEvent e) {
        if(e.getAction()==MotionEvent.ACTION_UP){ reps=0; streak=0; sessionStartMs=SystemClock.elapsedRealtime(); performClick(); }
        return true;
    }
    @Override public boolean performClick(){super.performClick();return true;}
}
'''

def sha256(path: pathlib.Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('root', type=pathlib.Path)
    ap.add_argument('--app', choices=['spark','rush'], required=True)
    ap.add_argument('--manifest-out', type=pathlib.Path, required=True)
    ns=ap.parse_args()
    package=f'com.topherofit.thf.{ns.app}'
    manifest=ns.root/'android/app/src/main/AndroidManifest.xml'
    if not manifest.is_file(): raise SystemExit('AndroidManifest.xml missing')
    tree=ET.parse(manifest); app=tree.getroot().find('application')
    if app is None: raise SystemExit('application element missing')
    name_key=f'{{{ANDROID_NS}}}name'
    existing=app.attrib.get(name_key,'').strip()
    if existing and existing not in ('.ThfGameApplication', package+'.ThfGameApplication'):
        raise SystemExit('existing custom Application detected; refusing unsafe replacement')
    app.set(name_key,'.ThfGameApplication')
    tree.write(manifest,encoding='utf-8',xml_declaration=True)
    java_dir=ns.root/'android/app/src/main/java'/pathlib.Path(*package.split('.'))
    java_dir.mkdir(parents=True,exist_ok=True)
    view='SparkLearningGameView' if ns.app=='spark' else 'RushFitnessGameView'
    files={
      'ThfGameApplication.java':COMMON.replace('__PACKAGE__',package).replace('__VIEW__',view),
      'ThfLifecycleGameView.java':BASE.replace('__PACKAGE__',package),
      f'{view}.java':(SPARK if ns.app=='spark' else RUSH).replace('__PACKAGE__',package),
    }
    for name,text in files.items(): (java_dir/name).write_text(text,encoding='utf-8')
    rows=[]
    for p in sorted([manifest,*[java_dir/n for n in files]]):
        rows.append(f'{sha256(p)}  {p.relative_to(ns.root)}')
    ns.manifest_out.parent.mkdir(parents=True,exist_ok=True)
    ns.manifest_out.write_text('\n'.join(rows)+'\n',encoding='utf-8')
    print(f'OVERLAY_APP={ns.app}')
    print(f'OVERLAY_PACKAGE={package}')
    print(f'OVERLAY_FILES={len(rows)}')
    print('OFFLINE_AUTHORITY=LOCAL_ONLY_NO_RANKED_SOCIAL_ECONOMY_MUTATION')
    print('READINESS_PROMOTION=NO')
    return 0

if __name__=='__main__': raise SystemExit(main())
