package com.topherofit.thf.pulse

import android.Manifest
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.content.pm.ServiceInfo
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.location.Location
import android.location.LocationListener
import android.location.LocationManager
import android.os.Build
import android.os.IBinder
import android.os.Looper
import android.os.SystemClock
import java.util.Locale
import kotlin.math.max

/**
 * Owns any live tracking session so collection is independent from MainActivity/WebView lifecycle.
 * A foreground notification is deliberately required: if the UI goes to the background, the user
 * can still see that GPS/motion collection is active and can stop it from the notification.
 */
class ActivityTrackingService : Service(), LocationListener, SensorEventListener {
    companion object {
        const val ACTION_START_ACTIVITY = "com.topherofit.thf.pulse.START_ACTIVITY"
        const val ACTION_START_WORKOUT = "com.topherofit.thf.pulse.START_WORKOUT"
        const val ACTION_STOP_TRACKING = "com.topherofit.thf.pulse.STOP_TRACKING"
        const val EXTRA_MODE = "mode"
        const val EXTRA_WEIGHT_KG = "weight_kg"
        const val EXTRA_SESSION_ID = "session_id"
        const val EXTRA_SENSOR_PROFILE = "sensor_profile"

        private const val CHANNEL_ID = "thf_live_tracking"
        private const val NOTIFICATION_ID = 51009
        private const val MAX_ROUTE_POINTS = 1200

        @Volatile private var instance: ActivityTrackingService? = null
        @Volatile private var lastActivitySnapshot = ActivitySnapshot(
            active = false,
            mode = null,
            startedAtWallMs = 0L,
            elapsedMs = 0L,
            distanceMetres = 0.0,
            stepDelta = 0,
            currentSpeedKph = 0.0,
            averageSpeedKph = 0.0,
            paceMinutesPerKm = null,
            estimatedCaloriesKcal = 0.0,
            gpsPointCount = 0,
            lastAccuracyMetres = null,
            route = emptyList(),
        )
        @Volatile private var lastWorkoutEvidence: MotionEvidence? = null

        fun hasActiveTracking(): Boolean = instance?.hasLiveSession() == true
        fun activitySnapshot(): ActivitySnapshot = instance?.buildActivitySnapshot(active = true) ?: lastActivitySnapshot
        fun workoutSnapshot(): MotionEvidence? = instance?.workoutEngine?.snapshot() ?: lastWorkoutEvidence

        fun startActivity(context: Context, mode: ActivityMode, weightKg: Double) {
            val intent = Intent(context, ActivityTrackingService::class.java)
                .setAction(ACTION_START_ACTIVITY)
                .putExtra(EXTRA_MODE, mode.wireName)
                .putExtra(EXTRA_WEIGHT_KG, weightKg)
            startForegroundCompat(context, intent)
        }

        fun startWorkout(context: Context, sessionId: String, profile: MotionSensorProfile) {
            val intent = Intent(context, ActivityTrackingService::class.java)
                .setAction(ACTION_START_WORKOUT)
                .putExtra(EXTRA_SESSION_ID, sessionId)
                .putExtra(EXTRA_SENSOR_PROFILE, profile.wireName)
            startForegroundCompat(context, intent)
        }

        fun finishActivity(): ActivitySnapshot {
            val service = instance ?: return lastActivitySnapshot
            return service.finishActivityInternal()
        }

        fun finishWorkout(): MotionEvidence? {
            val service = instance ?: return lastWorkoutEvidence
            return service.finishWorkoutInternal()
        }

        private fun startForegroundCompat(context: Context, intent: Intent) {
            if (Build.VERSION.SDK_INT >= 26) context.startForegroundService(intent) else context.startService(intent)
        }
    }

    private lateinit var notificationManager: NotificationManager
    private lateinit var locationManager: LocationManager
    private lateinit var sensorManager: SensorManager
    private var stepCounter: Sensor? = null

    private var activityMode: ActivityMode? = null
    private var activityWeightKg = 70.0
    private var activityStartedAtWallMs = 0L
    private var activityStartedAtElapsedMs = 0L
    private var activityDistanceMetres = 0.0
    private var activityStepBaseline: Float? = null
    private var activityStepDelta = 0
    private var currentSpeedKph = 0.0
    private var lastLocation: Location? = null
    private var lastAccuracyMetres: Float? = null
    private val route = mutableListOf<ActivityRoutePoint>()
    private var lastNotificationUpdateMs = 0L

    internal var workoutEngine: MotionSessionEngine? = null
        private set

    override fun onCreate() {
        super.onCreate()
        instance = this
        notificationManager = getSystemService(NotificationManager::class.java)
        locationManager = getSystemService(LocationManager::class.java)
        sensorManager = getSystemService(SensorManager::class.java)
        stepCounter = sensorManager.getDefaultSensor(Sensor.TYPE_STEP_COUNTER)
        createNotificationChannel()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_START_ACTIVITY -> {
                val mode = ActivityMode.fromWire(intent.getStringExtra(EXTRA_MODE)) ?: return START_NOT_STICKY
                startActivityInternal(mode, intent.getDoubleExtra(EXTRA_WEIGHT_KG, 70.0))
            }
            ACTION_START_WORKOUT -> {
                val sessionId = intent.getStringExtra(EXTRA_SESSION_ID).orEmpty().trim()
                if (sessionId.isNotEmpty()) {
                    startWorkoutInternal(sessionId, MotionSensorProfile.fromWire(intent.getStringExtra(EXTRA_SENSOR_PROFILE)))
                }
            }
            ACTION_STOP_TRACKING -> stopCurrentSession()
        }
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onTaskRemoved(rootIntent: Intent?) {
        // Deliberately keep the foreground session alive when the task UI is swiped away.
        // The visible notification remains the user's stop/control surface.
        super.onTaskRemoved(rootIntent)
    }

    override fun onDestroy() {
        unregisterActivitySources()
        workoutEngine?.let { engine ->
            lastWorkoutEvidence = runCatching { engine.stopSession() }.getOrNull() ?: lastWorkoutEvidence
            engine.onHostPause()
        }
        workoutEngine = null
        if (instance === this) instance = null
        super.onDestroy()
    }

    private fun hasLiveSession(): Boolean = activityMode != null || workoutEngine?.currentState()?.active == true

    private fun startActivityInternal(mode: ActivityMode, weightKg: Double) {
        stopCurrentSession(keepService = true)
        activityMode = mode
        activityWeightKg = weightKg.coerceIn(30.0, 250.0)
        activityStartedAtWallMs = System.currentTimeMillis()
        activityStartedAtElapsedMs = SystemClock.elapsedRealtime()
        activityDistanceMetres = 0.0
        activityStepBaseline = null
        activityStepDelta = 0
        currentSpeedKph = 0.0
        lastLocation = null
        lastAccuracyMetres = null
        route.clear()
        startForegroundForCurrentSession(buildNotification())
        registerActivitySources(mode)
        publishActivitySnapshot()
    }

    private fun startWorkoutInternal(sessionId: String, profile: MotionSensorProfile) {
        if (workoutEngine?.currentState()?.sessionId == sessionId) return
        stopCurrentSession(keepService = true)
        val engine = MotionSessionEngine(AndroidMotionSensorGateway(this))
        engine.onHostResume()
        engine.startSession(sessionId, profile)
        workoutEngine = engine
        startForegroundForCurrentSession(buildNotification())
    }

    private fun registerActivitySources(mode: ActivityMode) {
        if (checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED &&
            checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION) != PackageManager.PERMISSION_GRANTED
        ) return

        runCatching {
            if (locationManager.isProviderEnabled(LocationManager.GPS_PROVIDER)) {
                locationManager.requestLocationUpdates(LocationManager.GPS_PROVIDER, 1_000L, 1f, this, Looper.getMainLooper())
            }
        }
        runCatching {
            if (locationManager.isProviderEnabled(LocationManager.NETWORK_PROVIDER)) {
                locationManager.requestLocationUpdates(LocationManager.NETWORK_PROVIDER, 2_500L, 4f, this, Looper.getMainLooper())
            }
        }
        if (mode.usesSteps && hasActivityRecognitionPermission()) {
            stepCounter?.let { sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_NORMAL) }
        }
    }

    private fun unregisterActivitySources() {
        runCatching { locationManager.removeUpdates(this) }
        runCatching { sensorManager.unregisterListener(this) }
    }

    override fun onLocationChanged(location: Location) {
        val mode = activityMode ?: return
        val nowElapsed = SystemClock.elapsedRealtime()
        val previous = lastLocation
        // Reject before changing the distance, route, or next comparison baseline.
        if (!GpsFixGate.accepts(location.toGpsFix(), previous?.toGpsFix(), mode, activityStartedAtElapsedMs, nowElapsed)) return
        if (previous != null) {
            val deltaMetres = ActivityMetrics.distanceMetres(previous.latitude, previous.longitude, location.latitude, location.longitude)
            val deltaMs = location.elapsedRealtimeNanos / 1_000_000L - previous.elapsedRealtimeNanos / 1_000_000L
            val impliedKph = ActivityMetrics.averageSpeedKph(deltaMetres, deltaMs)
            if (deltaMetres >= 1.0) {
                activityDistanceMetres += deltaMetres
                currentSpeedKph = if (location.hasSpeed()) location.speed * 3.6 else impliedKph
            } else if (deltaMetres < 1.0) {
                currentSpeedKph = 0.0
            }
        }
        lastLocation = Location(location)
        lastAccuracyMetres = location.accuracy
        if (route.size >= MAX_ROUTE_POINTS) route.removeAt(0)
        route += ActivityRoutePoint(
            latitude = location.latitude,
            longitude = location.longitude,
            altitudeMetres = if (location.hasAltitude()) location.altitude else null,
            accuracyMetres = location.accuracy,
            elapsedMs = nowElapsed - activityStartedAtElapsedMs,
        )
        publishActivitySnapshot()
        if (nowElapsed - lastNotificationUpdateMs >= 5_000L) {
            notificationManager.notify(NOTIFICATION_ID, buildNotification())
            lastNotificationUpdateMs = nowElapsed
        }
    }

    @Suppress("DEPRECATION")
    private fun Location.toGpsFix() = GpsFix(
        latitude = latitude,
        longitude = longitude,
        accuracyMetres = if (hasAccuracy()) accuracy.toDouble() else Double.NaN,
        elapsedMs = elapsedRealtimeNanos / 1_000_000L,
        mock = if (Build.VERSION.SDK_INT >= 31) isMock else isFromMockProvider,
        speedMps = if (hasSpeed()) speed.toDouble() else null,
    )

    override fun onSensorChanged(event: SensorEvent) {
        if (event.sensor.type != Sensor.TYPE_STEP_COUNTER || activityMode?.usesSteps != true) return
        val raw = event.values.firstOrNull() ?: return
        val baseline = activityStepBaseline
        if (baseline == null || raw < baseline) {
            activityStepBaseline = raw
            activityStepDelta = 0
        } else {
            activityStepDelta = max(0, (raw - baseline).toInt())
        }
        publishActivitySnapshot()
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) = Unit

    private fun buildActivitySnapshot(active: Boolean): ActivitySnapshot {
        val mode = activityMode
        if (mode == null) return lastActivitySnapshot
        val elapsed = max(0L, SystemClock.elapsedRealtime() - activityStartedAtElapsedMs)
        return ActivitySnapshot(
            active = active,
            mode = mode,
            startedAtWallMs = activityStartedAtWallMs,
            elapsedMs = elapsed,
            distanceMetres = activityDistanceMetres,
            stepDelta = if (mode.usesSteps) activityStepDelta else 0,
            currentSpeedKph = currentSpeedKph,
            averageSpeedKph = ActivityMetrics.averageSpeedKph(activityDistanceMetres, elapsed),
            paceMinutesPerKm = if (mode == ActivityMode.CYCLE) null else ActivityMetrics.paceMinutesPerKm(activityDistanceMetres, elapsed),
            estimatedCaloriesKcal = ActivityMetrics.estimatedCalories(mode, activityWeightKg, elapsed),
            gpsPointCount = route.size,
            lastAccuracyMetres = lastAccuracyMetres,
            route = route.toList(),
        )
    }

    private fun publishActivitySnapshot() {
        if (activityMode != null) lastActivitySnapshot = buildActivitySnapshot(active = true)
    }

    private fun finishActivityInternal(): ActivitySnapshot {
        if (activityMode == null) return lastActivitySnapshot
        val final = buildActivitySnapshot(active = false)
        lastActivitySnapshot = final
        unregisterActivitySources()
        activityMode = null
        stopForeground(STOP_FOREGROUND_REMOVE)
        stopSelf()
        return final
    }

    private fun finishWorkoutInternal(): MotionEvidence? {
        val engine = workoutEngine ?: return lastWorkoutEvidence
        val evidence = engine.stopSession()
        engine.onHostPause()
        workoutEngine = null
        if (evidence != null) lastWorkoutEvidence = evidence
        stopForeground(STOP_FOREGROUND_REMOVE)
        stopSelf()
        return evidence
    }

    private fun stopCurrentSession(keepService: Boolean = false) {
        if (activityMode != null) {
            lastActivitySnapshot = buildActivitySnapshot(active = false)
            unregisterActivitySources()
            activityMode = null
        }
        workoutEngine?.let { engine ->
            lastWorkoutEvidence = engine.stopSession() ?: lastWorkoutEvidence
            engine.onHostPause()
        }
        workoutEngine = null
        if (!keepService) {
            stopForeground(STOP_FOREGROUND_REMOVE)
            stopSelf()
        }
    }

    private fun buildNotification(): Notification {
        val launchIntent = packageManager.getLaunchIntentForPackage(packageName)?.apply {
            flags = Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_CLEAR_TOP
        }
        val contentIntent = launchIntent?.let {
            PendingIntent.getActivity(this, 51009, it, PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
        }
        val stopIntent = PendingIntent.getService(
            this,
            51010,
            Intent(this, ActivityTrackingService::class.java).setAction(ACTION_STOP_TRACKING),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
        )
        val snapshot = if (activityMode != null) buildActivitySnapshot(active = true) else null
        val title = when (activityMode) {
            ActivityMode.WALK -> "Top Hero Fit · المشي مستمر"
            ActivityMode.RUN -> "Top Hero Fit · الجري مستمر"
            ActivityMode.CYCLE -> "Top Hero Fit · ركوب الدراجة مستمر"
            null -> "Top Hero Fit · التمرين مستمر"
        }
        val text = snapshot?.let {
            val km = it.distanceMetres / 1000.0
            val metric = if (it.mode == ActivityMode.CYCLE) {
                String.format(Locale.US, "%.1f km · %.1f km/h · %.0f kcal", km, it.averageSpeedKph, it.estimatedCaloriesKcal)
            } else {
                val pace = it.paceMinutesPerKm?.let(::formatPace) ?: "—"
                String.format(Locale.US, "%.1f km · %s /km · %.0f kcal", km, pace, it.estimatedCaloriesKcal)
            }
            metric
        } ?: "قياس الحركة مستمر حتى عند الخروج من التطبيق"
        return Notification.Builder(this, CHANNEL_ID)
            .setSmallIcon(android.R.drawable.ic_media_play)
            .setContentTitle(title)
            .setContentText(text)
            .setOngoing(true)
            .setOnlyAlertOnce(true)
            .setCategory(Notification.CATEGORY_SERVICE)
            .setContentIntent(contentIntent)
            .addAction(Notification.Action.Builder(null, "إيقاف", stopIntent).build())
            .build()
    }

    private fun startForegroundForCurrentSession(notification: Notification) {
        if (Build.VERSION.SDK_INT >= 29) {
            val type = when {
                activityMode != null -> ServiceInfo.FOREGROUND_SERVICE_TYPE_LOCATION
                Build.VERSION.SDK_INT >= 34 -> ServiceInfo.FOREGROUND_SERVICE_TYPE_HEALTH
                else -> ServiceInfo.FOREGROUND_SERVICE_TYPE_NONE
            }
            startForeground(NOTIFICATION_ID, notification, type)
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }
    }

    private fun createNotificationChannel() {
        val channel = NotificationChannel(
            CHANNEL_ID,
            "تتبع النشاط والتمرين",
            NotificationManager.IMPORTANCE_LOW,
        ).apply {
            description = "إشعار دائم أثناء قياس نشاط أو تمرين في الخلفية"
            setShowBadge(false)
        }
        notificationManager.createNotificationChannel(channel)
    }

    private fun hasActivityRecognitionPermission(): Boolean =
        Build.VERSION.SDK_INT < 29 || checkSelfPermission(Manifest.permission.ACTIVITY_RECOGNITION) == PackageManager.PERMISSION_GRANTED

    private fun formatPace(value: Double): String {
        val safe = value.coerceAtMost(99.0)
        val minutes = safe.toInt()
        val seconds = ((safe - minutes) * 60.0).toInt().coerceIn(0, 59)
        return "%d:%02d".format(Locale.US, minutes, seconds)
    }
}
