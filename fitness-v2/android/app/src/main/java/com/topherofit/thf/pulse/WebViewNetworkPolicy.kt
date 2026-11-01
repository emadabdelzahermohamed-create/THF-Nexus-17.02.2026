package com.topherofit.thf.pulse

import java.net.URI

/**
 * WebView is a local-first shell. Permit only approved HTTPS raster map tiles;
 * all other external HTTP(S) resources are blocked by MainActivity.
 */
object WebViewNetworkPolicy {
    private val osmTileHosts = setOf(
        "tile.openstreetmap.org",
        "a.tile.opentopomap.org",
        "b.tile.opentopomap.org",
        "c.tile.opentopomap.org",
    )
    private const val EOX_TILE_HOST = "tiles.maps.eox.at"
    private val rasterTilePath = Regex("^/\\d{1,2}/\\d+/\\d+\\.png$")
    private val eoxTilePath = Regex(
        "^/wmts/1\\.0\\.0/(s2cloudless_3857|streets_3857)/default/g/\\d{1,2}/\\d+/\\d+\\.(jpg|png)$",
    )

    fun isAllowedMapTileUrl(rawUrl: String): Boolean = runCatching {
        val uri = URI(rawUrl)
        if (!uri.scheme.equals("https", ignoreCase = true) ||
            (uri.port != -1 && uri.port != 443) ||
            uri.userInfo != null ||
            uri.query != null ||
            uri.fragment != null
        ) return@runCatching false

        val host = uri.host?.lowercase() ?: return@runCatching false
        val path = uri.path.orEmpty()
        when {
            host in osmTileHosts -> rasterTilePath.matches(path)
            host == EOX_TILE_HOST -> eoxTilePath.matches(path)
            else -> false
        }
    }.getOrDefault(false)

    fun shouldBlockExternalResource(rawUrl: String): Boolean = runCatching {
        when (URI(rawUrl).scheme?.lowercase()) {
            "http", "https" -> !isAllowedMapTileUrl(rawUrl)
            else -> false
        }
    }.getOrDefault(true)
}
