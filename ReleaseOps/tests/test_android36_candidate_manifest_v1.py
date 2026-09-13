import importlib.util,pathlib,tempfile,unittest,xml.etree.ElementTree as ET

P=pathlib.Path(__file__).parents[1]/'games_factory/patch_android36_predictive_back_v1.py'
S=importlib.util.spec_from_file_location('patcher',P);M=importlib.util.module_from_spec(S);S.loader.exec_module(M)
NS=M.ANDROID_NS
N='{%s}name'%NS; R='{%s}required'%NS; BACK='{%s}enableOnBackInvokedCallback'%NS

class Android36ManifestTests(unittest.TestCase):
 def make(self,body):
  td=tempfile.TemporaryDirectory(); root=pathlib.Path(td.name); p=root/'app/src/main/AndroidManifest.xml'; p.parent.mkdir(parents=True)
  p.write_text('<?xml version="1.0" encoding="utf-8"?><manifest xmlns:android="%s" package="x">%s<application/></manifest>'%(NS,body),encoding='utf-8')
  return td,root,p
 def test_camera_permission_adds_optional_feature(self):
  td,r,p=self.make('<uses-permission android:name="android.permission.CAMERA"/>')
  try:
   M.patch_manifest(r); x=ET.parse(p).getroot(); app=x.find('application'); self.assertEqual(app.attrib[BACK],'true')
   f=[e for e in x.findall('uses-feature') if e.attrib.get(N)=='android.hardware.camera']; self.assertEqual(len(f),1); self.assertEqual(f[0].attrib.get(R),'false')
  finally: td.cleanup()
 def test_existing_required_camera_is_downgraded_to_optional(self):
  td,r,p=self.make('<uses-permission android:name="android.permission.CAMERA"/><uses-feature android:name="android.hardware.camera" android:required="true"/>')
  try:
   M.patch_manifest(r); x=ET.parse(p).getroot(); f=[e for e in x.findall('uses-feature') if e.attrib.get(N)=='android.hardware.camera']; self.assertEqual(len(f),1); self.assertEqual(f[0].attrib.get(R),'false')
  finally: td.cleanup()
 def test_no_camera_permission_does_not_invent_feature(self):
  td,r,p=self.make('')
  try:
   M.patch_manifest(r); x=ET.parse(p).getroot(); self.assertFalse([e for e in x.findall('uses-feature') if e.attrib.get(N)=='android.hardware.camera']); self.assertEqual(x.find('application').attrib[BACK],'true')
  finally: td.cleanup()

if __name__=='__main__': unittest.main()
