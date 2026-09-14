from governance_decision_validation import (
    build_decision_evidence_review,
    validate_decision_evidence_review,
)


def _bundle(required_fields=None, blocker="per_user_cap_not_approved"):
    required_fields = required_fields or ["per_user_cap_raw", "governance_approval_sha256"]
    return {
        "network": "solana-mainnet-beta",
        "mint": "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv",
        "decision_packet_root_sha256": "a" * 64,
        "packets": [
            {
                "blocker": blocker,
                "packet_sha256": "b" * 64,
                "required_fields": required_fields,
            }
        ],
    }


def test_empty_inputs_remain_review_inputs_required():
    review = build_decision_evidence_review(_bundle(), {})
    assert review["status"] == "REVIEW_INPUTS_REQUIRED"
    assert review["inputs_missing_count"] == 1
    assert review["packet_reviews"][0]["missing_fields"] == [
        "governance_approval_sha256",
        "per_user_cap_raw",
    ]
    assert review["execution_authorized"] is False
    assert review["signer_action_now"] == "NONE"
    assert validate_decision_evidence_review(review) == []


def test_complete_shape_is_reviewable_but_never_authorized():
    review = build_decision_evidence_review(
        _bundle(),
        {
            "per_user_cap_not_approved": {
                "per_user_cap_raw": 100_000_000,
                "governance_approval_sha256": "c" * 64,
            }
        },
    )
    assert review["status"] == "REVIEWABLE_EVIDENCE_COMPLETE_NOT_AUTHORIZED"
    item = review["packet_reviews"][0]
    assert item["status"] == "REVIEWABLE_EVIDENCE_COMPLETE"
    assert item["governance_evidence_authenticity_verified"] is False
    assert item["execution_authorized"] is False
    assert review["important_semantics"]["sha256_presence_is_not_governance_approval"] is True
    assert validate_decision_evidence_review(review) == []


def test_invalid_hash_fails_closed():
    review = build_decision_evidence_review(
        _bundle(),
        {
            "per_user_cap_not_approved": {
                "per_user_cap_raw": 1,
                "governance_approval_sha256": "not-a-sha",
            }
        },
    )
    assert review["status"] == "FAIL_CLOSED_INVALID"
    assert "invalid_sha256:governance_approval_sha256" in review["packet_reviews"][0]["validation_errors"]


def test_secret_and_executable_fields_are_rejected():
    review = build_decision_evidence_review(
        _bundle(),
        {
            "per_user_cap_not_approved": {
                "per_user_cap_raw": 1,
                "governance_approval_sha256": "d" * 64,
                "private_key": "forbidden",
            }
        },
    )
    assert review["status"] == "FAIL_CLOSED_INVALID"
    errors = review["packet_reviews"][0]["validation_errors"]
    assert "unexpected_field:private_key" in errors
    assert any(error.startswith("forbidden_field:") for error in errors)


def test_public_treasury_fields_validate_without_private_material():
    bundle = _bundle(
        [
            "token_account",
            "owner_pubkey",
            "balance_raw",
            "observed_slot",
            "ownership_evidence_sha256",
            "balance_evidence_sha256",
        ],
        "distribution_reserve_not_approved",
    )
    pubkey = "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
    review = build_decision_evidence_review(
        bundle,
        {
            "distribution_reserve_not_approved": {
                "token_account": pubkey,
                "owner_pubkey": pubkey,
                "balance_raw": 0,
                "observed_slot": 1,
                "ownership_evidence_sha256": "e" * 64,
                "balance_evidence_sha256": "f" * 64,
            }
        },
    )
    assert review["status"] == "REVIEWABLE_EVIDENCE_COMPLETE_NOT_AUTHORIZED"
    assert review["private_key_required"] is False
    assert review["financial_effect"] is False


def test_value_basis_window_must_increase():
    bundle = _bundle(
        ["denomination", "method", "source_evidence_sha256", "governance_approval_sha256", "valid_from_utc", "valid_until_utc"],
        "revenue_value_basis_not_approved",
    )
    review = build_decision_evidence_review(
        bundle,
        {
            "revenue_value_basis_not_approved": {
                "denomination": "USD",
                "method": "governance-approved-observation",
                "source_evidence_sha256": "1" * 64,
                "governance_approval_sha256": "2" * 64,
                "valid_from_utc": "2026-09-14T12:00:00Z",
                "valid_until_utc": "2026-09-14T11:00:00Z",
            }
        },
    )
    assert review["status"] == "FAIL_CLOSED_INVALID"
    assert "invalid_validity_window:not_strictly_increasing" in review["packet_reviews"][0]["validation_errors"]
