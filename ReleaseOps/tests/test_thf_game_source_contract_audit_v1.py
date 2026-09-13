#!/usr/bin/env python3
import importlib.util, pathlib, tempfile, unittest

MOD_PATH=pathlib.Path(__file__).parents[1]/'scripts'/'thf_game_source_contract_audit_v1.py'
spec=importlib.util.spec_from_file_location('audit',MOD_PATH); audit=importlib.util.module_from_spec(spec); spec.loader.exec_module(audit)

GOOD_PROJECT='''[application]\nconfig/name="THF"\n[display]\n[display/window]\nsize/viewport_width=1920\nsize/viewport_height=1080\nhandheld/orientation=3\nstretch/aspect="expand"\n'''
GOOD_GD='''extends CharacterBody3D\nvar run_speed=8.0\nfunc _input(event):\n if event is InputEventScreenTouch: pass\nfunc _physics_process(delta):\n velocity.x=1\n move_and_slide()\n# avatar humanoid AnimationTree Camera3D NPC NavigationAgent3D WorldEnvironment weather day_night LOD AudioStreamPlayer GPUParticles3D locale reduce_motion data_saver offline local_training authoritative https://api.thf.invalid/rpc interact quest inventory\n'''
RIFT_GD='''# attack weapon damage hitbox hurtbox reload anti_cheat validate_hit proof_of_human\n'''

class AuditTests(unittest.TestCase):
 def make(self,game='terra',project=GOOD_PROJECT,gd=GOOD_GD):
  td=tempfile.TemporaryDirectory(); root=pathlib.Path(td.name); (root/'project.godot').write_text(project); (root/'export_presets.cfg').write_text('[preset.0]\nname="Android"\nplatform="Android"\n'); (root/'main.gd').write_text(gd+(RIFT_GD if game=='rift' else ''))
  return td,root
 def statuses(self,root,game):
  checks,_=audit.audit(root,game); return {c['name']:c['status'] for c in checks}
 def test_mobile_contract_passes(self):
  td,r=self.make(); s=self.statuses(r,'terra'); self.assertEqual(s['sensor_landscape'],'PASS'); self.assertEqual(s['expandable_aspect'],'PASS'); self.assertEqual(s['touch_input_contract'],'PASS'); self.assertEqual(s['world_interaction'],'PASS'); td.cleanup()
 def test_desktop_override_rejected(self):
  td,r=self.make(project=GOOD_PROJECT+'display/window/size/window_width_override=1280\n'); self.assertEqual(self.statuses(r,'terra')['no_desktop_window_override'],'FAIL'); td.cleanup()
 def test_placeholder_endpoint_rejected(self):
  td,r=self.make(gd=GOOD_GD+'\n# https://example.com/api\n'); self.assertEqual(self.statuses(r,'terra')['no_placeholder_endpoint'],'FAIL'); td.cleanup()
 def test_rift_requires_combat(self):
  td,r=self.make(game='rift',gd=GOOD_GD); self.assertEqual(self.statuses(r,'rift')['combat_wiring'],'FAIL'); td.cleanup()
 def test_rift_combat_passes(self):
  td,r=self.make(game='rift'); self.assertEqual(self.statuses(r,'rift')['combat_wiring'],'PASS'); td.cleanup()
 def test_duplicate_project_rejected(self):
  td,r=self.make(); (r/'nested').mkdir(); (r/'nested'/'project.godot').write_text(GOOD_PROJECT); self.assertEqual(self.statuses(r,'terra')['unique_project_root'],'FAIL'); td.cleanup()
if __name__=='__main__': unittest.main()
