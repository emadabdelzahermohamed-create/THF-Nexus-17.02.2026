package com.topherofit.thf.pulse

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.os.Build

class AndroidMotionSensorGateway(context: Context) : MotionSensorGateway, SensorEventListener {
    private val appContext = context.applicationContext
    private val sensorManager = appContext.getSystemService(Context.SENSOR_SERVICE) as SensorManager
    private val stepCounter = sensorManager.getDefaultSensor(Sensor.TYPE_STEP_COUNTER)
    private val stepDetector = sensorManager.getDefaultSensor(Sensor.TYPE_STEP_DETECTOR)
    private val accelerometer = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)
    private val gyroscope = sensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE)

    private var downstream: MotionSensorListener? = null
    private var lowPowerRegistered = false
    private var activeRegistered = false

    override fun capabilities(): SensorCapabilities = SensorCapabilities(
        stepCounter = stepCounter != null,
        stepDetector = stepDetector != null,
        accelerometer = accelerometer != null,
        gyroscope = gyroscope != null,
        activityRecognitionPermission = hasActivityRecognitionPermission(),
    )

    override fun startLowPower(listener: MotionSensorListener) {
        downstream = listener
        if (lowPowerRegistered || !hasActivityRecognitionPermission()) return
        stepCounter?.let { sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_NORMAL) }
        stepDetector?.let { sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_NORMAL) }
        lowPowerRegistered = stepCounter != null || stepDetector != null
    }

    override fun startActive(listener: MotionSensorListener) {
        downstream = listener
        startLowPower(listener)
        if (activeRegistered) return
        accelerometer?.let { sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_GAME) }
        gyroscope?.let { sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_GAME) }
        activeRegistered = accelerometer != null || gyroscope != null
    }

    override fun stopActive() {
        accelerometer?.let { sensorManager.unregisterListener(this, it) }
        gyroscope?.let { sensorManager.unregisterListener(this, it) }
        activeRegistered = false
    }

    override fun stopAll() {
        sensorManager.unregisterListener(this)
        lowPowerRegistered = false
        activeRegistered = false
    }

    override fun onSensorChanged(event: SensorEvent) {
        val listener = downstream ?: return
        when (event.sensor.type) {
            Sensor.TYPE_STEP_COUNTER -> event.values.firstOrNull()?.let { listener.onStepCounter(it, event.timestamp) }
            Sensor.TYPE_STEP_DETECTOR -> listener.onStepDetector(event.timestamp)
            Sensor.TYPE_ACCELEROMETER -> if (event.values.size >= 3) {
                listener.onAccelerometer(event.values[0], event.values[1], event.values[2], event.timestamp)
            }
            Sensor.TYPE_GYROSCOPE -> if (event.values.size >= 3) {
                listener.onGyroscope(event.values[0], event.values[1], event.values[2], event.timestamp)
            }
        }
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) = Unit

    private fun hasActivityRecognitionPermission(): Boolean =
        Build.VERSION.SDK_INT < 29 ||
            appContext.checkSelfPermission(Manifest.permission.ACTIVITY_RECOGNITION) == PackageManager.PERMISSION_GRANTED
}
