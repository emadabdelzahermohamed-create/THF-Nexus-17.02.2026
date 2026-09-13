import importlib.util
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('audit_identity', HERE/'audit_identity_handoff_contract.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)


def write_runtime(root: Path, text: str):
    p=root/'android/app/src/main/java/com/topherofit/Test.kt'
    p.parent.mkdir(parents=True,exist_ok=True); p.write_text(text)


def test_complete_contract_surface(tmp_path):
    write_runtime(tmp_path, '''
      val passUrl = BuildConfig.THF_PASS_URL
      fun login(){ request("/auth/login", headers=mapOf("Authorization" to "Bearer x")) }
      fun session(){ val accessToken="x"; val refreshToken="y"; if (status==401) refreshToken() }
      fun logout(){ clearSession(); revoke() }
      val prefs = EncryptedSharedPreferences.create("session", MasterKey.Builder(ctx).build(), ctx,
          EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
          EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM)
      fun send(){ startActivity(Intent(Intent.ACTION_VIEW, uri)) }
      fun receive(){ val d=getIntent().data }
    ''')
    out=mod.audit(tmp_path)
    assert out['minimum_contract_surfaces']['session_lifecycle_surface']
    assert out['minimum_contract_surfaces']['secure_storage_surface']
    assert out['minimum_contract_surfaces']['federation_binding_surface']
    assert out['minimum_contract_surfaces']['cross_app_handoff_surface']
    assert out['contract_surface_complete']


def test_sensitive_query_and_cleartext_fail_surface(tmp_path):
    write_runtime(tmp_path, 'val x="http://api.example.test/path?access_token=abc"')
    out=mod.audit(tmp_path)
    assert not out['minimum_contract_surfaces']['no_sensitive_query_token_pattern']
    assert not out['minimum_contract_surfaces']['no_cleartext_runtime_endpoint']
    assert not out['contract_surface_complete']


def test_docs_do_not_create_runtime_evidence(tmp_path):
    p=tmp_path/'docs/identity.md'; p.parent.mkdir(parents=True); p.write_text('THF_PASS_URL logout refresh token handoff')
    out=mod.audit(tmp_path)
    assert out['runtime_files_scanned']==0
    assert not out['contract_surface_complete']
