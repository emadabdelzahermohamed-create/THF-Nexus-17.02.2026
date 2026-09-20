extends Node

signal reward_claim_queued(payload: Dictionary)
signal status_changed(status: String)

var api_base := ""
var session_token := ""

func _ready() -> void:
    var env_base := OS.get_environment("THF_API_BASE")
    if not env_base.is_empty():
        api_base = env_base.trim_suffix("/")
    status_changed.emit(get_status())

func set_session_token(token: String) -> void:
    session_token = token

func set_api_base(value: String) -> void:
    api_base = value.strip_edges().trim_suffix("/")
    status_changed.emit(get_status())

func get_status() -> String:
    if api_base.is_empty():
        return "THF bridge ready; live API endpoint not configured"
    if session_token.is_empty():
        return "THF API configured; waiting for player session"
    return "THF bridge online"

func claim_farm_reward(amount: int, evidence: Dictionary = {}) -> bool:
    var payload := {
        "source": "ruinsciv_farm",
        "amount": amount,
        "evidence": evidence,
        "client_ts": Time.get_unix_time_from_system()
    }
    reward_claim_queued.emit(payload)
    if api_base.is_empty() or session_token.is_empty():
        return false

    var request := HTTPRequest.new()
    add_child(request)
    request.request_completed.connect(func(_result, _code, _headers, _body):
        request.queue_free()
    )
    var headers := [
        "Content-Type: application/json",
        "Authorization: Bearer " + session_token
    ]
    var err := request.request(
        api_base + "/v1/ruinsciv/rewards/claim",
        headers,
        HTTPClient.METHOD_POST,
        JSON.stringify(payload)
    )
    if err != OK:
        request.queue_free()
        return false
    return true
