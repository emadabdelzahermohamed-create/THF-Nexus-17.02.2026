import importlib.util
import sqlite3
import sys
from pathlib import Path
import pytest

ROOT=Path(__file__).parents[1]
for name in ("notification_lifecycle","notification_provider_contract","notification_dispatch"):
    spec=importlib.util.spec_from_file_location(name,ROOT/f"{name}.py")
    mod=importlib.util.module_from_spec(spec); sys.modules[name]=mod; spec.loader.exec_module(mod)
life=sys.modules["notification_lifecycle"]; prov=sys.modules["notification_provider_contract"]; dispatch=sys.modules["notification_dispatch"]

class Vault:
    def __init__(self): self.data={}; self.get_calls=[]
    def put(self,k,v): self.data[k]=v
    def get(self,k): self.get_calls.append(k); return self.data[k]
    def delete(self,k): self.data.pop(k,None)
class Adapter:
    provider_name="fcm"
    def __init__(self,configured=True,result=None): self.configured=configured; self.calls=[]; self.result=result or prov.DeliveryResult(True,"m1")
    def validate_configuration(self): return self.configured
    def send(self,*,provider_token,request): self.calls.append((provider_token,request)); return self.result
class Guard:
    def __init__(self,allowed=True): self.allowed=allowed; self.calls=[]
    def authorize_delivery(self,*,subject,session_id,package):
        self.calls.append((subject,session_id,package))
        if not self.allowed: raise PermissionError("session authority rejected delivery")

def setup_adapter(*,configured=True,result=None,guard=None):
    v=Vault(); r=life.NotificationTokenRegistry(sqlite3.connect(":memory:"),v)
    x=r.register(subject="u1",session_id="s1",package="com.topherofit.thf.pulse",provider="fcm",raw_token="provider-token-123456")
    a=Adapter(configured,result); g=guard or Guard(); d=dispatch.NotificationDispatcher(r,{"fcm":a},session_guard=g)
    req=prov.DeliveryRequest(x.token_id,"push.title","push.body","ar","thf://pulse/home",False)
    return r,v,x,a,g,d,req

def test_dispatch_requires_exact_subject_and_session_registration():
    r,v,x,a,g,d,req=setup_adapter(); out=d.dispatch(subject="u1",session_id="s1",request=req)
    assert out.accepted and a.calls==[("provider-token-123456",req)]
    assert g.calls==[("u1","s1","com.topherofit.thf.pulse")]
    with pytest.raises(PermissionError): d.dispatch(subject="u1",session_id="s2",request=req)
    with pytest.raises(PermissionError): d.dispatch(subject="u2",session_id="s1",request=req)

def test_dispatcher_requires_live_session_guard():
    v=Vault(); r=life.NotificationTokenRegistry(sqlite3.connect(":memory:"),v); a=Adapter()
    with pytest.raises(ValueError,match="guard is required"):
        dispatch.NotificationDispatcher(r,{"fcm":a},session_guard=None)

def test_guard_rejection_happens_before_vault_read_or_provider_send():
    r,v,x,a,g,d,req=setup_adapter(guard=Guard(False)); v.get_calls.clear()
    with pytest.raises(PermissionError,match="authority rejected"):
        d.dispatch(subject="u1",session_id="s1",request=req)
    assert g.calls==[("u1","s1","com.topherofit.thf.pulse")]
    assert v.get_calls==[] and a.calls==[]

def test_unconfigured_adapter_never_sends():
    _,_,_,a,_,d,req=setup_adapter(configured=False)
    with pytest.raises(RuntimeError,match="not configured"): d.dispatch(subject="u1",session_id="s1",request=req)
    assert a.calls==[]

def test_permanent_provider_failure_revokes_only_session_registration():
    result=prov.DeliveryResult(False,permanent_token_failure=True)
    r,v,x,a,g,d,req=setup_adapter(result=result); out=d.dispatch(subject="u1",session_id="s1",request=req)
    assert out.permanent_token_failure is True
    assert r.get(x.token_id,subject="u1",session_id="s1").active is False and x.token_id not in v.data

def test_retryable_failure_keeps_registration_active():
    result=prov.DeliveryResult(False,retryable=True)
    r,v,x,a,g,d,req=setup_adapter(result=result); out=d.dispatch(subject="u1",session_id="s1",request=req)
    assert out.retryable is True and r.get(x.token_id,subject="u1",session_id="s1").active

def test_invalid_provider_result_fails_closed_without_revoking():
    r,v,x,a,g,d,req=setup_adapter(result=prov.DeliveryResult(True,None))
    with pytest.raises(ValueError): d.dispatch(subject="u1",session_id="s1",request=req)
    assert r.get(x.token_id,subject="u1",session_id="s1").active

def test_adapter_map_identity_must_match_provider_name():
    r,_,_,a,g,_,_=setup_adapter()
    with pytest.raises(ValueError): dispatch.NotificationDispatcher(r,{"apns":a},session_guard=g)
