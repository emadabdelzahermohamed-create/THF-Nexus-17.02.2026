package com.topherofit.thf.pulse

import java.util.Locale

/**
 * Conservative distance accumulator for accepted raw GPS fixes.
 *
 * It keeps a stable movement anchor while net displacement remains inside both fixes' reported
 * accuracy radii. Accepted path length accumulates behind that anchor, so ordinary short updates
 * and curved movement are not discarded. Stationary jitter is not summed into distance unless
 * the net displacement also clears the uncertainty deadband. A threshold-crossing excursion must
 * persist for a second accepted fix; a one-fix spike that returns inside the deadband is discarded.
 * This is measurement filtering, not proof of location authenticity; prolonged stationary drift
 * can still exceed the deadband and persist long enough to be credited.
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
    private var lastFix: GpsFix? = null
    private var pendingPathDistanceMetres = 0.0
    private var pendingWorstAccuracyMetres = 0.0
    private var pendingDisplacementCandidate = false

    fun reset() {
        anchor = null
        lastFix = null
        pendingPathDistanceMetres = 0.0
        pendingWorstAccuracyMetres = 0.0
        pendingDisplacementCandidate = false
    }

    /** Seed a new measurement window without crediting a segment to the previous anchor. */
    fun seed(fix: GpsFix?) {
        val usable = fix?.takeIf(::isUsable)
        anchor = usable
        lastFix = usable
        pendingPathDistanceMetres = 0.0
        pendingWorstAccuracyMetres = usable?.accuracyMetres ?: 0.0
        pendingDisplacementCandidate = false
    }

    /**
     * Offer an already accepted raw fix. Returns accumulated path length only after net movement
     * exceeds both reported accuracy radii plus a small margin, then persists at the next accepted
     * fix. A one-fix excursion that falls back inside the deadband is discarded and re-anchored.
     * Provider changes and long gaps re-anchor rather than bridging unrelated evidence.
     */
    fun offer(fix: GpsFix): GpsDistanceCredit? {
        if (!isUsable(fix)) {
            reset()
            return null
        }

        val movementAnchor = anchor
        val previousFix = lastFix
        if (movementAnchor == null || previousFix == null) {
            seed(fix)
            return null
        }

        val anchorSource = normalizedSource(movementAnchor.sourceLabel)
        val currentSource = normalizedSource(fix.sourceLabel)
        if (currentSource == null) {
            reset()
            return null
        }
        if (anchorSource == null || anchorSource != currentSource) {
            seed(fix)
            return null
        }

        val sincePreviousMs = fix.elapsedMs - previousFix.elapsedMs
        val sinceAnchorMs = fix.elapsedMs - movementAnchor.elapsedMs
        if (sincePreviousMs <= 0L || sincePreviousMs > MAX_ANCHOR_GAP_MS ||
            sinceAnchorMs <= 0L || sinceAnchorMs > MAX_ANCHOR_GAP_MS
        ) {
            seed(fix)
            return null
        }

        val stepDistance = ActivityMetrics.distanceMetres(
            previousFix.latitude,
            previousFix.longitude,
            fix.latitude,
            fix.longitude,
        )
        val netDisplacement = ActivityMetrics.distanceMetres(
            movementAnchor.latitude,
            movementAnchor.longitude,
            fix.latitude,
            fix.longitude,
        )
        if (!stepDistance.isFinite() || !netDisplacement.isFinite()) {
            seed(fix)
            return null
        }

        pendingPathDistanceMetres += stepDistance
        pendingWorstAccuracyMetres = maxOf(pendingWorstAccuracyMetres, fix.accuracyMetres)
        lastFix = fix

        val uncertaintyDeadband = movementAnchor.accuracyMetres + pendingWorstAccuracyMetres
        val requiredDisplacement = uncertaintyDeadband + MIN_CREDITABLE_DISTANCE_METRES
        if (netDisplacement < requiredDisplacement) {
            if (pendingDisplacementCandidate) {
                // A threshold-crossing excursion did not persist. Drop its unconfirmed path so a
                // later real movement cannot accidentally credit the spike-and-return distance.
                anchor = fix
                lastFix = fix
                pendingPathDistanceMetres = 0.0
                pendingWorstAccuracyMetres = fix.accuracyMetres
                pendingDisplacementCandidate = false
            }
            return null
        }

        if (!pendingDisplacementCandidate) {
            pendingDisplacementCandidate = true
            return null
        }

        val credit = pendingPathDistanceMetres
        anchor = fix
        lastFix = fix
        pendingPathDistanceMetres = 0.0
        pendingWorstAccuracyMetres = fix.accuracyMetres
        pendingDisplacementCandidate = false
        return GpsDistanceCredit(
            distanceMetres = credit,
            elapsedMs = sinceAnchorMs,
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
