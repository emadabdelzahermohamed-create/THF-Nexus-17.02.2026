from resolution_dag import build_resolution_dag, summarize_resolution_dag


def readiness(blockers):
    return {
        "network": "solana-mainnet-beta",
        "mint": "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv",
        "readiness_sha256": "a" * 64,
        "blockers": blockers,
    }


def test_resolution_dag_orders_treasury_reserve_dependency():
    dag = build_resolution_dag(readiness([
        "distribution_reserve_not_approved",
        "treasury_accounts_and_evidence_missing",
        "per_user_cap_not_approved",
    ]))
    nodes = {n["blocker"]: n for n in dag["nodes"]}
    assert nodes["distribution_reserve_not_approved"]["depends_on"] == ["treasury_accounts_and_evidence_missing"]
    assert nodes["distribution_reserve_not_approved"]["ready_for_resolution_work"] is False
    assert nodes["treasury_accounts_and_evidence_missing"]["ready_for_resolution_work"] is True
    assert nodes["per_user_cap_not_approved"]["ready_for_resolution_work"] is True
    assert dag["signer_action_now"] == "NONE"
    assert dag["execution_authorized"] is False
    assert dag["broadcast"] is False
    assert dag["financial_effect"] is False
    assert dag["wave_touched"] is False


def test_lock_rewards_waits_for_lock_terms_when_both_open():
    dag = build_resolution_dag(readiness([
        "lock_rewards_terms_not_approved",
        "lock_terms_not_approved",
    ]))
    nodes = {n["blocker"]: n for n in dag["nodes"]}
    assert nodes["lock_rewards_terms_not_approved"]["depends_on"] == ["lock_terms_not_approved"]
    assert nodes["lock_terms_not_approved"]["depends_on"] == []


def test_unknown_blocker_is_fail_closed_and_visible():
    dag = build_resolution_dag(readiness(["future_unknown_blocker"]))
    assert dag["status"] == "FAIL_CLOSED"
    assert dag["unknown_blockers"] == ["future_unknown_blocker"]
    assert dag["nodes"][0]["class"] == "unmapped_fail_closed"
    assert dag["nodes"][0]["workstream"] == "manual_mapping_batch"


def test_summary_is_non_executable():
    dag = build_resolution_dag(readiness([
        "per_user_cap_not_approved",
        "revenue_value_basis_not_approved",
        "production_signer_policy_not_approved",
    ]))
    summary = summarize_resolution_dag(dag)
    assert summary["blocker_count"] == 3
    assert summary["immediately_actionable_count"] == 3
    assert summary["dependency_blocked_count"] == 0
    assert summary["signer_action_now"] == "NONE"
    assert summary["execution_authorized"] is False
    assert summary["financial_effect"] is False
