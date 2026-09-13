import importlib.util, pathlib, tempfile, unittest

SCRIPT=pathlib.Path(__file__).parents[1]/'scripts'/'thf_game_real_function_audit_v2.py'
spec=importlib.util.spec_from_file_location('auditv2',SCRIPT); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

class AuditV2Tests(unittest.TestCase):
    def mk(self,kind='terra',placeholder=False):
        td=tempfile.TemporaryDirectory(); r=pathlib.Path(td.name)
        (r/'project.godot').write_text('[display]\nhandheld/orientation=3\nstretch/aspect="expand"\n')
        (r/'export_presets.cfg').write_text('[preset.0]\nname="Android"\n')
        body='''extends CharacterBody3D\nfunc _physics_process(delta):\n velocity.x=1\n move_and_slide()\nfunc _input(e):\n if e is InputEventScreenTouch: pass\nvar avatar=preload("res://player.tscn")\nvar camera_controller=true\nvar score=0\nfunc interact(): pass\n'''
        if placeholder: body+='var api="http://localhost:8080"\n'
        (r/'main.gd').write_text(body)
        return td,r
    def test_mobile_terra_passes_core_contract(self):
        td,r=self.mk(); out=mod.audit(r,'terra'); self.assertEqual(out['source_contract_status'],'PASS'); self.assertEqual(out['device_status'],'PENDING'); td.cleanup()
    def test_placeholder_rejected(self):
        td,r=self.mk(placeholder=True); out=mod.audit(r,'terra'); self.assertIn('no_placeholder_endpoint',out['summary']['required_failures']); td.cleanup()
    def test_ui_only_shell_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            r=pathlib.Path(d); (r/'index.html').write_text('<button>Play</button><div id="score">0</div>')
            out=mod.audit(r,'learn'); self.assertIn('no_ui_only_shell',out['summary']['required_failures'])
    def test_rift_requires_combat(self):
        td,r=self.mk(); out=mod.audit(r,'rift'); self.assertIn('combat_wiring',out['summary']['required_failures']); td.cleanup()

if __name__=='__main__': unittest.main()
