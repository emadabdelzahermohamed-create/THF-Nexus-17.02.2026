package com.topherofit.thf.pulse

import java.net.URI
import java.security.MessageDigest
import java.security.SecureRandom
import java.util.Base64

data class AccountAuthRequest(
    val verifier: String,
    val challenge: String,
    val startUrl: String,
)

/** Pure, fail-closed contract for the external-browser Android account hand-off. */
object AccountAuthContract {
    const val REDIRECT_URI = "topherofit://auth/v2/complete"
    const val FLOW_TTL_MILLIS = 5 * 60 * 1000L
    private val blockedHosts = setOf(
        "localhost",
        "127.0.0.1",
        "::1",
        "trycloudflare.com",
        "ngrok-free.app",
        "ngrok.io",
    )

    fun persistentHttpsBase(value: String): String? = runCatching {
        val uri = URI(value.trim())
        val host = uri.host?.lowercase().orEmpty()
        require(uri.scheme.equals("https", ignoreCase = true))
        require(host.isNotBlank() && uri.userInfo == null && uri.fragment == null && uri.query == null)
        require(uri.port == -1 || uri.port == 443)
        require(!host.endsWith(".local"))
        require(blockedHosts.none { host == it || host.endsWith(".$it") })
        URI("https", null, host, normalizedPort(uri), normalizePath(uri.path), null, null).toASCIIString()
    }.getOrNull()

    fun newRequest(accountUrl: String, random: SecureRandom = SecureRandom()): AccountAuthRequest {
        val base = persistentHttpsBase(accountUrl) ?: throw IllegalArgumentException("approved HTTPS account URL required")
        val verifierBytes = ByteArray(32).also(random::nextBytes)
        val verifier = Base64.getUrlEncoder().withoutPadding().encodeToString(verifierBytes)
        val challenge = Base64.getUrlEncoder().withoutPadding().encodeToString(
            MessageDigest.getInstance("SHA-256").digest(verifier.toByteArray(Charsets.US_ASCII)),
        )
        val separator = if (base.contains('?')) '&' else '?'
        val query = listOf(
            "nativeAuth=android-v2",
            "code_challenge=$challenge",
            "code_challenge_method=S256",
            "redirect_uri=${urlEncode(REDIRECT_URI)}",
        ).joinToString("&")
        return AccountAuthRequest(verifier, challenge, "$base$separator$query")
    }

    fun callbackTicket(uriValue: String?): String? = runCatching {
        val uri = URI(uriValue ?: return@runCatching null)
        val customCallback = uri.scheme.equals("topherofit", true) && uri.host.equals("auth", true) && uri.path == "/v2/complete"
        val verifiedAppLink = uri.scheme.equals("https", true) &&
            uri.host.equals("thf-fitness-pulse-ul26f1.v2.appdeploy.ai", true) &&
            uri.path == "/android/auth/v2/complete"
        if (!customCallback && !verifiedAppLink) {
            return@runCatching null
        }
        uri.rawQuery.orEmpty().split('&')
            .mapNotNull { part ->
                val split = part.split('=', limit = 2)
                if (split.size == 2 && split[0] == "ticket") urlDecode(split[1]) else null
            }
            .singleOrNull()
            ?.takeIf(::validTicket)
    }.getOrNull()

    fun validVerifier(value: String?): Boolean =
        value != null && value.length in 43..128 && value.all { it.isLetterOrDigit() || it in "-._~" }

    fun validTicket(value: String): Boolean =
        value.length in 32..256 && value.all { it.isLetterOrDigit() || it == '-' || it == '_' }

    fun validAccessToken(value: String): String {
        val token = value.trim()
        val opaque = token.startsWith("thf_v2_") && token.length in 40..256 &&
            token.removePrefix("thf_v2_").all { it.isLetterOrDigit() || it == '-' || it == '_' }
        val jwt = token.length in 32..8192 && token.count { it == '.' } == 2 && token.none { it.isWhitespace() }
        require(opaque || jwt) { "invalid short-lived access token" }
        return token
    }

    private fun normalizedPort(uri: URI): Int = if (uri.port == 443) -1 else uri.port
    private fun normalizePath(path: String?): String = path.orEmpty().ifBlank { "/" }.let { if (it.endsWith('/')) it else "$it/" }
    private fun urlEncode(value: String): String = java.net.URLEncoder.encode(value, Charsets.UTF_8.name())
    private fun urlDecode(value: String): String = java.net.URLDecoder.decode(value, Charsets.UTF_8.name())
}
