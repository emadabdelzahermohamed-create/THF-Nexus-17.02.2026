import unittest

from ReleaseOps.FitnessStandalone.backend_openapi_contract import analyze_openapi


SECURITY = [{"bearerAuth": []}]


def operation(*, secured=True):
    return {"responses": {"200": {"description": "ok"}}, "security": SECURITY if secured else []}


GOOD_SPEC = {
    "openapi": "3.1.0",
    "security": SECURITY,
    "components": {
        "securitySchemes": {"bearerAuth": {"type": "http", "scheme": "bearer"}},
        "schemas": {
            "SetProof": {"properties": {"expectedSet": {}, "acceptedSet": {}}},
            "HealthRecord": {"properties": {"provenance": {}, "sourceId": {}}},
        },
    },
    "paths": {
        "/api/auth/login": {"post": operation(secured=False)},
        "/api/auth/logout": {"post": operation()},
        "/api/session": {"get": operation()},
        "/api/account": {"delete": operation()},
        "/api/sync": {"post": operation()},
        "/api/reports": {"get": operation()},
        "/api/health/records": {"post": operation()},
        "/api/workouts/{id}/sets": {"post": operation()},
        "/api/workouts/{id}/proof": {"post": operation()},
    },
}


class FitnessBackendOpenApiContractTests(unittest.TestCase):
    def test_complete_release_contract_reports_progress(self):
        report = analyze_openapi(GOOD_SPEC, "a" * 64, "2026-09-26T18:00:00Z")
        self.assertEqual(report["result"], "PROGRESS")
        self.assertEqual(report["issues"], [])
        self.assertEqual(report["route_count"], 9)

    def test_public_surface_without_auth_sync_or_health_ingestion_blocks(self):
        spec = {
            "openapi": "3.1.0",
            "paths": {
                "/health": {"get": operation(secured=False)},
                "/api/progress/{user_id}": {"get": operation(secured=False)},
                "/api/workouts/{id}/sets": {"post": operation(secured=False)},
            },
        }
        report = analyze_openapi(spec, "b" * 64, "2026-09-26T18:00:00Z")
        self.assertEqual(report["result"], "BLOCKED")
        self.assertIn("AUTH_LOGIN_ROUTE_MISSING", report["issues"])
        self.assertIn("HEALTH_INGESTION_ROUTE_MISSING", report["issues"])
        self.assertIn("OPENAPI_SECURITY_SCHEME_MISSING", report["issues"])

    def test_evidence_excludes_schema_bodies(self):
        report = analyze_openapi(GOOD_SPEC, "c" * 64, "2026-09-26T18:00:00Z")
        self.assertNotIn("components", report)
        self.assertNotIn("schemas", report)


if __name__ == "__main__":
    unittest.main()
