from ReleaseOps.TokenOps.epoch_commitment import (
    build_double_entry_preview,
    build_epoch_commitment,
    deterministic_capped_allocation,
)

MINT = "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"


def approved_policy():
    return {
        "network": "solana-mainnet-beta",
        "mint": MINT,
        "economics": {"active_user_revenue_share_bps": 3500},
        "distribution_controls": {
            "per_user_cap_raw": 100,
            "epoch_budget_cap_raw": 1000,
            "distribution_reserve_account": "public-account-ref",
            "delivery_model": "claim",
        },
    }


def treasury_ok(distribution_reserve="1000"):
    return {
        "status": "PASS",
        "role_balances_raw": {"distribution_reserve": distribution_reserve},
    }


def test_deterministic_allocation_conserves_and_sorts():
    rows = [
        {"subject_ref": "user-c", "activity_units": 1},
        {"subject_ref": "user-a", "activity_units": 1},
        {"subject_ref": "user-b", "activity_units": 1},
    ]
    out = deterministic_capped_allocation(10, 10, rows)
    assert out["conservation"] is True
    assert out["allocated_raw"] == 10
    assert out["unallocated_raw"] == 0
    assert [x["subject_ref"] for x in out["allocations"]] == ["user-a", "user-b", "user-c"]
    assert [x["amount_raw"] for x in out["allocations"]] == [4, 3, 3]


def test_cap_can_leave_unallocated_budget_without_overpaying():
    rows = [
        {"subject_ref": "a", "activity_units": 99},
        {"subject_ref": "b", "activity_units": 1},
    ]
    out = deterministic_capped_allocation(100, 40, rows)
    assert all(x["amount_raw"] <= 40 for x in out["allocations"])
    assert out["allocated_raw"] <= 80
    assert out["conservation"] is True


def test_epoch_commitment_fail_closed_on_current_unapproved_controls():
    policy = approved_policy()
    policy["distribution_controls"]["per_user_cap_raw"] = None
    out = build_epoch_commitment(
        policy,
        treasury_ok(),
        "epoch-1",
        1000,
        [{"subject_ref": "u1", "activity_units": 1}],
        ["0" * 64],
    )
    assert out["status"] == "FAIL_CLOSED"
    assert "per_user_cap_raw_not_approved" in out["blockers"]
    assert out["execution_authorized"] is False
    assert out["broadcast"] is False
    assert out["financial_effect"] is False


def test_epoch_commitment_caps_by_35_percent_epoch_and_reserve():
    policy = approved_policy()
    policy["distribution_controls"]["per_user_cap_raw"] = 1000
    policy["distribution_controls"]["epoch_budget_cap_raw"] = 500
    out = build_epoch_commitment(
        policy,
        treasury_ok("300"),
        "epoch-2",
        2000,
        [
            {"subject_ref": "u1", "activity_units": 1},
            {"subject_ref": "u2", "activity_units": 2},
        ],
        ["1" * 64, "2" * 64],
    )
    # 35% of 2000 = 700; epoch cap = 500; reserve = 300 -> 300 effective.
    assert out["approved_pool_minor"] == 700
    assert out["effective_budget_raw"] == 300
    assert out["allocation"]["allocated_raw"] == 300
    assert out["status"] == "REVIEW_READY_NOT_EXECUTION_READY"
    assert out["transaction_bytes_created"] is False
    assert out["instruction_bytes_created"] is False


def test_accounting_preview_is_balanced_and_unposted():
    packet = build_epoch_commitment(
        approved_policy(),
        treasury_ok(),
        "epoch-3",
        1000,
        [{"subject_ref": "u1", "activity_units": 1}],
        ["a" * 64],
    )
    preview = build_double_entry_preview(packet)
    assert preview["balanced"] is True
    assert preview["debits_raw"] == preview["credits_raw"]
    assert preview["posted"] is False
    assert preview["financial_effect"] is False


def test_sensitive_material_is_rejected():
    try:
        build_epoch_commitment(
            approved_policy(),
            treasury_ok(),
            "epoch-secret",
            100,
            [{"subject_ref": "u", "activity_units": 1, "private_key": "never"}],
            ["b" * 64],
        )
    except ValueError as exc:
        assert "forbidden sensitive field" in str(exc)
    else:
        raise AssertionError("private key material must be rejected")
