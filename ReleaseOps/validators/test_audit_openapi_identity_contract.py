from pathlib import Path
import importlib.util
P=Path(__file__).with_name('audit_openapi_identity_contract.py')
s=importlib.util.spec_from_file_location('m',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

def test_complete_identity_surface():
 d={'openapi':'3.1.0','info':{'title':'THF'},'paths':{
 '/health':{'get':{}},'/auth/login':{'post':{}},'/auth/refresh':{'post':{}},
 '/auth/logout':{'post':{}},'/auth/revoke':{'post':{}},'/pass/handoff':{'post':{}}}}
 r=m.audit(d); assert r['health_surface']; assert r['identity_lifecycle_surface_complete']; assert r['shared_pass_surface_complete']; assert not r['truth_boundary']['final_or_play_ready']

def test_missing_refresh_revoke_fails_closed():
 d={'paths':{'/health':{'get':{}},'/login':{'post':{}},'/logout':{'post':{}},'/handoff':{'post':{}}}}
 r=m.audit(d); assert not r['identity_lifecycle_surface_complete']; assert not r['shared_pass_surface_complete']; assert not r['capabilities']['refresh']; assert not r['capabilities']['revoke']

def test_wrong_http_method_does_not_pass():
 d={'paths':{'/refresh':{'get':{}},'/revoke':{'get':{}}}}
 r=m.audit(d); assert not r['capabilities']['refresh']; assert not r['capabilities']['revoke']
