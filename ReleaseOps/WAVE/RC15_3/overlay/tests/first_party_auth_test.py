import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class FirstPartyAuthSourceTest(unittest.TestCase):
    def test_first_party_auth_replaces_external_chatgpt_redirect(self):
        auth = (ROOT / "app" / "chatgpt-auth.ts").read_text(encoding="utf-8")
        self.assertIn('/login?return_to=', auth)
        self.assertIn('waveUserFromToken', auth)
        self.assertNotIn('/signin-with-chatgpt', auth)

    def test_credentials_are_derived_and_sessions_are_http_only(self):
        lib = (ROOT / "lib" / "wave-auth.ts").read_text(encoding="utf-8")
        self.assertIn('PBKDF2', lib)
        self.assertIn('100_000', lib)
        self.assertNotIn('210_000', lib)
        self.assertIn('HttpOnly; Secure; SameSite=Lax', lib)
        migration = (ROOT / "drizzle" / "0011_wave_first_party_auth.sql").read_text(encoding="utf-8")
        self.assertIn('wave_credentials', migration)
        self.assertIn('wave_sessions', migration)

if __name__ == '__main__':
    unittest.main()
