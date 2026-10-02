package com.topherofit.thf.pulse

import java.io.ByteArrayOutputStream
import java.net.URL
import java.nio.charset.StandardCharsets
import java.security.MessageDigest
import javax.net.ssl.HttpsURLConnection
import org.json.JSONArray
import org.json.JSONObject

data class BackendSyncReceipt(
    val result: String,
    val clientRecordId: String,
    val serverRevision: Long,
)

class BackendSyncException(message: String, val statusCode: Int? = null) : Exception(message)

/**
 * Native HTTPS boundary for the shared Fitness account/workout API.
 *
 * Access tokens are intentionally supplied by the account UI at runtime and are never
 * persisted by this class. Offline records remain queued until both an approved HTTPS
 * endpoint and a short-lived account token are available.
 */
class BackendSyncRepository(baseUrl: String) {
    companion object {
        private const val MAX_RESPONSE_BYTES = 64 * 1024
        private val ALLOWED_SET_TYPES = setOf("warmup", "working", "drop", "failure")
    }

    private val endpoint: URL? = parseEndpoint(baseUrl)

    val configured: Boolean get() = endpoint != null

    fun validateAccessToken(value: String): String {
        val token = value.trim()
        require(token.length in 32..8192 && token.count { it == '.' } == 2 && token.none { it.isWhitespace() }) {
            "invalid short-lived access token"
        }
        return token
    }

    fun workoutPayload(summary: JSONObject): JSONObject {
        val clientRecordId = summary.getString("clientRecordId")
        require(clientRecordId.matches(Regex("[A-Za-z0-9._:-]{8,120}"))) { "invalid clientRecordId" }
        val startedAt = summary.getLong("startedAtMs")
        val endedAt = summary.getLong("endedAtMs")
        require(startedAt > 0 && endedAt > startedAt) { "invalid workout time" }
        val exerciseId = summary.optString("id", "other").take(120).ifBlank { "other" }
        val sport = summary.optString("sport", exerciseId).take(80).ifBlank { "other" }
        val sourceSets = summary.optJSONArray("sets") ?: JSONArray()
        val sets = JSONArray()
        for (index in 0 until sourceSets.length()) {
            val item = sourceSets.optJSONObject(index) ?: continue
            if (!item.optBoolean("complete", false)) continue
            val type = item.optString("type", "working").let { if (it in ALLOWED_SET_TYPES) it else "working" }
            sets.put(
                JSONObject()
                    .put("exerciseId", exerciseId)
                    .put("ordinal", sets.length() + 1)
                    .put("setType", type)
                    .put("reps", item.optInt("reps", 0).coerceIn(0, 10_000))
                    .put("loadKg", boundedNumber(item.optDouble("load", 0.0), 0.0, 100_000.0))
                    .put("restSeconds", item.optInt("restSeconds", 0).coerceIn(0, 86_400))
                    .put("rpe", optionalEffort(item, "rpe"))
                    .put("rir", optionalEffort(item, "rir")),
            )
        }
        return JSONObject()
            .put("clientRecordId", clientRecordId)
            .put("clientRecordVersion", summary.optLong("recordVersion", 1L).coerceAtLeast(1L))
            .put("startedAt", java.time.Instant.ofEpochMilli(startedAt).toString())
            .put("endedAt", java.time.Instant.ofEpochMilli(endedAt).toString())
            .put("sport", sport)
            .put("exerciseSessionType", HealthSportMapper.toExerciseType(sport, exerciseId))
            .put("source", "THF_ANDROID")
            .put("provenancePackage", "com.topherofit.thf.pulse")
            .put("sets", sets)
    }

    fun sync(accessToken: String, summary: JSONObject): BackendSyncReceipt {
        val target = endpoint ?: throw BackendSyncException("Production backend endpoint is not configured")
        val token = validateAccessToken(accessToken)
        val payload = workoutPayload(summary)
        val raw = payload.toString().toByteArray(StandardCharsets.UTF_8)
        val recordId = payload.getString("clientRecordId")
        val version = payload.getLong("clientRecordVersion")
        val idempotencyKey = idempotencyKey(recordId, version)
        val connection = (target.openConnection() as HttpsURLConnection).apply {
            requestMethod = "POST"
            instanceFollowRedirects = false
            connectTimeout = 10_000
            readTimeout = 10_000
            doOutput = true
            setFixedLengthStreamingMode(raw.size)
            setRequestProperty("Accept", "application/json")
            setRequestProperty("Content-Type", "application/json")
            setRequestProperty("Authorization", "Bearer $token")
            setRequestProperty("Idempotency-Key", idempotencyKey)
        }
        return try {
            connection.outputStream.use { it.write(raw) }
            val status = connection.responseCode
            val response = readBounded(if (status in 200..299) connection.inputStream else connection.errorStream)
            if (status != 200) {
                throw BackendSyncException("Workout sync failed with HTTP $status", status)
            }
            val document = JSONObject(response)
            if (document.optString("clientRecordId") != recordId) {
                throw BackendSyncException("Workout sync receipt identity mismatch", status)
            }
            val result = document.optString("result")
            if (result !in setOf("inserted", "updated", "duplicate", "stale") ||
                document.optLong("serverRevision", -1L) != version
            ) {
                throw BackendSyncException("Workout sync receipt contract mismatch", status)
            }
            BackendSyncReceipt(
                result = result,
                clientRecordId = recordId,
                serverRevision = version,
            )
        } finally {
            connection.disconnect()
        }
    }

    private fun optionalEffort(item: JSONObject, key: String): Any {
        if (!item.has(key) || item.isNull(key)) return JSONObject.NULL
        val value = item.optDouble(key, Double.NaN)
        return if (value.isFinite() && value in 0.0..10.0) value else JSONObject.NULL
    }

    private fun boundedNumber(value: Double, minimum: Double, maximum: Double): Double =
        if (value.isFinite()) value.coerceIn(minimum, maximum) else minimum

    private fun idempotencyKey(recordId: String, version: Long): String {
        val digest = MessageDigest.getInstance("SHA-256")
            .digest("$recordId:$version".toByteArray(StandardCharsets.UTF_8))
            .joinToString("") { "%02x".format(it) }
        return "android-${digest.take(48)}"
    }

    private fun readBounded(stream: java.io.InputStream?): String {
        if (stream == null) return "{}"
        val output = ByteArrayOutputStream()
        val buffer = ByteArray(4096)
        stream.use { input ->
            while (true) {
                val count = input.read(buffer)
                if (count < 0) break
                if (output.size() + count > MAX_RESPONSE_BYTES) {
                    throw BackendSyncException("Workout sync response is too large")
                }
                output.write(buffer, 0, count)
            }
        }
        return output.toString(StandardCharsets.UTF_8.name())
    }

    private fun parseEndpoint(value: String): URL? = runCatching {
        val clean = value.trim().trimEnd('/')
        if (clean.isBlank()) return@runCatching null
        val base = URL(clean)
        require(base.protocol.equals("https", ignoreCase = true))
        require(base.host.isNotBlank() && base.userInfo == null && base.query == null && base.ref == null)
        require(
            base.host.lowercase() !in setOf("localhost", "127.0.0.1", "::1") &&
                !base.host.lowercase().endsWith(".local"),
        )
        URL("$clean/v2/workouts:sync")
    }.getOrNull()
}
