package com.topherofit.thf.pulse

import androidx.health.connect.client.records.metadata.Device
import androidx.health.connect.client.records.metadata.Metadata
import java.util.Locale

/**
 * Privacy-reduced, UI-safe projection of a selected Health Connect record.
 *
 * The provider record ID, client record ID, manufacturer and model are deliberately omitted.
 * recordKey is a deterministic pseudonymous identity for list reconciliation only; it is not
 * anonymization, hardware attestation, or an authorization token.
 */
data class HealthRecordProvenanceSummary(
    val recordKey: String?,
    val sourcePackage: String?,
    val recordType: String,
    val recordingMethod: String,
    val deviceClass: String,
    val integrityClass: String,
    val rewardEligible: Boolean,
    val verificationReason: String,
)

internal object HealthRecordProvenancePresentationPolicy {
    private val packageNamePattern =
        Regex("^[A-Za-z_][A-Za-z0-9_]*(\\.[A-Za-z_][A-Za-z0-9_]*)+$")
    private val recordTypePattern = Regex("^[A-Za-z][A-Za-z0-9]{0,63}$")
    private val recordKeyPattern = Regex("^thf-health-[0-9a-f]{40}$")
    private val reasonPattern = Regex("^[A-Z0-9_]{1,64}$")

    private val supportedRecordTypes = setOf(
        "StepsRecord",
        "DistanceRecord",
        "ActiveCaloriesBurnedRecord",
        "ExerciseSessionRecord",
    )

    private val rewardCompatibleDeviceClasses = setOf(
        "phone",
        "watch",
        "fitness_band",
        "chest_strap",
        "ring",
    )

    fun summarize(evidence: HealthRecordEvidence): HealthRecordProvenanceSummary {
        val source = normalizeSourcePackage(evidence.dataOrigin)
        val stableRecordType = normalizeRecordType(evidence.recordType)
        val recordId = evidence.recordId.trim()

        // Recompute and compare rather than trusting an arbitrary string in canonicalKey.
        // Unknown but well-formed record types retain a pseudonymous diagnostic key; they are
        // still labelled "unknown" and cannot qualify for rewards.
        val expectedKey = if (source != null && stableRecordType != null && recordId.isNotEmpty()) {
            WorkoutIdentity.stableHealthRecordKey(source, stableRecordType, recordId)
        } else {
            null
        }
        val recordKey = expectedKey?.takeIf {
            it == evidence.canonicalKey && recordKeyPattern.matches(it)
        }

        val recordingMethod = recordingMethodLabel(evidence.recordingMethod)
        val deviceClass = deviceClassLabel(evidence.deviceType)
        val integrityClass = evidence.integrityClass.name
        val reason = evidence.verificationReason.trim()
            .takeIf { reasonPattern.matches(it) }
            ?: "UNSPECIFIED"
        val isSupportedRecordType = stableRecordType in supportedRecordTypes

        // Presentation must never upgrade the repository's evidence decision. It only fails
        // closed further when identity or the displayable provenance contract is incomplete.
        val rewardEligible = evidence.verifiedForRewards &&
            evidence.integrityClass == IntegrityClass.VERIFIED &&
            source != null &&
            isSupportedRecordType &&
            recordKey != null &&
            recordingMethod in setOf("actively_recorded", "automatically_recorded") &&
            deviceClass in rewardCompatibleDeviceClasses

        return HealthRecordProvenanceSummary(
            recordKey = recordKey,
            sourcePackage = source,
            recordType = if (isSupportedRecordType) stableRecordType!! else "unknown",
            recordingMethod = recordingMethod,
            deviceClass = deviceClass,
            integrityClass = integrityClass,
            rewardEligible = rewardEligible,
            verificationReason = reason,
        )
    }

    private fun normalizeSourcePackage(raw: String): String? {
        val normalized = raw.trim().lowercase(Locale.ROOT)
        return normalized.takeIf {
            it.length <= 255 && packageNamePattern.matches(it)
        }
    }

    private fun normalizeRecordType(raw: String): String? {
        val normalized = raw.trim()
        return normalized.takeIf { recordTypePattern.matches(it) }
    }

    private fun recordingMethodLabel(value: Int): String = when (value) {
        Metadata.RECORDING_METHOD_ACTIVELY_RECORDED -> "actively_recorded"
        Metadata.RECORDING_METHOD_AUTOMATICALLY_RECORDED -> "automatically_recorded"
        Metadata.RECORDING_METHOD_MANUAL_ENTRY -> "manual_entry"
        else -> "unknown"
    }

    private fun deviceClassLabel(value: Int?): String = when (value) {
        Device.TYPE_PHONE -> "phone"
        Device.TYPE_WATCH -> "watch"
        Device.TYPE_FITNESS_BAND -> "fitness_band"
        Device.TYPE_CHEST_STRAP -> "chest_strap"
        Device.TYPE_RING -> "ring"
        Device.TYPE_SCALE -> "scale"
        else -> "unknown"
    }
}
