import unittest
from ReleaseOps.SocialControlPlane.cost_guard import Route, choose

class CostTests(unittest.TestCase):
    def test_free_sustainable_route_wins(self):
        r = choose([Route("paid", .02, True, "api"), Route("direct", 0, True, "quota")])
        self.assertEqual(r.provider, "direct")
