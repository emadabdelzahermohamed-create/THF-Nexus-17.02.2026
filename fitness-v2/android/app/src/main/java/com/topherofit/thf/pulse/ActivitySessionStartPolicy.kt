package com.topherofit.thf.pulse

object ActivitySessionStartPolicy {
    fun shouldStart(currentMode: ActivityMode?, requestedMode: ActivityMode): Boolean =
        currentMode == null && requestedMode.wireName.isNotBlank()
}
