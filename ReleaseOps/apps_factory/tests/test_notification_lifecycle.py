import importlib.util
import sqlite3
import sys
from pathlib import Path
import pytest

P=Path(__file__).parents[1]/"notification_lifecycle.py"
spec=importlib.util.spec_from_file_location("notification_lifecycle",P)
m=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=m
spec.loader.exec_module(m)

class Vault:
    def __init__(self): self.data={}
    def put(self,k,v): self.data[k]=v
    def delete(self,k): self.data.pop(k,None)

def reg():
    v=Vault(); r=m.NotificationTokenRegistry(sqlite3.connect(":memory:"),v); return r,v

def test_register_stores_only_fingerprint_in_db_and_raw_token_in_vault():
    r,v=reg(); raw="provider-token-123456"
    x=r.register(subject="u1",package="com.topherofit.thf.pulse",provider="fcm",raw_token=raw)
    assert x.active and len(x.fingerprint)==64 and x.generation==1
    assert v.data[x.token_id]==raw
    dump=" ".join(str(z) for z in r.db.execute("select * from notification_tokens").fetchone())
    assert raw not in dump

def test_rejects_unknown_package_and_unauthenticated_subject():
    r,_=reg()
    with pytest.raises(PermissionError): r.register(subject="",package="com.topherofit.thf.pulse",provider="fcm",raw_token="abcdefgh1234")
    with pytest.raises(PermissionError): r.register(subject="u",package="com.evil.fake",provider="fcm",raw_token="abcdefgh1234")

def test_rotation_revokes_old_token_and_increments_generation():
    r,v=reg(); p="com.topherofit.thf.echo"
    old=r.register(subject="u1",package=p,provider="fcm",raw_token="old-token-123456")
    new=r.rotate(subject="u1",package=p,provider="fcm",old_token_id=old.token_id,new_raw_token="new-token-123456")
    assert not r.get(old.token_id,subject="u1").active
    assert old.token_id not in v.data
    assert new.active and new.generation==2 and new.token_id in v.data

def test_cross_subject_access_is_fail_closed():
    r,_=reg(); x=r.register(subject="u1",package="com.topherofit.thf.forge",provider="fcm",raw_token="provider-token-123456")
    with pytest.raises(PermissionError): r.get(x.token_id,subject="u2")
    with pytest.raises(PermissionError): r.revoke(token_id=x.token_id,subject="u2")

def test_logout_revokes_only_subject_package_tokens():
    r,v=reg(); pulse="com.topherofit.thf.pulse"; forge="com.topherofit.thf.forge"
    a=r.register(subject="u1",package=pulse,provider="fcm",raw_token="token-pulse-12345")
    b=r.register(subject="u1",package=forge,provider="fcm",raw_token="token-forge-12345")
    c=r.register(subject="u2",package=pulse,provider="fcm",raw_token="token-other-12345")
    assert r.revoke_logout(subject="u1",package=pulse)==1
    assert not r.get(a.token_id,subject="u1").active
    assert r.get(b.token_id,subject="u1").active
    assert r.get(c.token_id,subject="u2").active

def test_provider_delivery_is_intentionally_not_implemented():
    assert not hasattr(m.NotificationTokenRegistry,"send")
