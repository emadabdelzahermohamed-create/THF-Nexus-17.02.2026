#!/usr/bin/env python3
"""Apply reversible real-game candidate overlays to extracted Learn/Fitness Games.

Canonical archives are never modified. The overlay attaches a full-screen local game
view through an Android Application lifecycle callback and fails closed if a custom
Application would be replaced. Online/ranked/social/economy authority is never
simulated by these local modes.
"""
from __future__ import annotations
import argparse, hashlib, pathlib, xml.etree.ElementTree as ET

ANDROID_NS="http://schemas.android.com/apk/res/android"
ET.register_namespace("android",ANDROID_NS)

APP=r'''package __PACKAGE__;
import android.app.Activity; import android.app.Application; import android.os.Bundle;
import android.view.Gravity; import android.view.ViewGroup; import android.widget.FrameLayout;
public final class ThfGameApplication extends Application implements Application.ActivityLifecycleCallbacks {
  private static final int ID=0x54484632;
  @Override public void onCreate(){super.onCreate();registerActivityLifecycleCallbacks(this);}
  @Override public void onActivityResumed(Activity a){
    ViewGroup d=(ViewGroup)a.getWindow().getDecorView(); if(d.findViewById(ID)!=null)return;
    FrameLayout.LayoutParams lp=new FrameLayout.LayoutParams(-1,-1,Gravity.CENTER);
    ThfLocalGameView v=new ThfLocalGameView(a);v.setId(ID);d.addView(v,lp);v.setSessionActive(true);
  }
  @Override public void onActivityPaused(Activity a){android.view.View v=a.getWindow().getDecorView().findViewById(ID);if(v instanceof ThfLocalGameView)((ThfLocalGameView)v).setSessionActive(false);}
  @Override public void onActivityCreated(Activity a,Bundle b){} @Override public void onActivityStarted(Activity a){}
  @Override public void onActivityStopped(Activity a){} @Override public void onActivitySaveInstanceState(Activity a,Bundle b){}
  @Override public void onActivityDestroyed(Activity a){}
}
'''

LEARN=r'''package __PACKAGE__;
import android.content.Context; import android.graphics.Canvas; import android.graphics.Color; import android.graphics.Paint;
import android.os.SystemClock; import android.view.Choreographer; import android.view.MotionEvent; import android.view.View; import java.util.Random;
final class ThfLocalGameView extends View implements Choreographer.FrameCallback {
  private final Paint p=new Paint(Paint.ANTI_ALIAS_FLAG); private final Random rng=new Random(0x4c4541524eL);
  private boolean active=true; private long lastNs=0; private float avatarX=.18f,avatarY=.72f,targetX=.72f,targetY=.46f,phase=0;
  private int lhs=2,rhs=3,answer=5,score=0,streak=0,mastery=0,level=1; private String feedback="Move the avatar, then tap the answer orb";
  ThfLocalGameView(Context c){super(c);setFocusable(true);setClickable(true);nextQuestion();Choreographer.getInstance().postFrameCallback(this);}
  void setSessionActive(boolean a){active=a;if(a)Choreographer.getInstance().postFrameCallback(this);}
  private void nextQuestion(){lhs=1+rng.nextInt(3+level);rhs=1+rng.nextInt(3+level);answer=lhs+rhs;targetX=.48f+rng.nextFloat()*.36f;targetY=.30f+rng.nextFloat()*.38f;}
  @Override public void doFrame(long ns){if(!active||!isAttachedToWindow())return;float dt=lastNs==0?0:Math.min(.05f,(ns-lastNs)/1_000_000_000f);lastNs=ns;phase+=dt;targetY+=Math.sin(phase*2.1f)*dt*.018f;invalidate();Choreographer.getInstance().postFrameCallback(this);}
  @Override protected void onDraw(Canvas c){super.onDraw(c);float w=getWidth(),h=getHeight();if(w<=0||h<=0)return;
    p.setColor(0xff0b2030);c.drawRect(0,0,w,h,p);p.setColor(Color.WHITE);p.setTextSize(Math.max(26,h*.045f));c.drawText("Learn Games • Level "+level+" • Mastery "+mastery+"%",w*.04f,h*.08f,p);
    p.setTextSize(Math.max(22,h*.036f));c.drawText(lhs+" + "+rhs+" = ?   Score "+score+"   Streak "+streak,w*.04f,h*.15f,p);
    float ar=Math.max(34,Math.min(w,h)*.055f);p.setColor(0xff42a5f5);c.drawCircle(avatarX*w,avatarY*h,ar,p);p.setColor(Color.WHITE);p.setTextSize(ar*.55f);c.drawText("AVATAR",avatarX*w-ar*.8f,avatarY*h+ar*.18f,p);
    float tr=Math.max(46,Math.min(w,h)*.075f);p.setColor(0xff56d6a2);c.drawCircle(targetX*w,targetY*h,tr,p);p.setColor(Color.BLACK);p.setTextSize(tr*.7f);String a=Integer.toString(answer);c.drawText(a,targetX*w-p.measureText(a)/2,targetY*h+tr*.25f,p);
    p.setColor(Color.WHITE);p.setTextSize(Math.max(17,h*.026f));c.drawText(feedback,w*.04f,h*.88f,p);c.drawText("Local practice only — ranked/social/economy state is never fabricated offline",w*.04f,h*.95f,p);
  }
  @Override public boolean onTouchEvent(MotionEvent e){if(e.getAction()!=MotionEvent.ACTION_UP)return true;float w=getWidth(),h=getHeight(),x=e.getX()/w,y=e.getY()/h;
    float dx=x-targetX,dy=y-targetY;if(dx*dx+dy*dy<.018f){score+=10+streak*2;streak++;mastery=Math.min(100,mastery+8);if(streak%4==0)level++;feedback="Correct answer — mastery advanced";nextQuestion();performClick();return true;}
    float vx=x-avatarX,vy=y-avatarY,len=(float)Math.sqrt(vx*vx+vy*vy);if(len>0){float step=Math.min(.14f,len);avatarX+=vx/len*step;avatarY+=vy/len*step;}streak=0;feedback="Avatar moved — reach and submit the correct answer";performClick();return true;}
  @Override public boolean performClick(){super.performClick();return true;}
}
'''

FITNESS=r'''package __PACKAGE__;
import android.content.Context; import android.graphics.Canvas; import android.graphics.Color; import android.graphics.Paint;
import android.hardware.Sensor; import android.hardware.SensorEvent; import android.hardware.SensorEventListener; import android.hardware.SensorManager;
import android.os.SystemClock; import android.view.Choreographer; import android.view.MotionEvent; import android.view.View;
final class ThfLocalGameView extends View implements Choreographer.FrameCallback,SensorEventListener {
  private final Paint p=new Paint(Paint.ANTI_ALIAS_FLAG); private final SensorManager sm; private final Sensor sensor;
  private boolean active=true,armed=true; private long lastNs=0,lastRepMs=0; private float motion=0,filtered=0,avatarY=.72f; private int repCount=0,setCount=0,streak=0; private String exercise="Motion Reps";
  ThfLocalGameView(Context c){super(c);setFocusable(true);setClickable(true);sm=(SensorManager)c.getSystemService(Context.SENSOR_SERVICE);Sensor s=sm.getDefaultSensor(Sensor.TYPE_LINEAR_ACCELERATION);sensor=s!=null?s:sm.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);if(sensor!=null)sm.registerListener(this,sensor,SensorManager.SENSOR_DELAY_GAME);Choreographer.getInstance().postFrameCallback(this);}
  void setSessionActive(boolean a){active=a;if(a)Choreographer.getInstance().postFrameCallback(this);}
  @Override protected void onDetachedFromWindow(){sm.unregisterListener(this);super.onDetachedFromWindow();}
  @Override public void doFrame(long ns){if(!active||!isAttachedToWindow())return;float dt=lastNs==0?0:Math.min(.05f,(ns-lastNs)/1_000_000_000f);lastNs=ns;filtered+=(motion-filtered)*Math.min(1f,dt*8f);avatarY=.72f-Math.min(.20f,filtered*.018f);invalidate();Choreographer.getInstance().postFrameCallback(this);}
  @Override public void onSensorChanged(SensorEvent e){float x=e.values[0],y=e.values[1],z=e.values[2];float m=(float)Math.sqrt(x*x+y*y+z*z);if(e.sensor.getType()==Sensor.TYPE_ACCELEROMETER)m=Math.abs(m-SensorManager.GRAVITY_EARTH);motion=m;long now=SystemClock.elapsedRealtime();if(armed&&m>3.0f&&now-lastRepMs>450){repCount++;streak++;lastRepMs=now;armed=false;performHapticFeedback(android.view.HapticFeedbackConstants.KEYBOARD_TAP);if(repCount%10==0)setCount++;}if(m<1.25f)armed=true;}
  @Override public void onAccuracyChanged(Sensor s,int a){}
  @Override protected void onDraw(Canvas c){super.onDraw(c);float w=getWidth(),h=getHeight();if(w<=0||h<=0)return;p.setColor(0xff101b26);c.drawRect(0,0,w,h,p);p.setColor(Color.WHITE);p.setTextSize(Math.max(27,h*.046f));c.drawText("Fitness Games • "+exercise,w*.04f,h*.09f,p);p.setTextSize(Math.max(21,h*.034f));c.drawText("Reps "+repCount+"   Sets "+setCount+"   Streak "+streak+"   Motion "+String.format(java.util.Locale.US,"%.1f",filtered),w*.04f,h*.16f,p);
    float ar=Math.max(38,Math.min(w,h)*.06f);p.setColor(0xffffb74d);c.drawCircle(w*.5f,avatarY*h,ar,p);p.setColor(Color.WHITE);p.setTextSize(ar*.5f);c.drawText("PLAYER",w*.5f-ar*.72f,avatarY*h+ar*.17f,p);float bar=Math.min(1,filtered/6f);p.setColor(0xff45d69b);c.drawRect(w*.08f,h*.27f,w*(.08f+.82f*bar),h*.34f,p);
    p.setColor(Color.WHITE);p.setTextSize(Math.max(17,h*.026f));c.drawText(sensor==null?"Sensor unavailable — hardware acceptance must reject motion gameplay":"Move rhythmically; repetitions are validated from local motion sensor events",w*.04f,h*.86f,p);c.drawText("Tap to reset local training. Ranked/social/economy state remains server-authoritative",w*.04f,h*.94f,p);}
  @Override public boolean onTouchEvent(MotionEvent e){if(e.getAction()==MotionEvent.ACTION_UP){repCount=0;setCount=0;streak=0;performClick();}return true;} @Override public boolean performClick(){super.performClick();return true;}
}
'''

def sha(p:pathlib.Path)->str:
  h=hashlib.sha256();h.update(p.read_bytes());return h.hexdigest()

def main()->int:
  ap=argparse.ArgumentParser();ap.add_argument('root',type=pathlib.Path);ap.add_argument('--kind',choices=['learn','fitness'],required=True);ap.add_argument('--manifest-out',type=pathlib.Path,required=True);a=ap.parse_args()
  package='com.thf.topherofit.learngames' if a.kind=='learn' else 'com.thf.topherofit.fitnessgames'
  manifest=a.root/'app/src/main/AndroidManifest.xml'
  if not manifest.is_file():raise SystemExit('AndroidManifest.xml missing')
  tree=ET.parse(manifest);app=tree.getroot().find('application');
  if app is None:raise SystemExit('application element missing')
  key=f'{{{ANDROID_NS}}}name';existing=app.attrib.get(key,'').strip()
  if existing and existing not in ('.ThfGameApplication',package+'.ThfGameApplication'):raise SystemExit('custom Application exists; refusing replacement')
  app.set(key,'.ThfGameApplication');tree.write(manifest,encoding='utf-8',xml_declaration=True)
  java=a.root/'app/src/main/java'/pathlib.Path(*package.split('.'));java.mkdir(parents=True,exist_ok=True)
  files={'ThfGameApplication.java':APP.replace('__PACKAGE__',package),'ThfLocalGameView.java':(LEARN if a.kind=='learn' else FITNESS).replace('__PACKAGE__',package)}
  for n,t in files.items():(java/n).write_text(t,encoding='utf-8')
  rows=[]
  for p in [manifest,*[java/n for n in files]]:rows.append(f'{sha(p)}  {p.relative_to(a.root)}')
  a.manifest_out.parent.mkdir(parents=True,exist_ok=True);a.manifest_out.write_text('\n'.join(rows)+'\n')
  print('OVERLAY_KIND='+a.kind);print('OVERLAY_PACKAGE='+package);print('OVERLAY_FILES='+str(len(rows)));print('OFFLINE_AUTHORITY=LOCAL_ONLY_NO_RANKED_SOCIAL_ECONOMY_MUTATION');print('READINESS_PROMOTION=NO')
  return 0
if __name__=='__main__':raise SystemExit(main())
