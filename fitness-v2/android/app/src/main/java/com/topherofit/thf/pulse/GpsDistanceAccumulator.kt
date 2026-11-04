package com.topherofit.thf.pulse

import java.util.Locale
import kotlin.math.max

/**
 * Conservative distance accumulator for accepted raw GPS fixes.
 *
 * Unlike the display route, this keeps a stable anchor while apparent movement is inside the
 * two fixes' horizontal-accuracy radii. Small real movements therefore accumulate instead of
 * being lost at every 1-second update, while stationary jitter is not summed as distance.
 * This is measurement filtering, not proof of location authenticity.
 */
data class GpsDistanceCredit(
    val distanceMetres: Double,
    val elapsedMs: Long,
)

class GpsDistanceAccumulator {
    companion object {
        const val MAX_ANCHOR_GAP_MS = 120_000L
        const val MAX_HORIZONTAL_ACCURACY_METRES = 50.0
        const val MIN_CREDITABLE_DISTANCE_METRES = 3.0
    }

    private var anchor: GpsFix? = null

    fun reset() {
        anchor = null
    }

    /** Seed a new measurement window without crediting the segment to the previous anchor. */
    fun seed(fix: GpsFix?) {
        anchor = fix?.takeIf(::isUsable)
    }

    /**
     * Offer an already accepted raw fix. Returns only conservative measurable distance.
     * Small/uncertain displacement leaves the anchor unchanged so real movement can accumulate.
     * Provider changes and long gaps re-anchor rather than bridging unrelated evidence.
     */
    fun offer(fix: GpsFix): GpsDistanceCredit? {
        if (!isUsable(fix)) {
            anchor = null
            return null
        }

        val previous = anchor
        if (previous == null) {
            anchor = fix
            return null
        }

        val previousSource = normalizedSource(previous.sourceLabel)
        val currentSource = normalizedSource(fix.sourceLabel)
        if (currentSource == null) {
            anchor = null
            return null
        }
        if (previousSource == null || previousSource != currentSource) {
            anchor = fix
            return null
        }

        val elapsedMs = fix.elapsedMs - previous.elapsedMs
        if (elapsedMs <= 0L || elapsedMs > MAX_ANCHOR_GAP_MS) {
            anchor = fix
            return null
        }

        val observedDistance = ActivityMetrics.distanceMetres(
            previous.latitude,
            previous.longitude,
            fix.latitude,
            fix.longitude,
        )
        if (!observedDistance.isFinite()) {
            anchor = fix
            return null
        }

        val uncertaintyMetres = previous.accuracyMetres + fix.accuracyMetres
        val conservativeDistance = max(0.0, observedDistance - uncertaintyMetres)
        if (conservativeDistance < MIN_CREDITABLE_DISTANCE_METRES) {
            return null
        }

        anchor = fix
        return GpsDistanceCredit(
            distanceMetres = conservativeDistance,
            elapsedMs = elapsedMs,
        )
    }

    private fun isUsable(fix: GpsFix): Boolean =
        !fix.mock &&
            fix.elapsedMs >= 0L &&
            fix.latitude.isFinite() && fix.latitude in -90.0..90.0 &&
            fix.longitude.isFinite() && fix.longitude in -180.0..180.0 &&
            fix.accuracyMetres.isFinite() && fix.accuracyMetres > 0.0 &&
            fix.accuracyMetres <= MAX_HORIZONTAL_ACCURACY_METRES &&
            normalizedSource(fix.sourceLabel) != null

    private fun normalizedSource(source: String?): String? =
        source?.trim()?.takeIf { it.isNotEmpty() }?.lowercase(Locale.ROOT)
}
