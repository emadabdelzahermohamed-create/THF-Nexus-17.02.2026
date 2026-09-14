from ReleaseOps.TokenOps.blocker_resolution import (
    build_resolution_packet,
    summarize_required_authorizations,
    validate_evidence_record,
)


def _readiness(blockers):
    return {
        "network": "solana-mainnet-beta",
        "mint": "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv",
        "readiness_sha256": "a" * 64,
        "blockers": blockers,
    }


def test_current_authoritative_blockers_map_fail_closed():
    blockers = [
        "distribution_delivery_model_not_approved",
        "distribution_reserve_not_approved",
        "epoch_budget_cap_not_approved",
        "lock_rewards_terms_not_approved",
        "lock_terms_not_approved",
        "per_user_cap_not_approved",
        "policy_mutation_governance_not_approved",
        "production_signer_policy_not_approved",
        "revenue_value_basis_not_approved",
        "treasury_accounts_and_evidence_missing",
        "vesting_terms_not_approved",
    ]
    packet = build_resolution_packet(_readiness(blockers))
    assert packet["status"] == "FAIL_CLOSED"
    assert packet["blocker_count"] == 11
    assert packet["unknown_blockers"] == []
    assert packet["execution"]["execution_authorized"] is False
    assert packet["execution"]["transaction_bytes_created"] is False
    assert packet["execution"]["instruction_bytes_created"] is False
    assert packet["execution"]["signed"] is False
    assert packet["execution"]["broadcast"] is False
    assert packet["execution"]["financial_effect"] is False
    assert packet["execution"]["private_key_required"] is False
    assert packet["execution"]["wave_touched"] is False
    assert len(packet["packet_sha256"]) == 64


def test_packet_is_deterministic_and_deduplicates_blockers():
    a = build_resolution_packet(_readiness(["per_user_cap_not_approved", "epoch_budget_cap_not_approved", "per_user_cap_not_approved"]))
    b = build_resolution_packet(_readiness(["epoch_budget_cap_not_approved", "per_user_cap_not_approved"]))
    assert a == b
    assert a["blocker_count"] == 2


def test_unknown_blocker_remains_fail_closed():
    packet = build_resolution_packet(_readiness(["future_unknown_control_not_approved"]))
    assert packet["status"] == "FAIL_CLOSED"
    assert packet["unknown_blockers"] == ["future_unknown_control_not_approved"]
    assert packet["items"][0]["class"] == "unmapped_fail_closed"


def test_evidence_validator_rejects_secrets_and_bad_hashes():
    errors = validate_evidence_record({"private_key": "never", "governance_approval_sha256": "bad"})
    assert "forbidden_field:private_key" in errors
    assert "invalid_sha256:governance_approval_sha256" in errors


def test_evidence_validator_accepts_public_hash_metadata():
    assert validate_evidence_record({
        "owner_pubkey": "11111111111111111111111111111111",
        "ownership_evidence_sha256": "b" * 64,
        "balance_evidence_sha256": "c" * 64,
    }) == []


def test_authorization_summary_requests_no_signer_action_while_blocked():
    packet = build_resolution_packet(_readiness([
        "distribution_reserve_not_approved",
        "production_signer_policy_not_approved",
        "policy_mutation_governance_not_approved",
    ]))
    summary = summarize_required_authorizations(packet)
    assert summary["blocker_count"] == 3
    assert summary["signer_action_now"] == "NONE"
    assert summary["execution_authorized"] is False
    assert summary["broadcast"] is False
    assert summary["financial_effect"] is False
    assert len(summary["summary_sha256"]) == 64
