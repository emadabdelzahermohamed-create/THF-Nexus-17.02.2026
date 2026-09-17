#!/usr/bin/env python3
from app.db import (
    init_db,
    create_user,
    create_social_auth_attempt,
    get_social_auth_attempt_by_state,
    link_social_account,
    get_social_link,
    complete_social_auth_attempt,
    consume_social_auth_attempt,
    social_links,
)
from app.passwords import hash_password
from app.main import app


def main() -> int:
    init_db()
    uid = create_user("socialgate", hash_password("password123"), "en")
    attempt = create_social_auth_attempt(
        "gate-attempt",
        "google",
        "gate-state",
        "gate-verifier",
        "web",
        None,
        600,
    )
    assert attempt["status"] == "pending"
    assert get_social_auth_attempt_by_state("google", "gate-state")["attempt_id"] == "gate-attempt"
    link_social_account(
        uid,
        "google",
        "gate-subject",
        "gate@example.test",
        True,
        "Gate User",
    )
    assert get_social_link("google", "gate-subject")["user_id"] == uid
    complete_social_auth_attempt("gate-attempt", uid)
    consumed = consume_social_auth_attempt("gate-attempt")
    assert consumed.get("_consumed_now") is True
    assert social_links(uid)[0]["provider"] == "google"
    paths = {getattr(route, "path", "") for route in app.routes}
    for path in (
        "/api/auth/providers",
        "/api/auth/oauth/start",
        "/api/auth/oauth/{provider}/callback",
        "/api/auth/oauth/status/{attempt_id}",
        "/api/account/links",
    ):
        assert path in paths, path
    print("TERRA_SOCIAL_AUTH_DB_AND_ROUTE_GATE=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
