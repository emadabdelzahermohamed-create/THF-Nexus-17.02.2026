import os, unittest
from ReleaseOps.SocialControlPlane.secret_refs import resolve, SecretRefError
from ReleaseOps.SocialControlPlane.retry import classify

class RuntimeGuardTests(unittest.TestCase):
    def test_raw_secret_rejected(self):
        with self.assertRaises(SecretRefError): resolve('abc123')
    def test_env_secret_resolved(self):
        os.environ['THF_TEST_SECRET']='ok'
        self.assertEqual(resolve('env:THF_TEST_SECRET'),'ok')
    def test_429_retries(self):
        d=classify(429,1,17); self.assertTrue(d.retry); self.assertEqual(d.delay_seconds,17)
    def test_auth_failure_permanent(self):
        self.assertFalse(classify(401,1).retry)
