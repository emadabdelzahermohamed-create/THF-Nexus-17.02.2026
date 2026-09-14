import importlib.util
import sqlite3
import sys
from pathlib import Path
import pytest

ROOT=Path(__file__).parents[1]
for name in ("notification_lifecycle", "notification_http_contract"):
    p=ROOT/f"{name}.py"
    spec=importlib.util.spec_from_file_location(name,p)
    mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod
    spec.loader.exec_module(mod)

life=sys.modules["notification_lifecycle"]
http=sys.modules["notification_http_contract"]

class Vault:
    def __init__(self): self.data={}
    def put(self,k,v): self.data[k]=v
    def delete(self,k): self.data.pop(k,None)

def contract():
    v=Vault()
    r=life.NotificationTokenRegistry(sqlite3.connect(":memory:"),v)
    return http.NotificationHttpContract(r),r,v

def principal(subject="u1", package="com.topherofit.thf.pulse", authenticated=True):
    return http.SessionPrincipal(subject=subject,session_id="session-123",package_id=package,authenticated=authenticated)

def test_register_requires_verified_pass_session_and_returns_no_raw_token():
    c,_,v=contract()
    body={"package":"com.topherofit.thf.pulse","provider":"fcm","provider_token":"provider-token-123456"}
    with pytest.raises(PermissionError): c.register(principal=principal(authenticated=False),body=body)
    out=c.register(principal=principal(),body=body)
    assert out.status==201 and out.body["active"] is True
    assert "provider_token" not in out.body
    assert list(v.data.values())==["provider-token-123456"]

def test_credentials_and_provider_tokens_are_rejected_in_query_strings():
    c,_,_=contract()
    body={"package":"com.topherofit.thf.echo","provider":"fcm","provider_token":"provider-token-123456"}
    for key in ("token","access_token","Authorization","provider-token","secret"):
        with pytest.raises(PermissionError): c.register(principal=principal(package=body["package"]),body=body,query={key:"leak"})

def test_unknown_package_fails_closed_through_http_contract():
    c,_,_=contract()
    with pytest.raises(PermissionError):
        c.register(principal=principal(package="com.fake.app"),body={"package":"com.fake.app","provider":"fcm","provider_token":"provider-token-123456"})

def test_cross_app_pass_audience_fails_closed():
    c,_,_=contract()
    with pytest.raises(PermissionError):
        c.register(
            principal=principal(package="com.topherofit.thf.pulse"),
            body={"package":"com.topherofit.thf.forge","provider":"fcm","provider_token":"provider-token-123456"},
        )

def test_rotation_and_revoke_are_subject_and_package_scoped():
    c,r,_=contract(); p="com.topherofit.thf.forge"
    body={"package":p,"provider":"fcm","provider_token":"old-token-123456"}
    first=c.register(principal=principal("u1",p),body=body)
    tid=first.body["token_id"]
    with pytest.raises(PermissionError): c.revoke(principal=principal("u2",p),body={"token_id":tid})
    with pytest.raises(PermissionError): c.revoke(principal=principal("u1","com.topherofit.thf.pulse"),body={"token_id":tid})
    rotated=c.rotate(principal=principal("u1",p),body={"package":p,"provider":"fcm","old_token_id":tid,"provider_token":"new-token-123456"})
    assert rotated.status==200 and rotated.body["generation"]==2
    assert not r.get(tid,subject="u1").active
    assert c.revoke(principal=principal("u1",p),body={"token_id":rotated.body["token_id"]}).status==204

def test_logout_revokes_only_authenticated_subject_package():
    c,r,_=contract(); p="com.topherofit.thf.codex"
    a=c.register(principal=principal("u1",p),body={"package":p,"provider":"fcm","provider_token":"token-user-one-123"})
    b=c.register(principal=principal("u2",p),body={"package":p,"provider":"fcm","provider_token":"token-user-two-123"})
    out=c.logout(principal=principal("u1",p),body={"package":p})
    assert out.status==200 and out.body["revoked"]==1
    assert not r.get(a.body["token_id"],subject="u1").active
    assert r.get(b.body["token_id"],subject="u2").active

def test_required_fields_fail_closed():
    c,_,_=contract()
    with pytest.raises(ValueError): c.register(principal=principal(),body={"package":"com.topherofit.thf.pulse","provider":"fcm"})
