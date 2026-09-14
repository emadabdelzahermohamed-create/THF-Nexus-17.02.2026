#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, sys, tempfile, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
S=importlib.util.spec_from_file_location('v14',HERE/'validate_game_device_evidence_v14.py'); M=importlib.util.module_from_spec(S); sys.modules[S.name]=M; S.loader.exec_module(M)
T=importlib.util.spec_from_file_location('t13',HERE/'test_validate_game_device_evidence_v13.py'); T13=importlib.util.module_from_spec(T); sys.modules[T.name]=T13; T.loader.exec_module(T)
V3=M.V3

def lines(product,key):
 base=['THF_RESULT=PASS']
 if key=='touch': base+=['THF_TOUCH_EVENTS_OBSERVED=4']
 elif key=='orientation_layout': base+=['THF_LAYOUT_SAFE_AREA_OK=TRUE','THF_ORIENTATION_OK=TRUE']+(['THF_SENSOR_LANDSCAPE=TRUE'] if product in {'terra','rift'} else [])
 elif key=='core_user_journey': base+=['THF_CORE_JOURNEY_COMPLETED=TRUE']
 elif key=='gameplay_interaction': base+=['THF_GAMEPLAY_INTERACTION=TRUE']
 elif key=='avatar_or_player_load': base+=['THF_AVATAR_LOADED=TRUE']
 elif key=='movement_camera': base+=['THF_PLAYER_MOVED=TRUE','THF_CAMERA_MOVED=TRUE']
 elif key=='world_npc_interaction': base+=['THF_WORLD_INTERACTION=TRUE']
 elif key=='combat': base+=['THF_COMBAT_ACTION=TRUE','THF_COMBAT_STATE_CHANGED=TRUE']
 elif key=='learning_progression': base+=['THF_LEARNING_PROGRESS_BEFORE=2','THF_LEARNING_PROGRESS_AFTER=3']
 elif key=='sensor_motion': base+=['THF_SENSOR_EVENTS_OBSERVED=12']
 elif key=='repetition_counting': base+=['THF_REPS_BEFORE=3','THF_REPS_AFTER=4']
 return base

def evidence(product,rsha,root):
 d=T13.evidence(product,rsha,root)
 for key,row in d['manual_observations'].items():
  if key not in M.BASE and key not in M.PRODUCT.get(product,{}): continue
  p=root/row['evidence_ref']; text=p.read_text(encoding='utf-8')+'\nTHF_SESSION_ID='+d['session']['session_id']+'\nTHF_PACKAGE='+d['package']+'\nTHF_CAPABILITY='+key+'\n'+'\n'.join(lines(product,key))+'\n'; p.write_text(text,encoding='utf-8'); row['evidence_sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
 return d

class V14(unittest.TestCase):
 def setUp(self): self.reg=T13.T12.T11.T10.T9.T8.T7.T6.registry_doc(); self.rsha='f'*64
 def test_all_six_pass(self):
  for product in V3.PRODUCT_MANUAL:
   with self.subTest(product=product), tempfile.TemporaryDirectory() as td:
    root=Path(td); self.assertEqual([],M.validate_bundle(self.reg,self.rsha,evidence(product,self.rsha,root),root))
 def test_rift_fake_combat_fails(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); d=evidence('rift',self.rsha,root); row=d['manual_observations']['combat']; p=root/row['evidence_ref']; p.write_text(p.read_text().replace('THF_COMBAT_STATE_CHANGED=TRUE','THF_COMBAT_STATE_CHANGED=FALSE')); row['evidence_sha256']=hashlib.sha256(p.read_bytes()).hexdigest(); self.assertTrue(any('THF_COMBAT_STATE_CHANGED=TRUE required' in x for x in M.validate_bundle(self.reg,self.rsha,d,root)))
 def test_learning_must_advance(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); d=evidence('spark',self.rsha,root); row=d['manual_observations']['learning_progression']; p=root/row['evidence_ref']; p.write_text(p.read_text().replace('THF_LEARNING_PROGRESS_AFTER=3','THF_LEARNING_PROGRESS_AFTER=2')); row['evidence_sha256']=hashlib.sha256(p.read_bytes()).hexdigest(); self.assertTrue(any('strictly increasing' in x for x in M.validate_bundle(self.reg,self.rsha,d,root)))
 def test_sensor_count_must_be_positive(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); d=evidence('rush',self.rsha,root); row=d['manual_observations']['sensor_motion']; p=root/row['evidence_ref']; p.write_text(p.read_text().replace('THF_SENSOR_EVENTS_OBSERVED=12','THF_SENSOR_EVENTS_OBSERVED=0')); row['evidence_sha256']=hashlib.sha256(p.read_bytes()).hexdigest(); self.assertTrue(any('positive observed event count' in x for x in M.validate_bundle(self.reg,self.rsha,d,root)))
 def test_terra_requires_sensor_landscape(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); d=evidence('terra',self.rsha,root); row=d['manual_observations']['orientation_layout']; p=root/row['evidence_ref']; p.write_text(p.read_text().replace('THF_SENSOR_LANDSCAPE=TRUE','THF_SENSOR_LANDSCAPE=FALSE')); row['evidence_sha256']=hashlib.sha256(p.read_bytes()).hexdigest(); self.assertTrue(any('SENSOR_LANDSCAPE' in x for x in M.validate_bundle(self.reg,self.rsha,d,root)))
if __name__=='__main__': unittest.main()
