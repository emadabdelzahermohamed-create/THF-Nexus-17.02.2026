import importlib.util, pathlib, tempfile, unittest

SCRIPT=pathlib.Path(__file__).parents[1]/'scripts'/'thf_game_shared_systems_audit_v1.py'
spec=importlib.util.spec_from_file_location('audit',SCRIPT); audit=importlib.util.module_from_spec(spec); spec.loader.exec_module(audit)

class SharedSystemsAuditTests(unittest.TestCase):
 def test_rift_real_signals_detected(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d); (r/'game.gd').write_text('''extends CharacterBody3D\nvar avatar=true\nfunc _physics_process(d): move_and_slide()\n# AnimationTree Skeleton3D Camera3D TouchScreenButton attack damage combat\n''')
   _,s=audit.scan(r)
   for key in ['avatar','animation','locomotion','camera','touch','combat']:
    self.assertGreater(s[key]['matches'],0,key)
 def test_ui_shell_does_not_fake_required_gameplay(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d); (r/'ui.gd').write_text('extends Control\n# menu settings button label\n')
   _,s=audit.scan(r)
   for key in ['locomotion','camera','touch','combat','world']:
    self.assertEqual(s[key]['matches'],0,key)
 def test_server_and_offline_signals_are_separate(self):
  with tempfile.TemporaryDirectory() as d:
   r=pathlib.Path(d); (r/'modes.gd').write_text('''# authoritative server validation over wss://\n# offline local_training practice single_player\n''')
   _,s=audit.scan(r)
   self.assertGreater(s['server_authority']['matches'],0)
   self.assertGreater(s['offline_local']['matches'],0)

if __name__=='__main__': unittest.main()
