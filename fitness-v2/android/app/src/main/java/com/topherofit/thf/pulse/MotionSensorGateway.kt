package com.topherofit.thf.pulse

interface MotionSensorListener {
    fun onStepCounter(rawCount: Float, elapsedNanos: Long)
    fun onStepDetector(elapsedNanos: Long)
    fun onAccelerometer(x: Float, y: Float, z: Float, elapsedNanos: Long)
    fun onGyroscope(x: Float, y: Float, z: Float, elapsedNanos: Long)
}

interface MotionSensorGateway {
    fun capabilities(): SensorCapabilities
    fun startLowPower(listener: MotionSensorListener)
    fun startActive(listener: MotionSensorListener)
    fun stopActive()
    fun stopAll()
}
