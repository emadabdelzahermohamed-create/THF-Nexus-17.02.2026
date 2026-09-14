from ReleaseOps.TokenOps.holder_concentration_probe import summarize_largest_accounts


def test_summarize_largest_accounts_bps():
    supply = 1_000_000
    accounts = [
        {"address": f"acct{i}", "amount": str(amount), "decimals": 8, "uiAmountString": str(amount)}
        for i, amount in enumerate([250_000, 150_000, 100_000, 50_000, 50_000, 40_000])
    ]
    out = summarize_largest_accounts(accounts, supply)
    assert out["account_count"] == 6
    assert out["top1_bps"] == 2500
    assert out["top5_bps"] == 6000
    assert out["top20_bps"] == 6400


def test_summarize_empty_accounts():
    out = summarize_largest_accounts([], 1_000_000)
    assert out["account_count"] == 0
    assert out["top1_bps"] is None
    assert out["top5_bps"] == 0
    assert out["top20_bps"] == 0
    assert out["top_accounts"] == []
