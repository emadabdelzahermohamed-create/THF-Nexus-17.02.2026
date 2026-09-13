import importlib.util,pathlib,tempfile,unittest
P=pathlib.Path(__file__).parents[1]/'scripts/thf_game_runtime_binding_audit_v1.py';S=importlib.util.spec_from_file_location('audit',P);M=importlib.util.module_from_spec(S);S.loader.exec_module(M)
GOOD='''extends Node3D\nfunc _physics_process(delta):\n velocity=Vector3.ZERO\n if Input.is_action_pressed("move_forward"): velocity.z-=1\n move_and_slide()\n var player_avatar=MeshInstance3D.new()\n add_child(player_avatar)\n var cam=Camera3D.new()\n add_child(cam)\n var anim=AnimationPlayer.new()\n add_child(anim)\n func camera_look(): cam.rotate_y(0.1)\n func interact_world(): pass\n'''
class T(unittest.TestCase):
 def run_case(self,text,kind='terra'):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);(r/'main.gd').write_text(text);return M.audit(r,kind)
 def test_dynamic_same_script_passes_player_avatar_binding(self):
  x=self.run_case(GOOD);self.assertNotIn('player_runtime_binding',x['required_failures']);self.assertNotIn('avatar_runtime_binding',x['required_failures']);self.assertEqual(x['dynamic_player_files'],['main.gd'])
 def test_asset_only_does_not_pass(self):
  x=self.run_case('extends Node3D\nvar avatar="hero.glb"\n');self.assertIn('player_runtime_binding',x['required_failures']);self.assertIn('avatar_runtime_binding',x['required_failures'])
 def test_split_markers_do_not_fake_dynamic_binding(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d);(r/'move.gd').write_text('func _physics_process(d):\n velocity=Vector3.ZERO\n if Input.is_action_pressed("x"): pass\n move_and_slide()');(r/'visual.gd').write_text('var player=MeshInstance3D.new()\nfunc x(): add_child(player)\nvar c=Camera3D.new()\nvar a=AnimationPlayer.new()');x=M.audit(r,'terra');self.assertFalse(x['dynamic_player_files']);self.assertIn('player_runtime_binding',x['required_failures'])
if __name__=='__main__':unittest.main()
