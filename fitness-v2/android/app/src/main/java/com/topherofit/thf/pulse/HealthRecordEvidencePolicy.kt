package com.topherofit.thf.pulse

import androidx.health.connect.client.records.metadata.Device

data class HealthRecordEvidenceAssessment(
    val integrityClass: IntegrityClass,
    val verifiedForRewards: Boolean,
    val reason: String,
)

object HealthRecordEvidencePolicy {
    fun assess(
        appPackageName: String,
        dataOrigin: String,
        recordType: String,
        recordId: String,
        trustedRecordingMethod: Boolean,
        deviceType: Int? = null,
    ): HealthRecordEvidenceAssessment {
        val app = appPackageName.trim()
        val origin = dataOrigin.trim()
        val type = recordType.trim()
        val id = recordId.trim()

        if (origin.equals(app, ignoreCase = true) && app.isNotEmpty()) {
            return HealthRecordEvidenceAssessment(
                integrityClass = IntegrityClass.REJECTED,
                verifiedForRewards = false,
                reason = "SELF_AUTHORED",
            )
        }
        if (!trustedRecordingMethod) {
            return HealthRecordEvidenceAssessment(
                integrityClass = IntegrityClass.MANUAL,
                verifiedForRewards = false,
                reason = "MANUAL_OR_UNKNOWN_METHOD",
            )
        }
        if (origin.isEmpty()) {
            return HealthRecordEvidenceAssessment(
                integrityClass = IntegrityClass.MANUAL,
                verifiedForRewards = false,
                reason = "UNKNOWN_ORIGIN",
            )
        }
        if (type.isEmpty() || id.isEmpty()) {
            return HealthRecordEvidenceAssessment(
                integrityClass = IntegrityClass.SUPPORTED,
                verifiedForRewards = false,
                reason = "INCOMPLETE_PROVIDER_IDENTITY",
            )
        }
        if (!HealthSourceTrustPolicy.isApprovedHealthConnectProvider(origin)) {
            return HealthRecordEvidenceAssessment(
                integrityClass = IntegrityClass.SUPPORTED,
                verifiedForRewards = false,
                reason = "UNTRUSTED_PROVIDER",
            )
        }
        if (deviceType == null || deviceType == Device.TYPE_UNKNOWN) {
            return HealthRecordEvidenceAssessment(
                integrityClass = IntegrityClass.SUPPORTED,
                verifiedForRewards = false,
                reason = "UNKNOWN_DEVICE_CLASS",
            )
        }
        return HealthRecordEvidenceAssessment(
            integrityClass = IntegrityClass.VERIFIED,
            verifiedForRewards = true,
            reason = "APPROVED_PROVIDER_WITH_DEVICE_METADATA",
        )
    }
}
