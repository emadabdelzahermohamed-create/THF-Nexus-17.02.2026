package com.topherofit.thf.pulse

import java.net.URI

/**
 * WebView is a local-first shell. Permit only the HTTPS tile endpoint required by the
 * activity map; native Kotlin networking remains responsible for authenticated APIs.
 */
object WebViewNetworkPolicy {
    private const val MAP_TILE_HOST = "tile.openstreetmap.org"
    private val tilePath = Regex("^/\\d{1,2}/\\d+/\\d+\\.png$")

    fun isAllowedMapTileUrl(rawUrl: String): Boolean = runCatching {
        val uri = URI(rawUrl)
        uri.scheme.equals("https", ignoreCase = true) &&
            uri.host.equals(MAP_TILE_HOST, ignoreCase = true) &&
            (uri.port == -1 || uri.port == 443) &&
            uri.userInfo == null &&
            uri.query == null &&
            uri.fragment == null &&
            tilePath.matches(uri.path.orEmpty())
    }.getOrDefault(false)

    fun shouldBlockExternalResource(rawUrl: String): Boolean = runCatching {
        when (URI(rawUrl).scheme?.lowercase()) {
            "http", "https" -> !isAllowedMapTileUrl(rawUrl)
            else -> false
        }
    }.getOrDefault(true)
}
