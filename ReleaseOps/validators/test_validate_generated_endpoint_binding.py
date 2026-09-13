from pathlib import Path
import importlib.util,tempfile
P=Path(__file__).with_name('validate_generated_endpoint_binding.py')
s=importlib.util.spec_from_file_location('m',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

def cfg(root,base,passwd):
 p=Path(root)/'BuildConfig.java';p.write_text(f'''public final class BuildConfig {{
 public static final String THF_BASE_URL = "{base}";
 public static final String THF_PASS_URL = "{passwd}";
}}''');return p

def test_secure_bindings_pass():
 with tempfile.TemporaryDirectory() as d:
  r=m.inspect(cfg(d,'https://api.topherofit.test','https://pass.topherofit.test'))
  assert r['binding_gate_pass']; assert r['bindings']['THF_BASE_URL']['value_redacted']=='<bound:https>'

def test_empty_binding_fails():
 with tempfile.TemporaryDirectory() as d:
  r=m.inspect(cfg(d,'',''))
  assert not r['binding_gate_pass']; assert not r['bindings']['THF_BASE_URL']['nonempty']

def test_cleartext_and_placeholder_fail():
 with tempfile.TemporaryDirectory() as d:
  r=m.inspect(cfg(d,'http://api.topherofit.test','https://example.com/pass'))
  assert not r['binding_gate_pass']; assert not r['bindings']['THF_BASE_URL']['secure_scheme']; assert not r['bindings']['THF_PASS_URL']['non_placeholder']
