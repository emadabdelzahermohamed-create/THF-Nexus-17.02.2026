package com.topherofit.thf.pulse

import android.content.Intent
import android.net.Uri
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.result.ActivityResultLauncher
import androidx.health.connect.client.HealthConnectClient
import androidx.health.connect.client.permission.HealthPermission
import androidx.health.connect.client.records.ExerciseSessionRecord
import androidx.health.connect.client.records.StepsRecord
import androidx.health.connect.client.records.metadata.Metadata
import androidx.health.connect.client.request.AggregateRequest
import androidx.health.connect.client.time.TimeRangeFilter
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.launch
import java.time.Instant
import java.time.LocalDate
import java.time.ZoneId

class HealthConnectBridge(
    private val activity: ComponentActivity,
    private val permissionLauncher: ActivityResultLauncher<Set<String>>,
) {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main.immediate)
    private val permissions = setOf(
        HealthPermission.getReadPermission(StepsRecord::class),
        HealthPermission.getReadPermission(ExerciseSessionRecord::class),
        HealthPermission.getWritePermission(ExerciseSessionRecord::class),
    )

    private val client: HealthConnectClient by lazy { HealthConnectClient.getOrCreate(activity) }

    fun requestPermissionsAndReadSteps() {
        when (HealthConnectClient.getSdkStatus(activity)) {
            HealthConnectClient.SDK_AVAILABLE -> scope.launch {
                runCatching { client.permissionController.getGrantedPermissions() }
                    .onSuccess { granted ->
                        if (granted.containsAll(permissions)) readTodaySteps() else permissionLauncher.launch(permissions)
                    }
                    .onFailure { toast("Health Connect: ${it.message ?: "permission check failed"}") }
            }
            HealthConnectClient.SDK_UNAVAILABLE_PROVIDER_UPDATE_REQUIRED -> {
                val uri = Uri.parse("market://details?id=com.google.android.apps.healthdata")
                runCatching { activity.startActivity(Intent(Intent.ACTION_VIEW, uri)) }
                    .onFailure { toast("Health Connect requires an update") }
            }
            else -> toast("Health Connect is not available on this device")
        }
    }

    fun onPermissionsResult(granted: Set<String>) {
        if (granted.containsAll(permissions)) {
            toast("Health Connect permissions granted")
            readTodaySteps()
        } else toast("Health Connect permissions were not fully granted")
    }

    fun readTodaySteps() {
        scope.launch {
            val zone = ZoneId.systemDefault()
            val start = LocalDate.now(zone).atStartOfDay(zone).toInstant()
            val end = Instant.now()
            runCatching {
                client.aggregate(
                    AggregateRequest(
                        metrics = setOf(StepsRecord.COUNT_TOTAL),
                        timeRangeFilter = TimeRangeFilter.between(start, end),
                    )
                )[StepsRecord.COUNT_TOTAL] ?: 0L
            }.onSuccess { toast("Today: $it steps") }
                .onFailure { toast("Health Connect read failed: ${it.message ?: "unknown error"}") }
        }
    }

    fun writeExerciseSession(startEpochMs: Long, endEpochMs: Long, title: String?) {
        if (endEpochMs <= startEpochMs) return
        scope.launch {
            runCatching {
                val granted = client.permissionController.getGrantedPermissions()
                if (!granted.contains(HealthPermission.getWritePermission(ExerciseSessionRecord::class))) {
                    permissionLauncher.launch(permissions)
                    return@runCatching
                }
                val start = Instant.ofEpochMilli(startEpochMs)
                val end = Instant.ofEpochMilli(endEpochMs)
                val rules = ZoneId.systemDefault().rules
                val record = ExerciseSessionRecord(
                    startTime = start,
                    startZoneOffset = rules.getOffset(start),
                    endTime = end,
                    endZoneOffset = rules.getOffset(end),
                    metadata = Metadata.manualEntry(),
                    exerciseType = ExerciseSessionRecord.EXERCISE_TYPE_OTHER_WORKOUT,
                    title = title?.take(80),
                    notes = "Top Hero Fit",
                    segments = emptyList(),
                    laps = emptyList(),
                    exerciseRoute = null,
                    plannedExerciseSessionId = null,
                )
                client.insertRecords(listOf(record))
            }.onSuccess { toast("Workout saved to Health Connect") }
                .onFailure { toast("Health Connect write failed: ${it.message ?: "unknown error"}") }
        }
    }

    fun close() = scope.cancel()

    private fun toast(message: String) {
        activity.runOnUiThread { Toast.makeText(activity, message, Toast.LENGTH_SHORT).show() }
    }
}
