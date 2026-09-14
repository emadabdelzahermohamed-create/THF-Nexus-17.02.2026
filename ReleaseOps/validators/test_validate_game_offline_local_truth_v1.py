#!/usr/bin/env python3
import importlib.util, pathlib, tempfile, unittest

HERE=pathlib.Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location('v',HERE/'validate_game_offline_local_truth_v1.py')
v=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(v)

GOOD='''Choreographer postFrameCallback onTouchEvent GameView\nOFFLINE_AUTHORITY=LOCAL_ONLY_NO_RANKED_SOCIAL_ECONOMY_MUTATION\nREADINESS_PROMOTION=NO\nranked/social/economy state is never fabricated offline\nscore streak level nextQuestion SensorManager SensorEventListener reps mastery repCount setCount\n'''

class Tests(unittest.TestCase):
    def run_audit(self,text,family):
        with tempfile.TemporaryDirectory() as td:
            p=pathlib.Path(td)/'x.py';p.write_text(text)
            return v.audit(p,family)
    def test_spark_rush_good(self): self.assertTrue(self.run_audit(GOOD,'spark_rush')['passed'])
    def test_learn_fitness_good(self): self.assertTrue(self.run_audit(GOOD,'learn_fitness')['passed'])
    def test_network_transport_rejected(self):
        r=self.run_audit(GOOD+'\nHttpURLConnection\n','spark_rush');self.assertFalse(r['passed']);self.assertFalse(r['checks']['no_network_transport_in_overlay_generator'])
    def test_api_endpoint_rejected(self):
        r=self.run_audit(GOOD+'\n/api/economy/internal-award\n','learn_fitness');self.assertFalse(r['passed'])
    def test_persistence_rejected(self):
        r=self.run_audit(GOOD+'\nSharedPreferences\n','learn_fitness');self.assertFalse(r['passed']);self.assertFalse(r['checks']['no_persistent_fake_authority_state'])
    def test_missing_no_promotion_rejected(self):
        r=self.run_audit(GOOD.replace('READINESS_PROMOTION=NO',''),'spark_rush');self.assertFalse(r['passed'])
    def test_missing_sensor_rejected(self):
        r=self.run_audit(GOOD.replace('SensorManager',''),'spark_rush');self.assertFalse(r['passed'])

if __name__=='__main__':unittest.main()
