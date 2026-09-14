import importlib.util
import sys
from pathlib import Path
import pytest

P=Path(__file__).parents[1]/"notification_provider_contract.py"
spec=importlib.util.spec_from_file_location("notification_provider_contract",P)
m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m)

class Adapter:
    provider_name="fcm"
    def __init__(self,configured=False): self.configured=configured; self.sent=[]
    def validate_configuration(self): return self.configured
    def send(self,request): self.sent.append(request); return m.DeliveryResult(accepted=True,provider_message_id="test-only")

def req(**kw):
    d=dict(token_id="id123",title_key="push.title",body_key="push.body",locale="ar",deeplink="thf://pulse/home",data_saver=False)
    d.update(kw); return m.DeliveryRequest(**d)

def test_unconfigured_adapter_is_structurally_conformant_but_not_delivery_ready():
    a=Adapter(False); m.assert_adapter_conformance(a); assert a.validate_configuration() is False and a.sent==[]

def test_supported_configured_adapter_conforms_without_sending():
    a=Adapter(True); m.assert_adapter_conformance(a); assert a.sent==[]

def test_unknown_provider_fails_closed():
    a=Adapter(); a.provider_name="unknown"
    with pytest.raises(ValueError): m.assert_adapter_conformance(a)

def test_missing_adapter_methods_fail_closed():
    class Broken: provider_name="fcm"
    with pytest.raises(TypeError): m.assert_adapter_conformance(Broken())

def test_localization_fields_and_token_id_are_mandatory():
    for r in (req(token_id=""),req(title_key=""),req(body_key=""),req(locale="")):
        with pytest.raises(ValueError): m.validate_delivery_request(r)

def test_deeplinks_must_be_credential_free():
    m.validate_delivery_request(req(deeplink="thf://pulse/inbox?id=42"))
    for q in ("token=x","access_token=x","authorization=x","secret=x","credential=x"):
        with pytest.raises(PermissionError): m.validate_delivery_request(req(deeplink=f"thf://pulse/inbox?{q}"))

def test_data_saver_is_explicit_contract_input():
    r=req(data_saver=True); m.validate_delivery_request(r); assert r.data_saver is True
