import importlib.util, json, pathlib, tempfile, unittest

SCRIPT = pathlib.Path(__file__).parents[1] / 'scripts' / 'thf_terra_rift_mobile_overlay_v1.py'
spec = importlib.util.spec_from_file_location('overlay', SCRIPT)
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

class OverlayTests(unittest.TestCase):
    def make(self, text):
        td = tempfile.TemporaryDirectory(); root = pathlib.Path(td.name)
        (root/'project.godot').write_text(text)
        return td, root

    def test_patches_mobile_settings_and_overrides(self):
        td, root = self.make('[application]\nconfig/name="X"\n\n[display]\nwindow/handheld/orientation=1\nwindow/stretch/aspect="keep"\nwindow/size/window_width_override=1280\nwindow/size/window_height_override=720\n')
        try:
            r = mod.patch_project(root/'project.godot')
            s = (root/'project.godot').read_text()
            self.assertIn('window/handheld/orientation=4', s)
            self.assertIn('window/stretch/aspect="expand"', s)
            self.assertIn('window/size/window_width_override=0', s)
            self.assertIn('window/size/window_height_override=0', s)
            self.assertTrue(r['changed'])
        finally: td.cleanup()

    def test_adds_display_section_when_missing(self):
        td, root = self.make('[application]\nconfig/name="X"\n')
        try:
            mod.patch_project(root/'project.godot')
            s=(root/'project.godot').read_text()
            self.assertIn('[display]', s)
            self.assertIn('window/handheld/orientation=4', s)
            self.assertIn('window/stretch/aspect="expand"', s)
        finally: td.cleanup()

    def test_network_inventory_redacts_values(self):
        td, root = self.make('[display]\nwindow/handheld/orientation=4\nwindow/stretch/aspect="expand"\n')
        try:
            (root/'main.gd').write_text('var api="http://localhost:18080"\nvar x=OS.get_environment("THF_BASE_URL")\n')
            x=mod.endpoint_inventory(root)
            self.assertEqual(x['network_authority_gate'],'BLOCKED')
            self.assertTrue(x['endpoint_values_redacted'])
            self.assertIn('main.gd',x['placeholder_paths'])
            self.assertGreater(x['runtime_config_file_count'],0)
            self.assertNotIn('18080', json.dumps(x))
        finally: td.cleanup()

if __name__ == '__main__': unittest.main()
