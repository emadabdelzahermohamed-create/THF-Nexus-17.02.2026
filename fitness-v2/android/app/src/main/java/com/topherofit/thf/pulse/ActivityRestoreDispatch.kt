package com.topherofit.thf.pulse

/**
 * Keeps a failed foreground-service dispatch from being reported as a restored live activity.
 * The persisted checkpoint is deliberately owned by the caller and is not cleared here.
 */
internal object ActivityRestoreDispatch {
    fun attempt(
        start: () -> Unit,
        onAccepted: () -> Unit,
        onRejected: () -> Unit,
    ): Boolean {
        val accepted = try {
            start()
            true
        } catch (_: RuntimeException) {
            false
        }
        if (accepted) onAccepted() else onRejected()
        return accepted
    }
}
