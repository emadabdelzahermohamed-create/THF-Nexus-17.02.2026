"""External regression pack bound to Rush RC3 source SHA256
`bd7e365ded07fd569020fff1c699d74322fd5c767b16ac6336f2bc99f8b5958b`.

This pack exercises exact archived source behavior without mutating the canonical
archive. It is not physical-device evidence and must not promote FINAL/PLAY_READY.
"""
from fastapi.testclient import TestClient

from appsrc.app import app

client = TestClient(app)


def _catalog_first_game():
    r = client.get('/catalog')
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body.get('items'), list) and body['items']
    first = body['items'][0]
    if isinstance(first, dict):
        return first.get('id') or first.get('game_id') or first.get('slug') or first.get('key')
    return first


def test_health_and_anticheat_capabilities_are_explicit():
    r = client.get('/health')
    assert r.status_code == 200
    body = r.json()
    assert body.get('status') == 'ok'
    assert isinstance(body.get('games'), int) and body['games'] > 0
    anti = body.get('anti_cheat')
    assert isinstance(anti, dict)
    assert anti.get('challenge_nonce') is True
    assert anti.get('replay_fingerprint') is True


def test_catalog_enforces_no_pay_to_win_policy_text():
    r = client.get('/catalog')
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body.get('items'), list) and body['items']
    policy = str(body.get('ranked_policy', '')).lower()
    assert 'no pay-to-win' in policy


def test_anticheat_endpoint_is_truthful_not_perfect_detection_claim():
    r = client.get('/anti-cheat')
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body.get('signals'), list) and len(body['signals']) >= 5
    assert 'no claim of perfect detection' in str(body.get('decision', '')).lower()
    assert 'minimum evidence' in str(body.get('privacy', '')).lower()


def test_session_creation_fails_closed_without_identity():
    game = _catalog_first_game()
    r = client.post('/sessions', json={'game_id': game})
    assert r.status_code in (401, 403), r.text


def test_league_creation_fails_closed_without_identity():
    game = _catalog_first_game()
    r = client.post('/leagues', json={
        'name': 'Regression League',
        'game_id': game,
        'entry_units': 0,
        'prize_pool_units': 0,
    })
    assert r.status_code in (401, 403), r.text


def test_leaderboard_is_read_only_and_reachable():
    game = _catalog_first_game()
    r = client.get(f'/leaderboard/{game}')
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, dict)
