from pathlib import Path
import importlib.util,tempfile
P=Path(__file__).with_name('audit_app_runtime_contract_v2.py')
s=importlib.util.spec_from_file_location('m',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

def wr(root,text):
 p=Path(root)/'android/app/src/main/java/x/A.kt';p.parent.mkdir(parents=True);p.write_text(text);return Path(root)

def test_complete_contract():
 with tempfile.TemporaryDirectory() as d:
  root=wr(d,"""const val THF_BASE_URL=\"https://api.thf.example.invalid\" // replaced below
  fun login(){ authenticate(); accessToken=\"x\"; refreshToken=\"y\"; if(code==401) refreshSession() }
  fun logout(){ revokeToken(); clearSession() }
  val cm=ConnectivityManager; val ds=DataStore; startActivity(); getIntent();
  val nc=NotificationChannel(\"x\",\"x\",3); val fm=FirebaseMessaging.getInstance(); onMessageReceived();
  val rtl=layoutDirection; val a=contentDescription
  """.replace('https://api.thf.example.invalid','https://api.topherofit.test'))
  r=m.audit(root)
  assert r['critical_source_contract']['logout_surface']
  assert r['critical_source_contract']['revocation_surface']
  assert r['notification_source_contract_complete']
  assert not r['readiness']['final_or_play_ready']

def test_fail_closed_placeholders_and_fake_offline():
 with tempfile.TemporaryDirectory() as d:
  root=wr(d,'const val BASE_URL="https://example.com"\n// offline wallet commit success')
  r=m.audit(root)
  assert not r['critical_source_contract']['no_placeholder_runtime_url']
  assert not r['critical_source_contract']['no_fake_offline_authority_pattern']
  assert not r['critical_source_contract_complete']

def test_cleartext_rejected():
 with tempfile.TemporaryDirectory() as d:
  r=m.audit(wr(d,'val u="http://api.test.invalid"'))
  assert not r['critical_source_contract']['no_cleartext_runtime_transport']
