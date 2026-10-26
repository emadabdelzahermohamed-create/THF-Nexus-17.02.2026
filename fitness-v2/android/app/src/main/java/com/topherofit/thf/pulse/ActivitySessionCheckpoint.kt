package com.topherofit.thf.pulse

data class ActivitySessionCheckpoint(
    val mode: ActivityMode,
    val weightKg: Double,
    val startedAtWallMs: Long,
    val startedAtElapsedMs: Long,
    val savedAtElapsedMs: Long,
    val distanceMetres: Double,
    val stepBaseline: Float?,
    val stepDelta: Int,
    val lastAccuracyMetres: Float?,
    val route: List<ActivityRoutePoint>,
    val phase: ActivitySessionPhase = ActivitySessionPhase.ACTIVE,
    val activatedAtWallMs: Long? = startedAtWallMs,
    val activatedAtElapsedMs: Long? = startedAtElapsedMs,
)

/**
 * Compact, dependency-free codec for an in-flight activity session.
 * V2 persists ARMED/ACTIVE truth state. V1 is still accepted so an in-place Play update can
 * safely recover a 51014 session; legacy V1 sessions are treated as already ACTIVE.
 */
object ActivitySessionCheckpointCodec {
    private const val VERSION_V1 = "1"
    private const val VERSION_V2 = "2"
    private const val V1_HEADER_FIELDS = 10
    private const val V2_HEADER_FIELDS = 13
    private const val MAX_ROUTE_POINTS = 1200
    private const val MAX_RESTORE_GAP_MS = 120_000L

    fun encode(checkpoint: ActivitySessionCheckpoint): String {
        val header = listOf(
            VERSION_V2,
            checkpoint.mode.wireName,
            checkpoint.weightKg.toString(),
            checkpoint.startedAtWallMs.toString(),
            checkpoint.startedAtElapsedMs.toString(),
            checkpoint.savedAtElapsedMs.toString(),
            checkpoint.distanceMetres.toString(),
            checkpoint.stepBaseline?.toString().orEmpty(),
            checkpoint.stepDelta.toString(),
            checkpoint.lastAccuracyMetres?.toString().orEmpty(),
            checkpoint.phase.wireName,
            checkpoint.activatedAtWallMs?.toString().orEmpty(),
            checkpoint.activatedAtElapsedMs?.toString().orEmpty(),
        ).joinToString("|")
        val encodedRoute = checkpoint.route.takeLast(MAX_ROUTE_POINTS).joinToString(";") { point ->
            listOf(
                point.latitude.toString(),
                point.longitude.toString(),
                point.altitudeMetres?.toString().orEmpty(),
                point.accuracyMetres.toString(),
                point.elapsedMs.toString(),
            ).joinToString(",")
        }
        return "$header\n$encodedRoute"
    }

    fun decode(raw: String?): ActivitySessionCheckpoint? {
        if (raw.isNullOrBlank()) return null
        return runCatching {
            val sections = raw.split('\n', limit = 2)
            val fields = sections[0].split('|')
            val version = fields.firstOrNull() ?: return null
            if (version == VERSION_V1 && fields.size != V1_HEADER_FIELDS) return null
            if (version == VERSION_V2 && fields.size != V2_HEADER_FIELDS) return null
            if (version != VERSION_V1 && version != VERSION_V2) return null

            val mode = ActivityMode.fromWire(fields[1]) ?: return null
            val weightKg = fields[2].toDouble()
            val startedAtWallMs = fields[3].toLong()
            val startedAtElapsedMs = fields[4].toLong()
            val savedAtElapsedMs = fields[5].toLong()
            val distanceMetres = fields[6].toDouble()
            val stepBaseline = fields[7].takeIf { it.isNotEmpty() }?.toFloat()
            val stepDelta = fields[8].toInt()
            val lastAccuracyMetres = fields[9].takeIf { it.isNotEmpty() }?.toFloat()
            val phase = if (version == VERSION_V1) {
                ActivitySessionPhase.ACTIVE
            } else {
                ActivitySessionPhase.entries.firstOrNull { it.wireName == fields[10] } ?: return null
            }
            val activatedAtWallMs = if (version == VERSION_V1) startedAtWallMs else fields[11].takeIf { it.isNotEmpty() }?.toLong()
            val activatedAtElapsedMs = if (version == VERSION_V1) startedAtElapsedMs else fields[12].takeIf { it.isNotEmpty() }?.toLong()

            if (!weightKg.isFinite() || weightKg !in 30.0..250.0) return null
            if (startedAtWallMs <= 0L || startedAtElapsedMs <= 0L || savedAtElapsedMs < startedAtElapsedMs) return null
            if (!distanceMetres.isFinite() || distanceMetres < 0.0) return null
            if (stepBaseline != null && (!stepBaseline.isFinite() || stepBaseline < 0f)) return null
            if (stepDelta < 0) return null
            if (lastAccuracyMetres != null && (!lastAccuracyMetres.isFinite() || lastAccuracyMetres < 0f)) return null
            if (phase == ActivitySessionPhase.ARMED && (activatedAtWallMs != null || activatedAtElapsedMs != null)) return null
            if (phase == ActivitySessionPhase.ACTIVE) {
                if (activatedAtWallMs == null || activatedAtElapsedMs == null) return null
                if (activatedAtWallMs <= 0L || activatedAtElapsedMs < startedAtElapsedMs || activatedAtElapsedMs > savedAtElapsedMs) return null
            }

            val route = decodeRoute(sections.getOrNull(1)) ?: return null
            ActivitySessionCheckpoint(
                mode = mode,
                weightKg = weightKg,
                startedAtWallMs = startedAtWallMs,
                startedAtElapsedMs = startedAtElapsedMs,
                savedAtElapsedMs = savedAtElapsedMs,
                distanceMetres = distanceMetres,
                stepBaseline = stepBaseline,
                stepDelta = stepDelta,
                lastAccuracyMetres = lastAccuracyMetres,
                route = route,
                phase = phase,
                activatedAtWallMs = activatedAtWallMs,
                activatedAtElapsedMs = activatedAtElapsedMs,
            )
        }.getOrNull()
    }

    private fun decodeRoute(encoded: String?): List<ActivityRoutePoint>? {
        if (encoded.isNullOrBlank()) return emptyList()
        val rows = encoded.split(';')
        if (rows.size > MAX_ROUTE_POINTS) return null
        return rows.map { row ->
            val values = row.split(',')
            if (values.size != 5) return null
            val latitude = values[0].toDoubleOrNull() ?: return null
            val longitude = values[1].toDoubleOrNull() ?: return null
            val altitude = values[2].takeIf { it.isNotEmpty() }?.toDoubleOrNull()
            val accuracy = values[3].toFloatOrNull() ?: return null
            val elapsedMs = values[4].toLongOrNull() ?: return null
            if (!latitude.isFinite() || latitude !in -90.0..90.0) return null
            if (!longitude.isFinite() || longitude !in -180.0..180.0) return null
            if (values[2].isNotEmpty() && altitude == null) return null
            if (altitude != null && !altitude.isFinite()) return null
            if (!accuracy.isFinite() || accuracy < 0f || elapsedMs < 0L) return null
            ActivityRoutePoint(latitude, longitude, altitude, accuracy, elapsedMs)
        }
    }

    fun canRestore(checkpoint: ActivitySessionCheckpoint, nowElapsedMs: Long): Boolean {
        if (nowElapsedMs <= 0L || nowElapsedMs < checkpoint.savedAtElapsedMs) return false
        if (nowElapsedMs - checkpoint.savedAtElapsedMs > MAX_RESTORE_GAP_MS) return false
        val lastRouteElapsed = checkpoint.route.lastOrNull()?.elapsedMs ?: 0L
        return lastRouteElapsed <= checkpoint.savedAtElapsedMs - checkpoint.startedAtElapsedMs
    }

    fun adjustedStartedAtElapsedMs(checkpoint: ActivitySessionCheckpoint, nowElapsedMs: Long): Long {
        val interruptedMs = (nowElapsedMs - checkpoint.savedAtElapsedMs).coerceAtLeast(0L)
        return checkpoint.startedAtElapsedMs + interruptedMs
    }

    fun adjustedActivatedAtElapsedMs(checkpoint: ActivitySessionCheckpoint, nowElapsedMs: Long): Long? {
        val activated = checkpoint.activatedAtElapsedMs ?: return null
        val interruptedMs = (nowElapsedMs - checkpoint.savedAtElapsedMs).coerceAtLeast(0L)
        return activated + interruptedMs
    }
}
