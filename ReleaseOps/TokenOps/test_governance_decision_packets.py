from governance_decision_packets import build_governance_decision_packets, validate_governance_decision_packets


def _dag():
    return {
        "network": "solana-mainnet-beta",
        "mint": "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv",
        "resolution_dag_sha256": "a" * 64,
        "nodes": [
            {
                "blocker": "per_user_cap_not_approved",
                "class": "governance_policy",
                "workstream": "governance_policy_batch",
                "depends_on": [],
                "ready_for_resolution_work": True,
                "requires_user_controlled_governance": True,
                "requires_public_evidence": False,
                "required_fields": ["per_user_cap_raw", "governance_approval_sha256"],
            },
            {
                "blocker": "distribution_reserve_not_approved",
                "class": "treasury_evidence",
                "workstream": "treasury_evidence_batch",
                "depends_on": ["treasury_accounts_and_evidence_missing"],
                "ready_for_resolution_work": False,
                "requires_user_controlled_governance": False,
                "requires_public_evidence": True,
                "required_fields": ["token_account", "balance_evidence_sha256"],
            },
        ],
        "dependency_blocked_resolution_work": ["distribution_reserve_not_approved"],
    }


def test_builds_only_dependency_free_draft_packets():
    bundle = build_governance_decision_packets(_dag())
    assert bundle["packet_count"] == 1
    assert bundle["packets"][0]["blocker"] == "per_user_cap_not_approved"
    assert bundle["packets"][0]["decision_status"] == "DRAFT_REQUIRED"
    assert bundle["packets"][0]["decision_values"] == {
        "per_user_cap_raw": None,
        "governance_approval_sha256": None,
    }
    assert bundle["signer_action_now"] == "NONE"
    assert validate_governance_decision_packets(bundle) == []


def test_validator_rejects_autofilled_economic_value():
    bundle = build_governance_decision_packets(_dag())
    bundle["packets"][0]["decision_values"]["per_user_cap_raw"] = 123
    errors = validate_governance_decision_packets(bundle)
    assert "autofilled_decision_value:per_user_cap_not_approved" in errors


def test_validator_rejects_execution_flags():
    bundle = build_governance_decision_packets(_dag())
    bundle["broadcast"] = True
    bundle["packets"][0]["execution"]["signed"] = True
    errors = validate_governance_decision_packets(bundle)
    assert "unsafe_bundle_flag:broadcast" in errors
    assert "unsafe_packet_flag:per_user_cap_not_approved:signed" in errors


def test_hash_is_deterministic():
    one = build_governance_decision_packets(_dag())
    two = build_governance_decision_packets(_dag())
    assert one["decision_packet_root_sha256"] == two["decision_packet_root_sha256"]
