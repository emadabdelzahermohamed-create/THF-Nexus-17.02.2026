import importlib.util
import sqlite3
import sys
from pathlib import Path
import pytest

P=Path(__file__).parents[1]/"notification_lifecycle.py"
spec=importlib.util.spec_from_file_location("notification_lifecycle",P)
m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m)

class Vault:
    def __init__(self): self.data={}; self.fail_put=False
    def put(self,k,v):
        if self.fail_put: raise RuntimeError("vault put failed")
        self.data[k]=v
    def get(self,k): return self.data[k]
    def delete(self,k): self.data.pop(k,None)

def reg():
    v=Vault(); r=m.NotificationTokenRegistry(sqlite3.connect(":memory:"),v); return r,v

def register(r, subject="u1", session_id="s1", package="com.topherofit.thf.pulse", token="provider-token-123456"):
    return r.register(subject=subject,session_id=session_id,package=package,provider="fcm",raw_token=token)

def test_register_is_session_bound_and_raw_token_stays_out_of_db():
    r,v=reg(); raw="provider-token-123456"; x=register(r,token=raw)
    assert x.active and x.session_id=="s1" and len(x.fingerprint)==64
    assert v.get(x.token_id)==raw
    dump=" ".join(str(z) for z in r.db.execute("select * from notification_tokens").fetchone())
    assert raw not in dump

def test_same_user_package_provider_token_in_two_sessions_gets_distinct_registration():
    r,v=reg(); raw="provider-token-123456"
    a=register(r,session_id="s1",token=raw); b=register(r,session_id="s2",token=raw)
    assert a.token_id != b.token_id
    assert r.get(a.token_id,subject="u1",session_id="s1").active
    assert r.get(b.token_id,subject="u1",session_id="s2").active
    with pytest.raises(PermissionError): r.get(a.token_id,subject="u1",session_id="s2")

def test_rotation_is_session_scoped_and_failure_safe():
    r,v=reg(); p="com.topherofit.thf.echo"
    old=register(r,session_id="s1",package=p,token="old-token-123456")
    with pytest.raises(PermissionError):
        r.rotate(subject="u1",session_id="s2",package=p,provider="fcm",old_token_id=old.token_id,new_raw_token="new-token-123456")
    v.fail_put=True
    with pytest.raises(RuntimeError):
        r.rotate(subject="u1",session_id="s1",package=p,provider="fcm",old_token_id=old.token_id,new_raw_token="new-token-123456")
    assert r.get(old.token_id,subject="u1",session_id="s1").active
    assert v.data=={old.token_id:"old-token-123456"}
    v.fail_put=False
    new=r.rotate(subject="u1",session_id="s1",package=p,provider="fcm",old_token_id=old.token_id,new_raw_token="new-token-123456")
    assert new.generation==2 and new.active
    assert not r.get(old.token_id,subject="u1",session_id="s1").active

def test_logout_revokes_only_current_session_not_other_device_session():
    r,v=reg(); p="com.topherofit.thf.pulse"
    a=register(r,session_id="phone-a",package=p,token="token-phone-a-123")
    b=register(r,session_id="phone-b",package=p,token="token-phone-b-123")
    assert r.revoke_logout(subject="u1",session_id="phone-a",package=p)==1
    assert not r.get(a.token_id,subject="u1",session_id="phone-a").active
    assert r.get(b.token_id,subject="u1",session_id="phone-b").active
    assert a.token_id not in v.data and b.token_id in v.data

def test_cross_subject_and_cross_session_revoke_fail_closed():
    r,_=reg(); x=register(r)
    with pytest.raises(PermissionError): r.revoke(token_id=x.token_id,subject="u2",session_id="s1")
    with pytest.raises(PermissionError): r.revoke(token_id=x.token_id,subject="u1",session_id="s2")

def test_legacy_schema_rebuilds_rows_fail_closed_and_removes_old_unique_constraint():
    db=sqlite3.connect(":memory:")
    db.execute("CREATE TABLE notification_tokens(token_id TEXT PRIMARY KEY,subject TEXT NOT NULL,package TEXT NOT NULL,provider TEXT NOT NULL,fingerprint TEXT NOT NULL,generation INTEGER NOT NULL,active INTEGER NOT NULL,created_at INTEGER NOT NULL,updated_at INTEGER NOT NULL,UNIQUE(subject,package,provider,fingerprint))")
    db.execute("INSERT INTO notification_tokens VALUES('legacy','u1','com.topherofit.thf.pulse','fcm','fp',1,1,1,1)")
    v=Vault(); r=m.NotificationTokenRegistry(db,v)
    row=db.execute("SELECT session_id FROM notification_tokens WHERE token_id='legacy'").fetchone()
    assert row[0]==m.LEGACY_UNBOUND_SESSION
    with pytest.raises(PermissionError): r.get("legacy",subject="u1",session_id="s1")
    raw="same-provider-token-123456"
    a=register(r,session_id="s1",token=raw); b=register(r,session_id="s2",token=raw)
    assert a.token_id != b.token_id
    assert r.get(a.token_id,subject="u1",session_id="s1").active
    assert r.get(b.token_id,subject="u1",session_id="s2").active
    assert db.execute("SELECT COUNT(*) FROM notification_tokens").fetchone()[0]==3

def test_invalid_session_package_and_provider_fail_closed():
    r,_=reg()
    with pytest.raises(PermissionError): register(r,session_id="")
    with pytest.raises(PermissionError): register(r,session_id=m.LEGACY_UNBOUND_SESSION)
    with pytest.raises(PermissionError): register(r,package="com.evil.fake")
    with pytest.raises(ValueError): r.register(subject="u1",session_id="s1",package="com.topherofit.thf.pulse",provider="bad",raw_token="abcdefgh1234")

def test_provider_delivery_is_intentionally_not_implemented():
    assert not hasattr(m.NotificationTokenRegistry,"send")
