"""External regression pack bound to Spark RC3 source SHA256
`dc312dc65e681e914c3421a20362cd0fba0c1e692a7becdb66d7d17a0b6299a0`.

This pack intentionally exercises the exact archived source without mutating the
canonical archive. It is not physical-device evidence and must not promote
FINAL/PLAY_READY.
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


def test_health_is_real_and_non_demo_contract_shape():
    r = client.get('/health')
    assert r.status_code == 200
    body = r.json()
    assert body.get('status') == 'ok'
    assert isinstance(body.get('games'), int) and body['games'] > 0
    assert 'demo' in body


def test_catalog_exposes_real_learning_game_inventory():
    r = client.get('/catalog')
    assert r.status_code == 200
    body = r.json()
    assert body.get('downloadable_modules') is True
    assert body.get('infinite_levels')
    assert isinstance(body.get('items'), list) and len(body['items']) > 0


def test_seeded_level_is_deterministic():
    game = _catalog_first_game()
    assert game
    params = {'level': 7, 'seed': 'regression-seed-2026'}
    a = client.get(f'/level/{game}', params=params)
    b = client.get(f'/level/{game}', params=params)
    assert a.status_code == b.status_code == 200
    assert a.json() == b.json()


def test_score_mutation_fails_closed_without_identity():
    game = _catalog_first_game()
    r = client.post('/scores', json={
        'game_id': game,
        'score': 10,
        'level': 1,
        'seed': 'seed-1234',
        'duration_ms': 1000,
    })
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


def test_ai_proposal_creation_fails_closed_without_identity():
    r = client.post('/ai/proposals', json={
        'title': 'Safe learning proposal',
        'audience': 'all',
        'learning_goal': 'Practice a measurable learning objective',
        'mechanic': 'Use deterministic progression with review before publication',
    })
    assert r.status_code in (401, 403), r.text
