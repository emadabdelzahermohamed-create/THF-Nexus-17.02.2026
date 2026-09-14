from ReleaseOps.TokenOps.rpc_capability_probe import rpc_candidates, select_first_capable


def test_rpc_candidates_deduplicates_and_keeps_public_fallback():
    env = {
        "SOLANA_RPC_URL": "https://primary.example/key",
        "SOLANA_RPC_FALLBACK_URLS": "https://backup.example/a;https://primary.example/key\nhttps://backup2.example/b",
    }
    out = rpc_candidates(env)
    assert out[0] == "https://primary.example/key"
    assert out[1] == "https://backup.example/a"
    assert out[2] == "https://backup2.example/b"
    assert out[-1] == "https://api.mainnet-beta.solana.com"
    assert len(out) == 4


def test_select_first_capable_requires_all_methods():
    rows = [
        {
            "candidate_index": 0,
            "capabilities": {
                "getTokenSupply": {"ok": True},
                "getTokenLargestAccounts": {"ok": False},
            },
        },
        {
            "candidate_index": 1,
            "capabilities": {
                "getTokenSupply": {"ok": True},
                "getTokenLargestAccounts": {"ok": True},
            },
        },
    ]
    assert select_first_capable(rows, ("getTokenSupply", "getTokenLargestAccounts")) == 1
    assert select_first_capable(rows, ("getHealth",)) is None
