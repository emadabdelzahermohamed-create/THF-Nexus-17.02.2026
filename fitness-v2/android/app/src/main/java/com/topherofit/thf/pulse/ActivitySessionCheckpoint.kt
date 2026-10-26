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
)

/**
 * Compact, dependency-free codec for the in-flight activity session.
 *
 * The checkpoint is only restorable while Android elapsedRealtime() is continuous. That means a
 * process death can recover the session, while a reboot deliberately fails closed because the
 * step-counter baseline and monotonic timestamps no longer belong to the same boot.
 */
object ActivitySessionCheckpointCodec {
    private const val VERSION = "1"
    private const val HEADER_FIELDS = 10
    private const val MAX_ROUTE_POINTS = 1200
    private const val MAX_RESTORE_GAP_MS = 120_000L

    fun encode(checkpoint: ActivitySessionCheckpoint): String {
        val header = listOf(
            VERSION,
            checkpoint.mode.wireName,
            checkpoint.weightKg.toString(),
            checkpoint.startedAtWallMs.toString(),
            checkpoint.startedAtElapsedMs.toString(),
            checkpoint.savedAtElapsedMs.toString(),
            checkpoint.distanceMetres.toString(),
            checkpoint.stepBaseline?.toString().orEmpty(),
            checkpoint.stepDelta.toString(),
            checkpoint.lastAccuracyMetres?.toString().orEmpty(),
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
            if (fields.size != HEADER_FIELDS || fields[0] != VERSION) return null
            val mode = ActivityMode.fromWire(fields[1]) ?: return null
            val weightKg = fields[2].toDouble()
            val startedAtWallMs = fields[3].toLong()
            val startedAtElapsedMs = fields[4].toLong()
            val savedAtElapsedMs = fields[5].toLong()
            val distanceMetres = fields[6].toDouble()
            val stepBaseline = fields[7].takeIf { it.isNotEmpty() }?.toFloat()
            val stepDelta = fields[8].toInt()
            val lastAccuracyMetres = fields[9].takeIf { it.isNotEmpty() }?.toFloat()
            if (!weightKg.isFinite() || weightKg !in 30.0..250.0) return null
            if (startedAtWallMs <= 0L || startedAtElapsedMs <= 0L || savedAtElapsedMs < startedAtElapsedMs) return null
            if (!distanceMetres.isFinite() || distanceMetres < 0.0) return null
            if (stepBaseline != null && (!stepBaseline.isFinite() || stepBaseline < 0f)) return null
            if (stepDelta < 0) return null
            if (lastAccuracyMetres != null && (!lastAccuracyMetres.isFinite() || lastAccuracyMetres < 0f)) return null

            val route = if (sections.size < 2 || sections[1].isBlank()) {
                emptyList()
            } else {
                val rows = sections[1].split(';')
                if (rows.size > MAX_ROUTE_POINTS) return null
                rows.map { row ->
                    val values = row.split(',')
                    if (values.size != 5) return null
                    val latitude = values[0].toDouble()
                    val longitude = values[1].toDouble()
                    val altitude = values[2].takeIf { it.isNotEmpty() }?.toDouble()
                    val accuracy = values[3].toFloat()
                    val elapsedMs = values[4].toLong()
                    if (!latitude.isFinite() || latitude !in -90.0..90.0) return null
                    if (!longitude.isFinite() || longitude !in -180.0..180.0) return null
                    if (altitude != null && !altitude.isFinite()) return null
                    if (!accuracy.isFinite() || accuracy < 0f || elapsedMs < 0L) return null
                    ActivityRoutePoint(latitude, longitude, altitude, accuracy, elapsedMs)
                }
            }
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
            )
        }.getOrNull()
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
}
