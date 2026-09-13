#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,re
from pathlib import Path
TEXT={'.java','.kt','.kts','.xml','.gradle','.properties','.json','.py','.js','.ts','.tsx'}
ROOTS=('android/app/src/main','app','appsrc')
RX={
'auth_login':r'(?i)(/auth\b|/login\b|\blogin\s*\(|authenticate|Authorization\s*[:=]|Bearer)',
'session_store':r'(?i)(access.?token|refresh.?token|session|EncryptedSharedPreferences|AndroidKeyStore|KeyStore)',
'expiry':r'(?i)(expires?|expiry|401|unauthori[sz]ed)',
'refresh':r'(?i)(refresh.?token|token.?refresh|refreshSession|renewSession)',
'logout':r'(?i)(\blogout\b|sign.?out|clear.?session|clearCredentials)',
'revoke':r'(?i)(\brevoke\b|revokeToken|invalidate.?token|delete.?token)',
'backend_config':r'(?i)(THF_BASE_URL|BASE_URL|API_URL|THF_PASS_URL|PASS_URL|WSS_URL|BuildConfig\.[A-Z_]*(?:URL|HOST))',
'notification_register':r'(?i)(FirebaseMessaging|registerForRemoteNotifications|push.?token|notification.?token|subscribeToTopic)',
'notification_channel':r'(?i)(NotificationChannel|NotificationManager|createNotificationChannel)',
'notification_receive':r'(?i)(onMessageReceived|FirebaseMessagingService|BroadcastReceiver|PendingIntent)',
'network_state':r'(?i)(ConnectivityManager|NetworkCapabilities|isOnline|network.?available|Data.?Saver|restrictBackground)',
'offline_store':r'(?i)(RoomDatabase|SQLite|SharedPreferences|DataStore|cache|offline)',
'handoff_send':r'(?i)(startActivity|ACTION_VIEW|deep.?link|app.?link|handoff)',
'handoff_receive':r'(?i)(onNewIntent|getIntent\s*\(|intent\.data|getData\s*\(|intent-filter|scheme=|host=)',
'rtl':r'(?i)(supportsRtl|layoutDirection|startToEnd|endToStart|locale)',
'accessibility':r'(?i)(contentDescription|importantForAccessibility|accessibility|TalkBack)',
'admin':r'(?i)(admin|control.?panel|moderation|operator)',
}
P={k:re.compile(v) for k,v in RX.items()}
URL=re.compile(r'(?i)\b(?:https|wss)://[^\s\"\'<>)]*')
BADURL=re.compile(r'(?i)(example\.com|localhost|127\.0\.0\.1|0\.0\.0\.0|placeholder|changeme|your[-_.]?(?:api|host|url))')
CLEAR=re.compile(r'(?i)\b(?:http|ws)://(?!schemas\.android\.com)')
# Fail closed only when offline and authoritative state terms are coupled to a success/commit/sync
# signal on the same logical line. Cross-line matches caused false positives where an offline_fallback
# requirement was followed later by unrelated DB commit code.
FAKE_OFFLINE=re.compile(r'(?i)(?:offline[^\n]{0,180}(?:rank|leaderboard|wallet|token|econom|social)[^\n]{0,180}(?:success|commit|sync)|(?:rank|leaderboard|wallet|token|econom|social)[^\n]{0,180}offline[^\n]{0,180}(?:success|commit|sync))')

def files(root):
 seen=set()
 for rel in ROOTS:
  b=root/rel
  if not b.exists(): continue
  for p in b.rglob('*'):
   if p.is_file() and p.suffix.lower() in TEXT and p.resolve() not in seen:
    seen.add(p.resolve()); yield p

def audit(root):
 hits={k:0 for k in P}; samples={k:[] for k in P}; urls=set(); clear=[]; fake=[]; n=0
 for p in files(root):
  n+=1; rel=p.relative_to(root).as_posix(); t=p.read_text(errors='ignore')
  for k,rx in P.items():
   c=len(rx.findall(t)); hits[k]+=c
   if c and len(samples[k])<6:samples[k].append(rel)
  for u in URL.findall(t): urls.add(u.rstrip('.,;'))
  if CLEAR.search(t): clear.append(rel)
  if FAKE_OFFLINE.search(t): fake.append(rel)
 placeholders=sorted(u for u in urls if BADURL.search(u))
 critical={
  'auth_login_surface':hits['auth_login']>0,
  'session_persistence_surface':hits['session_store']>0,
  'expiry_surface':hits['expiry']>0,
  'refresh_surface':hits['refresh']>0,
  'logout_surface':hits['logout']>0,
  'revocation_surface':hits['revoke']>0,
  'backend_config_surface':hits['backend_config']>0 or bool(urls),
  'no_placeholder_runtime_url':not placeholders,
  'no_cleartext_runtime_transport':not clear,
  'network_state_surface':hits['network_state']>0,
  'offline_local_surface':hits['offline_store']>0,
  'no_fake_offline_authority_pattern':not fake,
  'handoff_surface':hits['handoff_send']>0 and hits['handoff_receive']>0,
 }
 notifications={
  'registration':hits['notification_register']>0,
  'channel':hits['notification_channel']>0,
  'receive_or_action':hits['notification_receive']>0,
 }
 return {'schema':2,'root':str(root),'runtime_files_scanned':n,'hits':hits,'samples':samples,
 'runtime_https_wss_urls':sorted(urls),'placeholder_urls':placeholders,'cleartext_files':sorted(set(clear)),
 'fake_offline_authority_files':sorted(set(fake)),'critical_source_contract':critical,
 'critical_source_contract_complete':all(critical.values()),'notifications':notifications,
 'notification_source_contract_complete':all(notifications.values()),
 'readiness':{'source_contract_only':True,'backend_health_auth_runtime_required':True,'physical_phone_required':True,'final_or_play_ready':False}}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--json-out',type=Path);ns=ap.parse_args();d=audit(ns.root);s=json.dumps(d,indent=2);print(s)
 if ns.json_out:ns.json_out.write_text(s+'\n')
if __name__=='__main__':main()
