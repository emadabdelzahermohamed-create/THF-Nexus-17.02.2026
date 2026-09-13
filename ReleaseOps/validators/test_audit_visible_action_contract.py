from pathlib import Path
import importlib.util,tempfile
P=Path(__file__).with_name('audit_visible_action_contract.py')
s=importlib.util.spec_from_file_location('m',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

def tree(root,html,py=''):
 r=Path(root); (r/'app/web').mkdir(parents=True); (r/'app/web/index.html').write_text(html); (r/'app/main.py').write_text(py); return r

def test_real_button_and_route_pass():
 with tempfile.TemporaryDirectory() as d:
  r=tree(d,"""<button id='go'>Go</button><a href='/help'>Help</a><script>
  document.getElementById('go').onclick=()=>fetch('/api/items');
  </script>""","""from fastapi import FastAPI
app=FastAPI()
@app.get('/api/items')
def items(): return []
""")
  a=m.audit(r); assert a['source_action_contract_complete']; assert not a['orphan_buttons']; assert not a['unmapped_local_api_references']

def test_legacy_named_id_and_form_helper_are_handlers():
 with tempfile.TemporaryDirectory() as d:
  r=tree(d,"""<button id='save'>Save</button><form id='pro'><button>Submit</button></form><script>
  save.onclick=()=>{}; function postForm(x){x.onsubmit=e=>e.preventDefault()} postForm(pro);
  </script>""")
  a=m.audit(r); assert not a['orphan_buttons']; assert not a['orphan_forms']

def test_orphan_button_and_dead_anchor_fail():
 with tempfile.TemporaryDirectory() as d:
  a=m.audit(tree(d,"<button id='x'>X</button><a href='#'>Dead</a>"))
  assert not a['source_action_contract_complete']; assert a['orphan_buttons']; assert a['bad_anchors']

def test_unmapped_local_fetch_fails():
 with tempfile.TemporaryDirectory() as d:
  a=m.audit(tree(d,"<button onclick=\"fetch('/api/missing')\">X</button>"))
  assert '/api/missing' in a['unmapped_local_api_references']; assert not a['source_action_contract_complete']

def test_dynamic_fetch_not_falsely_mapped():
 with tempfile.TemporaryDirectory() as d:
  a=m.audit(tree(d,"<button onclick=\"fetch(`/api/item/${id}`)\">X</button>"))
  assert not a['unmapped_local_api_references']

def test_literal_prefix_maps_parameterized_backend_route():
 with tempfile.TemporaryDirectory() as d:
  r=tree(d,"<button onclick=\"fetch('/api/handoff/'+target)\">X</button>","""from fastapi import FastAPI
app=FastAPI()
@app.post('/api/handoff/{target}')
def h(target): return target
""")
  a=m.audit(r); assert not a['unmapped_local_api_references']
