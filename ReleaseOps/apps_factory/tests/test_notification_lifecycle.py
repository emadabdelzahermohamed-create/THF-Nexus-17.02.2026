import importlib.util
import sqlite3
import sys
from pathlib import Path
import pytest

P=Path(__file__).parents[1]/"notification_lifecycle.py"
spec=importlib.util.spec_from_file_location("notification_lifecycle",P)
m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m)

class Vault:
    def __init__(self):
        self.data={}; self.fail_put=False; self.fail_delete=False; self.delete_calls=[]
    def put(self,k,v):
        if self.fail_put: raise RuntimeError("vault put failed")
        self.data[k]=v
    def get(self,k): return self.data[k]
    def delete(self,k):
        self.delete_calls.append(k)
        if self.fail_delete: raise RuntimeError("vault delete failed")
        self.data.pop(k,None)

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
    assert old.token_id not in v.data and new.token_id in v.data

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
    schema=" ".join(db.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='notification_tokens'").fetchone()[0].split())
    assert "UNIQUE(subject, session_id, package, provider, fingerprint)" in schema
    with pytest.raises(PermissionError): r.get("legacy",subject="u1",session_id="s1")
    raw="same-provider-token-123456"
    a=register(r,session_id="s1",token=raw); b=register(r,session_id="s2",token=raw)
    assert a.token_id != b.token_id
    assert r.get(a.token_id,subject="u1",session_id="s1").active
    assert r.get(b.token_id,subject="u1",session_id="s2").active
    assert db.execute("SELECT COUNT(*) FROM notification_tokens").fetchone()[0]==3
    assert db.execute("SELECT COUNT(*) FROM notification_token_cleanup").fetchone()[0]==0

def test_invalid_session_package_and_provider_fail_closed():
    r,_=reg()
    with pytest.raises(PermissionError): register(r,session_id="")
    with pytest.raises(PermissionError): register(r,session_id=m.LEGACY_UNBOUND_SESSION)
    with pytest.raises(PermissionError): register(r,package="com.evil.fake")
    with pytest.raises(ValueError): r.register(subject="u1",session_id="s1",package="com.topherofit.thf.pulse",provider="bad",raw_token="abcdefgh1234")

def test_revoke_delete_failure_journals_only_opaque_id_and_retries():
    r,v=reg(); raw="sensitive-provider-token-123456"; x=register(r,token=raw)
    v.fail_delete=True
    r.revoke(token_id=x.token_id,subject="u1",session_id="s1")
    assert not r.get(x.token_id,subject="u1",session_id="s1").active
    assert x.token_id in v.data and r.pending_vault_cleanup_count()==1
    row=r.db.execute("SELECT token_id,attempts,last_error FROM notification_token_cleanup").fetchone()
    assert row[0]==x.token_id and row[1]==1 and "delete failed" in row[2]
    dump=" ".join(str(z) for z in row)
    assert raw not in dump and x.fingerprint not in dump
    assert r.drain_vault_cleanup()==(0,1)
    attempts=r.db.execute("SELECT attempts FROM notification_token_cleanup WHERE token_id=?",(x.token_id,)).fetchone()[0]
    assert attempts==2
    v.fail_delete=False
    assert r.drain_vault_cleanup()==(1,0)
    assert r.pending_vault_cleanup_count()==0 and x.token_id not in v.data

def test_rotation_delete_failure_keeps_new_token_live_and_tracks_old_cleanup():
    r,v=reg(); p="com.topherofit.thf.echo"
    old=register(r,package=p,token="old-provider-token-123456")
    v.fail_delete=True
    new=r.rotate(subject="u1",session_id="s1",package=p,provider="fcm",old_token_id=old.token_id,new_raw_token="new-provider-token-123456")
    assert new.active and not r.get(old.token_id,subject="u1",session_id="s1").active
    assert r.pending_vault_cleanup_count()==1
    assert old.token_id in v.data and new.token_id in v.data
    v.fail_delete=False
    assert r.drain_vault_cleanup()==(1,0)
    assert old.token_id not in v.data and new.token_id in v.data

def test_reregister_same_token_cancels_stale_cleanup_before_reactivation():
    r,v=reg(); raw="provider-token-reactivate-123456"; x=register(r,token=raw)
    v.fail_delete=True
    r.revoke(token_id=x.token_id,subject="u1",session_id="s1")
    assert r.pending_vault_cleanup_count()==1 and x.token_id in v.data
    v.fail_delete=False
    again=register(r,token=raw)
    assert again.token_id==x.token_id and again.active
    assert r.pending_vault_cleanup_count()==0
    assert v.data[x.token_id]==raw
    assert r.drain_vault_cleanup()==(0,0)
    assert v.data[x.token_id]==raw

def test_cleanup_never_deletes_active_registration_even_with_stale_journal_row():
    r,v=reg(); x=register(r)
    r.db.execute(
        "INSERT INTO notification_token_cleanup(token_id,queued_at,attempts,last_error) VALUES(?,?,?,?)",
        (x.token_id,1,1,"synthetic stale row"),
    ); r.db.commit()
    before=list(v.delete_calls)
    assert r.drain_vault_cleanup()==(1,0)
    assert v.delete_calls==before
    assert r.get(x.token_id,subject="u1",session_id="s1").active
    assert x.token_id in v.data and r.pending_vault_cleanup_count()==0

def test_rotation_to_already_active_destination_fails_without_mutation():
    r,v=reg(); p="com.topherofit.thf.pulse"
    first=register(r,package=p,token="provider-first-token-123")
    second=register(r,package=p,token="provider-second-token-123")
    snapshot=dict(v.data)
    with pytest.raises(ValueError,match="already active"):
        r.rotate(subject="u1",session_id="s1",package=p,provider="fcm",old_token_id=first.token_id,new_raw_token="provider-second-token-123")
    assert r.get(first.token_id,subject="u1",session_id="s1").active
    assert r.get(second.token_id,subject="u1",session_id="s1").active
    assert v.data==snapshot

def test_cleanup_limit_is_bounded():
    r,_=reg()
    for bad in (0,-1,1001,1.5):
        with pytest.raises(ValueError): r.drain_vault_cleanup(limit=bad)

def test_provider_delivery_is_intentionally_not_implemented():
    assert not hasattr(m.NotificationTokenRegistry,"send")
