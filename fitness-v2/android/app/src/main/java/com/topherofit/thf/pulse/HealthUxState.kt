package com.topherofit.thf.pulse

enum class HealthUxState {
    UNAVAILABLE,
    PROVIDER_UPDATE_REQUIRED,
    PERMISSION_REQUIRED,
    READY_UNSYNCED,
    SYNCING,
    SYNCED_VERIFIED,
    SYNCED_NO_RECORDS,
    SYNCED_UNVERIFIED_ONLY,
    RATE_LIMITED,
    ERROR,
}

data class HealthUxInput(
    val availability: String,
    val readPermissionsGranted: Boolean,
    val syncing: Boolean,
    val hasSuccessfulSync: Boolean,
    val recordsRead: Int,
    val verifiedRecords: Int,
    val lastErrorCode: String?,
)

object HealthUxStateClassifier {
    fun classify(input: HealthUxInput): HealthUxState {
        return when {
            input.availability == "PROVIDER_UPDATE_REQUIRED" -> HealthUxState.PROVIDER_UPDATE_REQUIRED
            input.availability != "AVAILABLE" -> HealthUxState.UNAVAILABLE
            !input.readPermissionsGranted -> HealthUxState.PERMISSION_REQUIRED
            input.syncing -> HealthUxState.SYNCING
            input.lastErrorCode == "RATE_LIMITED" -> HealthUxState.RATE_LIMITED
            !input.lastErrorCode.isNullOrBlank() -> HealthUxState.ERROR
            !input.hasSuccessfulSync -> HealthUxState.READY_UNSYNCED
            input.recordsRead <= 0 -> HealthUxState.SYNCED_NO_RECORDS
            input.verifiedRecords <= 0 -> HealthUxState.SYNCED_UNVERIFIED_ONLY
            else -> HealthUxState.SYNCED_VERIFIED
        }
    }
}
