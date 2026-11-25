package com.topherofit.thf.pulse

import java.util.Locale

/**
 * Conservative distance accumulator for accepted raw GPS fixes.
 *
 * It keeps a stable movement anchor while net displacement remains inside both fixes' reported
 * accuracy radii. Accepted path length accumulates behind that anchor, so ordinary short updates
 * and curved movement are not discarded. Stationary jitter is not summed into distance unless
 * the net displacement also clears the uncertainty deadband. Credited path length is bounded to
 * 1.4x net displacement so oscillating fixes cannot inflate a small drift into a long route. A
 * threshold-crossing excursion must persist across at least three accepted fixes spanning six
 * seconds; a one- or two-fix spike that returns inside the deadband is discarded. This is
 * measurement filtering, not proof of location authenticity. When Android supplies a valid
 * speed-accuracy estimate, repeated confidently-stationary observations re-anchor the window so
 * slow provider drift cannot ratchet into credited distance. If speed accuracy is unavailable,
 * GPS-only evidence remains conservative but prolonged coherent drift is still a physical-QA risk.
 */
data class GpsDistanceCredit(
    val distanceMetres: Double,
    val elapsedMs: Long,
)

class GpsDistanceAccumulator {
    companion object {
        const val MAX_ANCHOR_GAP_MS = GpsFixGate.MAX_FIX_AGE_MS
        const val MAX_HORIZONTAL_ACCURACY_METRES = 50.0
        const val MIN_CREDITABLE_DISTANCE_METRES = 3.0
        const val MIN_CONFIRMATION_FIXES = 3
        const val MIN_CONFIRMATION_DURATION_MS = 6_000L
        const val MAX_PATH_TO_NET_RATIO = 1.4
        const val STATIONARY_SPEED_UPPER_BOUND_MPS = 0.35
        const val MIN_STATIONARY_CONFIRMATION_FIXES = 2
        const val MIN_STATIONARY_CONFIRMATION_DURATION_MS = 3_000L
    }

    private var anchor: GpsFix? = null
    private var lastFix: GpsFix? = null
    private var pendingPathDistanceMetres = 0.0
    private var pendingWorstAccuracyMetres = 0.0
    private var pendingDisplacementCandidate = false
    private var pendingDisplacementCandidateSinceElapsedMs: Long? = null
    private var pendingDisplacementCandidateFixCount = 0
    private var stationaryCandidateSinceElapsedMs: Long? = null
    private var stationaryCandidateFixCount = 0

    fun reset() {
        anchor = null
        lastFix = null
        pendingPathDistanceMetres = 0.0
        pendingWorstAccuracyMetres = 0.0
        clearPendingDisplacementCandidate()
        clearStationaryCandidate()
    }

    /** Seed a new measurement window without crediting a segment to the previous anchor. */
    fun seed(fix: GpsFix?) {
        val usable = fix?.takeIf(::isUsable)
        anchor = usable
        lastFix = usable
        pendingPathDistanceMetres = 0.0
        pendingWorstAccuracyMetres = usable?.accuracyMetres ?: 0.0
        clearPendingDisplacementCandidate()
        clearStationaryCandidate()
    }

    /**
     * Offer an already accepted raw fix. Returns accumulated path length only after net movement
     * exceeds both reported accuracy radii plus a small margin, then persists at the next accepted
     * fix. A one-fix excursion that falls back inside the deadband is discarded and re-anchored.
     * Provider changes and gaps beyond the shared 30-second fix-freshness window re-anchor rather
     * than bridging stale evidence.
     */
    fun offer(fix: GpsFix): GpsDistanceCredit? {
        if (!isUsable(fix)) {
            reset()
            return null
        }

        var movementAnchor = anchor
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
        val observedGapSinceAnchorMs = fix.elapsedMs - movementAnchor.elapsedMs
        if (sincePreviousMs <= 0L || sincePreviousMs > MAX_ANCHOR_GAP_MS ||
            observedGapSinceAnchorMs <= 0L || observedGapSinceAnchorMs > MAX_ANCHOR_GAP_MS
        ) {
            seed(fix)
            return null
        }

        if (isConfidentlyStationary(fix)) {
            val candidateStartedAt = stationaryCandidateSinceElapsedMs
            if (candidateStartedAt == null) {
                stationaryCandidateSinceElapsedMs = fix.elapsedMs
                stationaryCandidateFixCount = 1
            } else {
                stationaryCandidateFixCount += 1
            }
            lastFix = fix
            if (stationaryCandidateFixCount >= MIN_STATIONARY_CONFIRMATION_FIXES &&
                fix.elapsedMs - (candidateStartedAt ?: fix.elapsedMs) >= MIN_STATIONARY_CONFIRMATION_DURATION_MS
            ) {
                anchor = fix
                pendingPathDistanceMetres = 0.0
                pendingWorstAccuracyMetres = fix.accuracyMetres
                clearPendingDisplacementCandidate()
                clearStationaryCandidate()
            }
            return null
        }

        // A low-speed observation was provisional until confirmed by a second fix. If movement
        // resumes first, restart at that last observation so stationary drift is never credited.
        if (stationaryCandidateSinceElapsedMs != null) {
            anchor = previousFix
            movementAnchor = previousFix
            pendingPathDistanceMetres = 0.0
            pendingWorstAccuracyMetres = previousFix.accuracyMetres
            clearPendingDisplacementCandidate()
            clearStationaryCandidate()
        }

        val sinceAnchorMs = fix.elapsedMs - movementAnchor.elapsedMs
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
                clearPendingDisplacementCandidate()
            }
            return null
        }

        if (!pendingDisplacementCandidate) {
            pendingDisplacementCandidate = true
            pendingDisplacementCandidateSinceElapsedMs = fix.elapsedMs
            pendingDisplacementCandidateFixCount = 1
            return null
        }

        pendingDisplacementCandidateFixCount += 1
        val candidateStartedAt = pendingDisplacementCandidateSinceElapsedMs ?: fix.elapsedMs
        val candidateDurationMs = fix.elapsedMs - candidateStartedAt
        if (pendingDisplacementCandidateFixCount < MIN_CONFIRMATION_FIXES ||
            candidateDurationMs < MIN_CONFIRMATION_DURATION_MS
        ) return null

        // Preserve ordinary turns, but bound path inflation from oscillating stationary fixes.
        val credit = minOf(pendingPathDistanceMetres, netDisplacement * MAX_PATH_TO_NET_RATIO)
        anchor = fix
        lastFix = fix
        pendingPathDistanceMetres = 0.0
        pendingWorstAccuracyMetres = fix.accuracyMetres
        clearPendingDisplacementCandidate()
        return GpsDistanceCredit(
            distanceMetres = credit,
            elapsedMs = sinceAnchorMs,
        )
    }

    private fun isConfidentlyStationary(fix: GpsFix): Boolean {
        val speed = fix.speedMps ?: return false
        val speedAccuracy = fix.speedAccuracyMps ?: return false
        if (!speed.isFinite() || speed < 0.0 || !speedAccuracy.isFinite() || speedAccuracy < 0.0) {
            return false
        }
        return speed + speedAccuracy <= STATIONARY_SPEED_UPPER_BOUND_MPS
    }

    private fun clearStationaryCandidate() {
        stationaryCandidateSinceElapsedMs = null
        stationaryCandidateFixCount = 0
    }

    private fun clearPendingDisplacementCandidate() {
        pendingDisplacementCandidate = false
        pendingDisplacementCandidateSinceElapsedMs = null
        pendingDisplacementCandidateFixCount = 0
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
