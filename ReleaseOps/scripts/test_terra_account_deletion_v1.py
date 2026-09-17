#!/usr/bin/env python3
from pathlib import Path

from app.db import (
    db,
    init_db,
    create_user,
    get_user,
    link_social_account,
    social_links,
    delete_user_account,
)
from app.passwords import hash_password
from app.main import app


def main() -> int:
    init_db()
    uid = create_user("deletegate", hash_password("password123"), "en")
    link_social_account(uid, "google", "delete-gate-subject", "delete@example.test", True, "Delete Gate")
    now = 1_800_000_000
    with db() as c:
        c.execute("INSERT INTO card_draws(user_id,day,draws) VALUES(?,?,?)", (uid, "2026-09-17", 1))
        c.execute("INSERT INTO catches(user_id,fish_id,rod_id,reward,caught_at) VALUES(?,?,?,?,?)", (uid, "gate_fish", "wood", 1, now))
        c.execute("INSERT INTO payments(user_id,tx_signature,item_id,amount,status,created_at) VALUES(?,?,?,?,?,?)", (uid, "delete-gate-tx", "gate_item", 1.0, "test", now))
        c.execute("INSERT INTO audit_log(actor,action,details,created_at) VALUES(?,?,?,?)", ("deletegate", "gate", "gate", now))
    result = delete_user_account(uid, "deletegate")
    assert result["deleted_user_id"] == uid
    assert get_user(uid) is None
    assert social_links(uid) == []
    with db() as c:
        for table in ("card_draws", "catches", "payments"):
            assert c.execute(f"SELECT COUNT(*) AS n FROM {table} WHERE user_id=?", (uid,)).fetchone()["n"] == 0, table
        assert c.execute("SELECT COUNT(*) AS n FROM audit_log WHERE actor=?", ("deletegate",)).fetchone()["n"] == 0
    paths = {getattr(route, "path", "") for route in app.routes}
    assert "/api/account/delete" in paths
    assert "/account-delete" in paths
    assert Path("web/templates/account_delete.html").is_file()
    print("TERRA_ACCOUNT_DELETION_GATE=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
