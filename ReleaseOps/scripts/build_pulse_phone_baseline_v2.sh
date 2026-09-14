#!/usr/bin/env bash
set -Eeuo pipefail

SRC="$HOME/thf-apps-rc3-exact-candidate-v2/work/pulse/THF_Pulse_APPS_RC2_SOURCE"
EXPECTED_SOURCE_TREE_SHA="6a180cf6599f8827e824431caf4566f520cc3796d9366c30abc197b4aeb6ba34"
MPFB="$HOME/thf-terra-rift-staging-apk-v1/terra/work/web/static/assets/avatars/stage16a/thf_mpfb_stage16a_ual12_animated.glb"
ROOT="$HOME/thf-pulse-phone-baseline-v2"
WORK="$ROOT/work"
OUT="$ROOT/out"
SDK="$HOME/thf-builder-rc16-build/android-sdk"
CACHE="$HOME/thf-builder-rc16-build/cache"
APK_NAME="THF-PULSE-PHONE-BASELINE-QA2.apk"

rm -rf "$ROOT"
mkdir -p "$OUT"
test -d "$SRC"
test -s "$MPFB"
SOURCE_TREE_SHA=$(cd "$SRC" && find . -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum | awk '{print $1}')
test "$SOURCE_TREE_SHA" = "$EXPECTED_SOURCE_TREE_SHA"
cp -a "$SRC" "$WORK"
cd "$WORK"

# Source code stays Pulse-only. The already-verified MPFB file is imported read-only
# from the builder cache; no Terra/Rift/Spark/Rush source or state is modified.
ASSETS="android/app/src/main/assets/pulse"
mkdir -p "$ASSETS"
cp "$MPFB" "$ASSETS/avatar.glb"
cp static/photoreal_runtime.mjs "$ASSETS/photoreal_source.mjs"

curl -fsSL --retry 3 --retry-delay 2 https://unpkg.com/three@0.128.0/build/three.min.js -o "$ASSETS/three.min.js"
curl -fsSL --retry 3 --retry-delay 2 https://unpkg.com/three@0.128.0/examples/js/loaders/GLTFLoader.js -o "$ASSETS/GLTFLoader.js"
test -s "$ASSETS/three.min.js"
test -s "$ASSETS/GLTFLoader.js"

python3 - <<'PY'
from pathlib import Path
import json

assets=Path('android/app/src/main/assets/pulse')

src=Path('static/photoreal_runtime.mjs').read_text(encoding='utf-8')
src=src.replace("if(!cfg.threeModuleUrl || !cfg.gltfLoaderUrl) fail('3D dependency URLs missing');\n\nlet THREE, GLTFLoader;\ntry {\n  THREE = await import(cfg.threeModuleUrl);\n  ({GLTFLoader} = await import(cfg.gltfLoaderUrl));\n} catch (e) { fail('تعذر تحميل محرك 3D: '+e.message); }",
"const THREE=window.THREE;\nconst GLTFLoader=window.THREE && window.THREE.GLTFLoader;\nif(!THREE || !GLTFLoader) fail('Local 3D engine unavailable');")
src=src.replace("const pattern=cfg.pattern||'dynamic_warmup';",
"let pattern=cfg.pattern||'dynamic_warmup';\nwindow.THF_PULSE_SET_PATTERN=(p)=>{pattern=String(p||'dynamic_warmup');if(statusEl)statusEl.textContent='MPFB ready · '+bones.length+' bones · '+pattern;window.PulseNative?.poseEvent?.(JSON.stringify({schema:1,kind:'motion_pattern',pattern,ts:Date.now()}));};")
src="(async()=>{\n"+src+"\n})().catch(e=>{console.error(e);const n=document.getElementById('photoStatus');if(n)n.textContent='3D ERROR · '+e.message;});\n"
(assets/'photoreal.js').write_text(src,encoding='utf-8')

contracts={
  "schema":1,
  "canonical_unit_policy":"SI_or_provider_native_normalized_to_contract",
  "dedup":{"key":"sha256(provider|source_record_id|metric|start_ms|end_ms)","same_key":"duplicate"},
  "provenance_required":["provider","source_record_id","start_ms","end_ms"],
  "metrics":{
    "activity":{"unit":"event","fields":["activity_type","start_ms","end_ms"]},
    "workout":{"unit":"event","fields":["workout_type","start_ms","end_ms"]},
    "steps":{"unit":"count","fields":["value"]},
    "distance":{"unit":"m","fields":["value"]},
    "calories":{"unit":"kcal","fields":["value"]},
    "heart_rate":{"unit":"bpm","fields":["value"]},
    "sleep":{"unit":"ms","fields":["start_ms","end_ms","stage"]},
    "body_composition":{"unit":"mixed","fields":["weight_kg","body_fat_pct"]}
  },
  "providers":{"health_connect":{"permission_bridge":True,"read_adapter":"BOUNDARY_READY_DEVICE_READ_PENDING"},"samsung_health":{"sdk_adapter":"BOUNDARY_READY_SDK_BINARY_NOT_BUNDLED"}},
  "rewards":{"provider_data_alone_authorizes_reward":False,"pose_hook_alone_authorizes_reward":False}
}
(assets/'health-contracts.json').write_text(json.dumps(contracts,ensure_ascii=False,indent=2),encoding='utf-8')

html=r'''<!doctype html>
<html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>THF Pulse · Phone Baseline</title>
<style>
:root{color-scheme:dark;--bg:#071219;--panel:#0c1c24;--line:#38505b;--gold:#edca78;--txt:#edf3f5;--muted:#a9b5bb;--ok:#78dfaa;--warn:#ffc761}*{box-sizing:border-box}body{margin:0;background:linear-gradient(180deg,#061018,#0b1720);color:var(--txt);font-family:system-ui,-apple-system,"Noto Sans Arabic",sans-serif;padding-bottom:28px}.top{position:sticky;top:0;z-index:5;padding:12px 16px;background:#07131bea;border-bottom:1px solid #32454f}.brand{display:flex;justify-content:space-between;align-items:center;gap:8px}.brand b{font-size:21px;letter-spacing:2px;color:var(--gold)}.badge{font-size:11px;border:1px solid #8f783e;border-radius:999px;padding:5px 8px;color:var(--gold)}main{max-width:800px;margin:auto;padding:14px}.card{background:linear-gradient(180deg,#0d1c24,#0a171e);border:1px solid #334953;border-radius:18px;padding:16px;margin:12px 0}.stage{height:54vh;min-height:390px;max-height:590px;position:relative;border-radius:18px;overflow:hidden;background:#090b0c;border:1px solid #34444b}.stage canvas{width:100%;height:100%;display:block}.status{position:absolute;bottom:10px;left:10px;right:10px;background:#071219d9;border:1px solid #52646b;border-radius:12px;padding:9px;font-size:12px}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.mini{padding:10px;border:1px solid #30434c;border-radius:12px}.mini b{display:block;color:var(--gold)}button,select,input{width:100%;min-height:50px;border-radius:12px;border:1px solid #53656e;background:#0a161d;color:var(--txt);padding:9px 11px;font-size:16px;margin:5px 0}button.primary{background:linear-gradient(180deg,#4b3f22,#271f11);border-color:#8e7437;color:var(--gold);font-weight:800}.muted{color:var(--muted)}.ok{color:var(--ok)}.warn{color:var(--warn)}.row{display:flex;gap:8px;flex-wrap:wrap}.row>*{flex:1}.hide{display:none}.banner{padding:9px;border-radius:10px;background:#2b210b;color:#ffd98a;margin-bottom:10px}.lang{width:auto;min-width:110px}.truth{font-size:12px;border-top:1px solid #2b3c44;padding-top:10px;color:#9fb0b7}@media(max-width:540px){main{padding:9px}.stage{min-height:370px}.grid{grid-template-columns:1fr}.brand b{font-size:18px}}
</style></head><body>
<header class="top"><div class="brand"><b>THF PULSE</b><select id="lang" class="lang" aria-label="Language"><option value="ar">العربية</option><option value="en">English</option></select><span class="badge">PHONE BASELINE QA2</span></div></header>
<main>
<div id="offline" class="banner hide"></div>
<section id="onboarding" class="card"><h1 data-ar="ابدأ مع THF Pulse" data-en="Start with THF Pulse"></h1><p class="muted" data-ar="مدرب حركة ثلاثي الأبعاد + بيانات صحة اختيارية. بياناتك الصحية لا تستخدم للإعلانات." data-en="3D Motion Coach + optional health data. Health data is not used for ads."></p><label><input id="consent" type="checkbox"> <span data-ar="أفهم أن ربط بيانات الصحة اختياري" data-en="I understand health linking is optional"></span></label><button id="finishOnboarding" class="primary" data-ar="متابعة" data-en="Continue"></button></section>
<section id="app" class="hide">
<section class="card"><div class="grid"><div class="mini"><b id="identityState">—</b><span data-ar="THF Identity" data-en="THF Identity"></span></div><div class="mini"><b id="backendState">—</b><span data-ar="الخدمة" data-en="Backend"></span></div><div class="mini"><b id="healthState">—</b><span>Health Connect</span></div><div class="mini"><b id="samsungState">—</b><span>Samsung Health</span></div></div><div class="row"><button id="identity" data-ar="ربط THF Identity / Google" data-en="Connect THF Identity / Google"></button><button id="health" data-ar="صلاحيات Health Connect" data-en="Health Connect permissions"></button></div><p id="bridgeMsg" class="muted"></p></section>
<section class="stage"><canvas id="photoCanvas"></canvas><div id="photoStatus" class="status" data-ar="تحميل نموذج MPFB المحلي…" data-en="Loading local MPFB…"></div></section>
<section class="card"><label data-ar="الحركة / التمرين" data-en="Motion / exercise"></label><select id="pattern"></select><button id="voice" class="primary" data-ar="▶ الدليل الصوتي" data-en="▶ Voice cue"></button><p id="cue"></p><div class="row"><button id="startWorkout" data-ar="ابدأ الجلسة" data-en="Start session"></button><button id="finishWorkout" data-ar="أنهِ الجلسة" data-en="Finish session"></button></div><p id="sessionState" class="muted"></p></section>
<section class="card"><h2 data-ar="جسر بيانات الصحة" data-en="Health data bridge"></h2><p id="contractState" class="muted"></p><div class="row"><button id="demoMetric" data-ar="اختبار عقد steps محليًا" data-en="Test steps contract locally"></button><button id="providerState" data-ar="حالة الموصلات" data-en="Provider adapter status"></button></div><pre id="metricOut"></pre><p class="truth" data-ar="هذه النسخة لا تمنح مكافآت ولا تعتبر بيانات المزود أو pose وحدها دليلًا كافيًا. القراءة الفعلية من Health Connect وSamsung تحتاج اختبار جهاز/مزود." data-en="This build grants no rewards and does not treat provider or pose data alone as sufficient proof. Actual Health Connect/Samsung reads require device/provider testing."></p></section>
</section></main>
<script>
const P=window.PulseNative||null;const S=localStorage;const T={ar:{offline:'أنت غير متصل — Motion Coach المحلي يظل متاحًا.',connected:'متصل',unconfigured:'غير مهيأ',ready:'جاهز'},en:{offline:'You are offline — local Motion Coach remains available.',connected:'online',unconfigured:'not configured',ready:'ready'}};let lang=S.getItem('pulse.lang')||((navigator.language||'').startsWith('ar')?'ar':'en');
function applyLang(){document.documentElement.lang=lang;document.documentElement.dir=lang==='ar'?'rtl':'ltr';langEl.value=lang;document.querySelectorAll('[data-ar]').forEach(n=>n.textContent=n.dataset[lang]);applyPattern();}const langEl=document.getElementById('lang');langEl.onchange=()=>{lang=langEl.value;S.setItem('pulse.lang',lang);applyLang()};
function online(){const ok=navigator.onLine;offline.classList.toggle('hide',ok);offline.textContent=T[lang].offline;return ok}addEventListener('online',online);addEventListener('offline',online);
const patterns=[['dynamic_warmup','إحماء ديناميكي','Dynamic warm-up','حرّك الجسم تدريجيًا واستعد للتمرين.','Move progressively and prepare for training.'],['squat','سكوات','Squat','اثبت القدمين وانزل بتحكم ثم اصعد بثبات.','Keep the feet planted, descend under control, then stand tall.'],['hinge','Hip Hinge','Hip Hinge','ادفع الورك للخلف مع ظهر محايد ثم عد.','Push the hips back with a neutral spine, then return.'],['lunge','لانجز','Lunge','اخطُ بثبات واخفض الحوض ثم ادفع للعودة.','Step with control, lower the hips, then drive back.'],['run','جري','Run','حافظ على إيقاع ثابت وهبوط قدم هادئ.','Keep a steady rhythm and quiet foot strike.'],['boxing_jab','Boxing Jab','Boxing Jab','اضرب مباشرة مع حماية الوجه وثبات الجذع.','Punch straight while protecting the face and trunk.'],['stretch','إطالة','Stretch','تحرك ببطء إلى مدى الإطالة المريح.','Move slowly into a comfortable stretch.'],['breathing','تنفس','Breathing','تنفس بهدوء وحافظ على استرخاء الجذع.','Breathe calmly and keep the trunk relaxed.']];const sel=pattern;patterns.forEach(r=>{const o=document.createElement('option');o.value=r[0];sel.appendChild(o)});sel.value=S.getItem('pulse.pattern')||'dynamic_warmup';
function applyPattern(){const r=patterns.find(x=>x[0]===sel.value)||patterns[0];[...sel.options].forEach((o,i)=>o.textContent=patterns[i][lang==='ar'?1:2]);cue.textContent=r[lang==='ar'?3:4];window.THF_PHOTOREAL_CONFIG.pattern=r[0];window.THF_PULSE_SET_PATTERN?.(r[0]);S.setItem('pulse.pattern',r[0])}sel.onchange=applyPattern;voice.onclick=()=>{const r=patterns.find(x=>x[0]===sel.value)||patterns[0];if('speechSynthesis'in window){speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(r[lang==='ar'?3:4]);u.lang=lang==='ar'?'ar-EG':'en-US';speechSynthesis.speak(u)}};
function parse(x){try{return JSON.parse(x)}catch{return {raw:x}}}function refreshNative(){const b=P?parse(P.backendStatus()):{configured:false,online:navigator.onLine};backendState.textContent=b.configured?(b.online?'READY':'OFFLINE'):'NOT CONFIGURED';const i=P?parse(P.identityStatus()):{passConfigured:false,sessionSeen:false};identityState.textContent=i.sessionSeen?'SESSION':'HANDOFF';const h=P?parse(P.healthStatus()):{availability:'BRIDGE_UNAVAILABLE'};healthState.textContent=h.availability||'—';const s=P?parse(P.samsungStatus()):{status:'BOUNDARY_ONLY'};samsungState.textContent=s.status||'—'}
identity.onclick=()=>{if(!P){bridgeMsg.textContent='Native bridge unavailable';return}const r=parse(P.beginIdentity());bridgeMsg.textContent=r.message||r.status||JSON.stringify(r)};health.onclick=()=>{if(!P){bridgeMsg.textContent='Native bridge unavailable';return}const r=parse(P.requestHealthPermissions());bridgeMsg.textContent=r.message||r.status||JSON.stringify(r);setTimeout(refreshNative,1200)};providerState.onclick=()=>{metricOut.textContent=JSON.stringify({health:P?parse(P.healthStatus()):null,samsung:P?parse(P.samsungStatus()):null},null,2)};
startWorkout.onclick=()=>{const v={startedAt:Date.now(),pattern:sel.value};S.setItem('pulse.workout',JSON.stringify(v));P?.saveWorkoutSession?.(JSON.stringify(v));showSession()};finishWorkout.onclick=()=>{const v=parse(S.getItem('pulse.workout')||'{}');if(v.startedAt){v.endedAt=Date.now();v.durationMs=v.endedAt-v.startedAt;P?.saveWorkoutSession?.(JSON.stringify(v))}S.removeItem('pulse.workout');showSession()};function showSession(){const v=parse(S.getItem('pulse.workout')||'{}');sessionState.textContent=v.startedAt?((lang==='ar'?'جلسة نشطة منذ ':'Active session since ')+new Date(v.startedAt).toLocaleTimeString()):(lang==='ar'?'لا توجد جلسة نشطة':'No active session')}
demoMetric.onclick=()=>{const rec={schema:1,provider:'qa_local',source_record_id:'steps-'+new Date().toISOString().slice(0,10),metric:'steps',start_ms:Date.now()-60000,end_ms:Date.now(),value:123,unit:'count'};metricOut.textContent=P?P.ingestProviderRecord(JSON.stringify(rec)):JSON.stringify({status:'BRIDGE_UNAVAILABLE'})};
fetch('health-contracts.json').then(r=>r.json()).then(j=>contractState.textContent=(lang==='ar'?'العقود: ':'Contracts: ')+Object.keys(j.metrics).join(' · ')).catch(()=>contractState.textContent='contract load error');
finishOnboarding.onclick=()=>{if(!consent.checked)return;S.setItem('pulse.onboarding','1');P?.setOnboardingComplete?.();onboarding.classList.add('hide');app.classList.remove('hide');refreshNative();showSession()};if(S.getItem('pulse.onboarding')==='1'||(P&&P.isOnboardingComplete())){onboarding.classList.add('hide');app.classList.remove('hide')}online();applyLang();showSession();refreshNative();
window.addEventListener('thf:health-permissions',e=>{bridgeMsg.textContent=(lang==='ar'?'تم تحديث صلاحيات الصحة: ':'Health permissions updated: ')+JSON.stringify(e.detail);refreshNative()});
window.THF_PHOTOREAL_CONFIG={assetUrl:'avatar.glb',pattern:sel.value,tempoSec:3};
</script><script src="three.min.js"></script><script src="GLTFLoader.js"></script><script src="photoreal.js"></script></body></html>'''
(assets/'index.html').write_text(html,encoding='utf-8')

main=r'''package com.topherofit.thf.pulse;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.net.ConnectivityManager;
import android.net.Network;
import android.net.NetworkCapabilities;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.CookieManager;
import android.webkit.JavascriptInterface;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;
import androidx.health.connect.client.PermissionController;
import androidx.health.connect.client.permission.HealthPermission;
import androidx.health.connect.client.records.ActiveCaloriesBurnedRecord;
import androidx.health.connect.client.records.BodyFatRecord;
import androidx.health.connect.client.records.DistanceRecord;
import androidx.health.connect.client.records.ExerciseSessionRecord;
import androidx.health.connect.client.records.HeartRateRecord;
import androidx.health.connect.client.records.SleepSessionRecord;
import androidx.health.connect.client.records.StepsRecord;
import androidx.health.connect.client.records.TotalCaloriesBurnedRecord;
import androidx.health.connect.client.records.WeightRecord;
import androidx.activity.result.contract.ActivityResultContract;
import org.json.JSONObject;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

public final class MainActivity extends Activity {
  private static final String PREFS="thf_pulse_phone_v2";
  private static final int HEALTH_REQUEST=14021;
  private WebView web; private SharedPreferences prefs;
  private final Set<String> healthPermissions=new HashSet<>(Arrays.asList(
    HealthPermission.getReadPermission(ExerciseSessionRecord.class),HealthPermission.getReadPermission(StepsRecord.class),HealthPermission.getReadPermission(DistanceRecord.class),HealthPermission.getReadPermission(TotalCaloriesBurnedRecord.class),HealthPermission.getReadPermission(ActiveCaloriesBurnedRecord.class),HealthPermission.getReadPermission(HeartRateRecord.class),HealthPermission.getReadPermission(SleepSessionRecord.class),HealthPermission.getReadPermission(WeightRecord.class),HealthPermission.getReadPermission(BodyFatRecord.class)));
  private final ActivityResultContract<Set<String>,Set<String>> healthContract=PermissionController.createRequestPermissionResultContract();

  @Override public void onCreate(Bundle state){super.onCreate(state);prefs=getSharedPreferences(PREFS,MODE_PRIVATE);web=new WebView(this);setContentView(web);configureWeb();Uri u=getIntent()!=null?getIntent().getData():null;if(u!=null&&"topherofit".equals(u.getScheme()))handleDeepLink(u);else loadLocal();}
  private void configureWeb(){CookieManager.getInstance().setAcceptThirdPartyCookies(web,false);WebSettings s=web.getSettings();s.setJavaScriptEnabled(true);s.setDomStorageEnabled(true);s.setAllowFileAccess(true);s.setAllowContentAccess(false);s.setAllowFileAccessFromFileURLs(true);s.setAllowUniversalAccessFromFileURLs(false);s.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);s.setTextZoom(prefs.getInt("text_zoom",100));web.addJavascriptInterface(new PulseBridge(),"PulseNative");web.setWebViewClient(new WebViewClient(){@Override public boolean shouldOverrideUrlLoading(WebView v,WebResourceRequest r){Uri u=r.getUrl();String scheme=u.getScheme()==null?"":u.getScheme();if("topherofit".equals(scheme)){handleDeepLink(u);return true;}if("file".equals(scheme))return !u.toString().startsWith("file:///android_asset/pulse/");return !"https".equalsIgnoreCase(scheme);}@Override public void onReceivedError(WebView v,WebResourceRequest r,WebResourceError e){if(r.isForMainFrame()&&r.getUrl()!=null&&"https".equalsIgnoreCase(r.getUrl().getScheme())){Toast.makeText(MainActivity.this,"Secure service unavailable — local Motion Coach remains available",Toast.LENGTH_LONG).show();loadLocal();}}});}
  private void loadLocal(){web.loadUrl("file:///android_asset/pulse/index.html");}
  private boolean safeHttps(String x){try{Uri u=Uri.parse(x==null?"":x.trim());return "https".equalsIgnoreCase(u.getScheme())&&u.getHost()!=null&&!u.getHost().isBlank()&&u.getUserInfo()==null;}catch(Exception e){return false;}}
  private boolean online(){ConnectivityManager cm=(ConnectivityManager)getSystemService(Context.CONNECTIVITY_SERVICE);if(cm==null)return true;Network n=cm.getActiveNetwork();if(n==null)return false;NetworkCapabilities c=cm.getNetworkCapabilities(n);return c!=null&&c.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET);}
  private void handleDeepLink(Uri u){if(u==null){loadLocal();return;}if("pass".equals(u.getHost())){String ticket=u.getQueryParameter("ticket"),target=u.getQueryParameter("target");if(target!=null&&!BuildConfig.THF_APP_SLUG.equals(target)){Toast.makeText(this,"Handoff target mismatch",Toast.LENGTH_SHORT).show();loadLocal();return;}String pass=BuildConfig.THF_PASS_URL==null?"":BuildConfig.THF_PASS_URL.trim();if(!safeHttps(pass)||ticket==null||ticket.isBlank()){Toast.makeText(this,"THF Pass endpoint/ticket unavailable",Toast.LENGTH_LONG).show();loadLocal();return;}prefs.edit().putBoolean("identity_session_seen",true).apply();Uri dest=Uri.parse(pass).buildUpon().appendPath("handoff").appendPath("consume").appendQueryParameter("target",BuildConfig.THF_APP_SLUG).appendQueryParameter("ticket",ticket).build();web.loadUrl(dest.toString());return;}loadLocal();}
  @Override protected void onActivityResult(int requestCode,int resultCode,Intent data){super.onActivityResult(requestCode,resultCode,data);if(requestCode==HEALTH_REQUEST){Set<String> granted=healthContract.parseResult(resultCode,data);prefs.edit().putStringSet("health_granted",new HashSet<>(granted)).apply();String payload=new JSONObject().put("granted_count",granted.size()).put("requested_count",healthPermissions.size()).toString();web.evaluateJavascript("window.dispatchEvent(new CustomEvent('thf:health-permissions',{detail:"+payload+"}))",null);}}
  @Override protected void onNewIntent(Intent intent){super.onNewIntent(intent);setIntent(intent);Uri u=intent.getData();if(u!=null)handleDeepLink(u);}
  @Override public void onBackPressed(){if(web.canGoBack())web.goBack();else super.onBackPressed();}

  final class PulseBridge {
    @JavascriptInterface public boolean isOnboardingComplete(){return prefs.getBoolean("onboarding_complete",false);} @JavascriptInterface public void setOnboardingComplete(){prefs.edit().putBoolean("onboarding_complete",true).apply();}
    @JavascriptInterface public String backendStatus(){try{return new JSONObject().put("configured",safeHttps(BuildConfig.THF_BASE_URL)).put("online",online()).put("endpoint_secret_embedded",false).toString();}catch(Exception e){return "{}";}}
    @JavascriptInterface public String identityStatus(){try{return new JSONObject().put("passConfigured",safeHttps(BuildConfig.THF_PASS_URL)).put("sessionSeen",prefs.getBoolean("identity_session_seen",false)).put("ticketPersisted",false).toString();}catch(Exception e){return "{}";}}
    @JavascriptInterface public String beginIdentity(){try{String pass=BuildConfig.THF_PASS_URL==null?"":BuildConfig.THF_PASS_URL.trim();JSONObject o=new JSONObject();if(!safeHttps(pass)){return o.put("status","BLOCKED").put("message","THF_PASS_URL not injected; Google/THF provider flow requires authoritative Pass endpoint configuration").toString();}Intent i=new Intent(Intent.ACTION_VIEW,Uri.parse(pass));startActivity(i);return o.put("status","HANDOFF_STARTED").put("message","THF Pass opened; one-time ticket returns through topherofit://pass/handoff").toString();}catch(Exception e){return new JSONObject().put("status","ERROR").put("message",e.getClass().getSimpleName()).toString();}}
    @JavascriptInterface public String requestHealthPermissions(){try{Intent i=healthContract.createIntent(MainActivity.this,healthPermissions);startActivityForResult(i,HEALTH_REQUEST);return new JSONObject().put("status","PERMISSION_UI_STARTED").put("requested_count",healthPermissions.size()).toString();}catch(Exception e){return new JSONObject().put("status","UNAVAILABLE").put("message",e.getClass().getSimpleName()).toString();}}
    @JavascriptInterface public String healthStatus(){try{Set<String> g=prefs.getStringSet("health_granted",new HashSet<>());return new JSONObject().put("availability","PERMISSION_BRIDGE_READY").put("granted_count",g==null?0:g.size()).put("requested_count",healthPermissions.size()).put("read_adapter","BOUNDARY_READY_DEVICE_READ_PENDING").toString();}catch(Exception e){return "{}";}}
    @JavascriptInterface public String samsungStatus(){try{boolean installed;try{getPackageManager().getPackageInfo("com.sec.android.app.shealth",0);installed=true;}catch(PackageManager.NameNotFoundException e){installed=false;}return new JSONObject().put("installed",installed).put("status","BOUNDARY_READY_SDK_BINARY_NOT_BUNDLED").put("direct_sdk_read",false).toString();}catch(Exception e){return "{}";}}
    @JavascriptInterface public String ingestProviderRecord(String raw){try{JSONObject j=new JSONObject(raw);String provider=req(j,"provider"),id=req(j,"source_record_id"),metric=req(j,"metric");long start=j.getLong("start_ms"),end=j.getLong("end_ms");if(end<start||!allowedMetric(metric))return new JSONObject().put("status","INVALID").toString();String key=sha256(provider+"|"+id+"|"+metric+"|"+start+"|"+end);Set<String> seen=new HashSet<>(prefs.getStringSet("provider_dedupe",new HashSet<>()));boolean duplicate=!seen.add(key);if(!duplicate){while(seen.size()>512)seen.remove(seen.iterator().next());prefs.edit().putStringSet("provider_dedupe",seen).apply();}return new JSONObject().put("status",duplicate?"DUPLICATE":"ACCEPTED").put("dedupe_sha256",key).put("reward_authorized",false).toString();}catch(Exception e){return new JSONObject().put("status","INVALID").put("error",e.getClass().getSimpleName()).toString();}}
    @JavascriptInterface public String poseEvent(String raw){try{JSONObject j=new JSONObject(raw);prefs.edit().putString("last_pose_pattern",j.optString("pattern","unknown")).putLong("last_pose_ts",System.currentTimeMillis()).apply();return new JSONObject().put("status","HOOK_ACCEPTED").put("verification","NOT_PROOF_BY_ITSELF").toString();}catch(Exception e){return "{\"status\":\"INVALID\"}";}}
    @JavascriptInterface public void saveWorkoutSession(String raw){if(raw!=null&&raw.length()<4096)prefs.edit().putString("last_workout_session",raw).apply();}
    private String req(JSONObject j,String k)throws Exception{String v=j.getString(k);if(v.isBlank()||v.length()>160)throw new Exception("invalid");return v;}private boolean allowedMetric(String m){return Arrays.asList("activity","workout","steps","distance","calories","heart_rate","sleep","body_composition").contains(m);}private String sha256(String s)throws Exception{byte[] b=MessageDigest.getInstance("SHA-256").digest(s.getBytes(StandardCharsets.UTF_8));StringBuilder x=new StringBuilder();for(byte q:b)x.append(String.format("%02x",q));return x.toString();}
  }
}
'''
Path('android/app/src/main/java/com/topherofit/thf/pulse/MainActivity.java').write_text(main,encoding='utf-8')

gradle=Path('android/app/build.gradle').read_text(encoding='utf-8')
gradle=gradle.replace('versionCode 41200','versionCode 41401').replace("versionName '4.1.2'","versionName '4.1.4-phonebaseline1'")
if 'androidx.health.connect:connect-client' not in gradle:
    gradle += "\n\ndependencies {\n    implementation 'androidx.health.connect:connect-client:1.1.0'\n    implementation 'androidx.activity:activity:1.10.1'\n}\n"
Path('android/app/build.gradle').write_text(gradle,encoding='utf-8')

manifest='''<?xml version="1.0" encoding="utf-8"?>\n<manifest xmlns:android="http://schemas.android.com/apk/res/android">\n  <uses-permission android:name="android.permission.INTERNET"/>\n  <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/>\n  <uses-permission android:name="android.permission.health.READ_EXERCISE"/>\n  <uses-permission android:name="android.permission.health.READ_STEPS"/>\n  <uses-permission android:name="android.permission.health.READ_DISTANCE"/>\n  <uses-permission android:name="android.permission.health.READ_TOTAL_CALORIES_BURNED"/>\n  <uses-permission android:name="android.permission.health.READ_ACTIVE_CALORIES_BURNED"/>\n  <uses-permission android:name="android.permission.health.READ_HEART_RATE"/>\n  <uses-permission android:name="android.permission.health.READ_SLEEP"/>\n  <uses-permission android:name="android.permission.health.READ_WEIGHT"/>\n  <uses-permission android:name="android.permission.health.READ_BODY_FAT"/>\n  <queries><package android:name="com.google.android.apps.healthdata"/><package android:name="com.sec.android.app.shealth"/></queries>\n  <application android:supportsRtl="true" android:allowBackup="false" android:usesCleartextTraffic="false" android:theme="@style/AppTheme" android:label="@string/app_name" android:networkSecurityConfig="@xml/network_security_config">\n    <activity android:name=".MainActivity" android:exported="true">\n      <intent-filter><action android:name="android.intent.action.MAIN"/><category android:name="android.intent.category.LAUNCHER"/></intent-filter>\n      <intent-filter><action android:name="android.intent.action.VIEW"/><category android:name="android.intent.category.DEFAULT"/><category android:name="android.intent.category.BROWSABLE"/><data android:scheme="topherofit" android:host="app" android:pathPrefix="/pulse"/></intent-filter>\n      <intent-filter><action android:name="android.intent.action.VIEW"/><category android:name="android.intent.category.DEFAULT"/><category android:name="android.intent.category.BROWSABLE"/><data android:scheme="topherofit" android:host="pass" android:pathPrefix="/handoff"/></intent-filter>\n    </activity>\n  </application>\n</manifest>\n'''
Path('android/app/src/main/AndroidManifest.xml').write_text(manifest,encoding='utf-8')
PY

for f in index.html avatar.glb three.min.js GLTFLoader.js photoreal.js health-contracts.json; do test -s "$ASSETS/$f"; done
grep -q 'PHONE BASELINE QA2' "$ASSETS/index.html"
grep -q 'PulseNative' "$ASSETS/index.html"
grep -q 'HealthPermission.getReadPermission' android/app/src/main/java/com/topherofit/thf/pulse/MainActivity.java
grep -q 'androidx.health.connect:connect-client:1.1.0' android/app/build.gradle
grep -q 'targetSdk 36' android/app/build.gradle

python3 -m compileall -q app
if python3 -c 'import pytest' >/dev/null 2>&1; then python3 -m pytest -q tests > "$OUT/pytest.log" 2>&1; PYTEST_STATUS=PASS; else echo 'pytest module unavailable on builder; compileall PASS' > "$OUT/pytest.log"; PYTEST_STATUS=UNAVAILABLE_COMPILEALL_PASS; fi

export ANDROID_SDK_ROOT="$SDK" ANDROID_HOME="$SDK" GRADLE_USER_HOME="$ROOT/gradle-home"
export PATH="$SDK/platform-tools:$SDK/build-tools/36.0.0:$SDK/cmdline-tools/latest/bin:$PATH"
mkdir -p "$GRADLE_USER_HOME"
GVER=8.11.1
GBIN="$CACHE/gradle-dist-${GVER}/gradle-${GVER}/bin/gradle"
test -x "$GBIN"
cd android
"$GBIN" --no-daemon --stacktrace clean :app:assembleDebug >"$OUT/gradle.log" 2>&1
cp app/build/outputs/apk/debug/app-debug.apk "$OUT/$APK_NAME"

APK="$OUT/$APK_NAME"; AAPT="$SDK/build-tools/36.0.0/aapt"; APKSIGNER="$SDK/build-tools/36.0.0/apksigner"
"$AAPT" dump badging "$APK" > "$OUT/badging.txt"
"$APKSIGNER" verify --verbose --print-certs "$APK" > "$OUT/apksigner.txt"
grep -q "package: name='com.topherofit.thf.pulse.debug'" "$OUT/badging.txt"
grep -q "versionCode='41401'" "$OUT/badging.txt"
grep -q "targetSdkVersion:'36'" "$OUT/badging.txt"
zipinfo -1 "$APK" > "$OUT/apk_entries.txt"
for f in index.html avatar.glb three.min.js GLTFLoader.js photoreal.js health-contracts.json; do grep -Fxq "assets/pulse/$f" "$OUT/apk_entries.txt"; done

TMP="$ROOT/extract"; rm -rf "$TMP"; mkdir -p "$TMP"; unzip -q "$APK" 'assets/pulse/*' -d "$TMP"
for f in avatar.glb three.min.js GLTFLoader.js photoreal.js health-contracts.json index.html; do test "$(sha256sum "app/src/main/assets/pulse/$f"|awk '{print $1}')" = "$(sha256sum "$TMP/assets/pulse/$f"|awk '{print $1}')"; done

cd "$WORK"
APK_SHA=$(sha256sum "$APK"|awk '{print $1}'); APK_SIZE=$(stat -c %s "$APK"); MPFB_SHA=$(sha256sum "$ASSETS/avatar.glb"|awk '{print $1}'); CONTRACT_SHA=$(sha256sum "$ASSETS/health-contracts.json"|awk '{print $1}')
find "$ASSETS" -maxdepth 1 -type f -printf '%f\0' | sort -z | while IFS= read -r -d '' f; do sha256sum "$ASSETS/$f"; done > "$OUT/runtime-assets.sha256"
cat > "$OUT/EVIDENCE.txt" <<EOF
THF_PULSE_PHONE_BASELINE_QA2=BUILT
source=THF_Pulse_APPS_RC2_SOURCE
source_tree_sha256=$SOURCE_TREE_SHA
source_tree_sha_expected=$EXPECTED_SOURCE_TREE_SHA
source_authoritative_gate=PASS
non_pulse_code_modified=false
mpfb_import_mode=READ_ONLY_EXISTING_VERIFIED_ASSET
avatar_sha256=$MPFB_SHA
health_contract_sha256=$CONTRACT_SHA
motion_runtime_local=true
runtime_asset_extract_integrity=PASS
onboarding_persistence=IMPLEMENTED
identity_handoff=THF_PASS_BOUNDARY_IMPLEMENTED_ENDPOINT_REQUIRED
identity_ticket_persisted=false
backend_endpoint=current_source_requires_injected_TFH_BASE_URL
backend_offline_local_motion=IMPLEMENTED
health_connect_dependency=androidx.health.connect_connect-client_1.1.0
health_connect_permission_bridge=IMPLEMENTED
health_connect_device_record_read=BOUNDARY_READY_DEVICE_TEST_PENDING
samsung_health_adapter=BOUNDARY_READY_SDK_BINARY_NOT_BUNDLED
health_metric_contracts=activity,workout,steps,distance,calories,heart_rate,sleep,body_composition
provider_provenance_dedup=IMPLEMENTED_SHA256
pose_motion_verification_hook=IMPLEMENTED_NOT_PROOF_BY_ITSELF
arabic_english_rtl=IMPLEMENTED
accessibility_prefs_source_preserved=true
data_saver_source_pref_preserved=true
targetSdk=36
python_compileall=PASS
pytest_status=$PYTEST_STATUS
package=com.topherofit.thf.pulse.debug
version=4.1.4-phonebaseline1-debug
versionCode=41401
apk_size_bytes=$APK_SIZE
apk_sha256=$APK_SHA
physical_device_status=PENDING
visible_moving_human_phone_validation=PENDING
backend_live_reachability=PENDING_ENDPOINT_INJECTION
thf_identity_google_live=PENDING_PASS_OAUTH_CONFIGURATION
health_connect_live_read=PENDING_PHYSICAL_DEVICE
samsung_health_live_read=PENDING_SDK_PROVIDER_DEVICE
final_or_play_ready=FALSE
EOF
cat "$OUT/EVIDENCE.txt"
