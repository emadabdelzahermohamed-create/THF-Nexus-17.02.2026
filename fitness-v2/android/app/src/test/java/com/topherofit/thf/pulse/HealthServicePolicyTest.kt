package com.topherofit.thf.pulse

import java.time.Instant
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.runBlocking
import org.junit.Assert.*
import org.junit.Test

class HealthServicePolicyTest {
    private val now = Instant.parse("2026-10-25T08:00:00Z")
    private val data = HealthMetricResult(
        HealthService.WEIGHT, HealthMetricStatus.READY,
        listOf(HealthMetricValue(72.5, "kg")), setOf("com.sec.android.app.shealth"), now,
    )

    @Test fun revokedPermissionRemovesValueSourceAndTimestamp() {
        val masked = HealthServiceAccessPolicy.visibleResult(HealthService.WEIGHT, emptySet(), data)
        assertEquals(HealthMetricStatus.PERMISSION_REQUIRED, masked.status)
        assertTrue(masked.values.isEmpty())
        assertTrue(masked.origins.isEmpty())
        assertNull(masked.observedAt)
    }

    @Test fun unrelatedGrantDoesNotAuthorizeAnotherMetric() {
        val masked = HealthServiceAccessPolicy.visibleResult(
            HealthService.WEIGHT, setOf(HealthService.STEPS.permission), data,
        )
        assertEquals(HealthMetricStatus.PERMISSION_REQUIRED, masked.status)
    }

    @Test fun aGrantedMetricDoesNotRequireTheWholePermissionSet() {
        val result = HealthServiceAccessPolicy.visibleResult(
            HealthService.WEIGHT, setOf(HealthService.WEIGHT.permission), data,
        )
        assertEquals(72.5, result.values.single().value, 0.001)
        assertEquals(setOf("com.sec.android.app.shealth"), result.origins)
    }

    @Test fun missingDataIsNotReportedAsZero() {
        val result = HealthServiceAccessPolicy.measurement(HealthService.STEPS, emptyList())
        assertEquals(HealthMetricStatus.NO_DATA, result.status)
        assertTrue(result.values.isEmpty())
    }

    @Test fun measuredZeroRemainsARealValue() {
        val result = HealthServiceAccessPolicy.measurement(
            HealthService.ACTIVE_CALORIES, listOf(HealthMetricValue(0.0, "kcal")),
        )
        assertEquals(HealthMetricStatus.READY, result.status)
        assertEquals(0.0, result.values.single().value, 0.0)
    }

    @Test fun malformedMeasurementsCannotReachTheDisplay() {
        val result = HealthServiceAccessPolicy.measurement(
            HealthService.WEIGHT,
            listOf(HealthMetricValue(Double.NaN, "kg"), HealthMetricValue(-1.0, "kg")),
        )
        assertEquals(HealthMetricStatus.NO_DATA, result.status)
    }

    @Test fun aResultForAnotherServiceCannotBeDisplayed() {
        val result = HealthServiceAccessPolicy.visibleResult(
            HealthService.HEIGHT, setOf(HealthService.HEIGHT.permission), data,
        )
        assertEquals(HealthMetricStatus.ERROR, result.status)
        assertTrue(result.values.isEmpty())
    }

    @Test fun deniedPermissionNeverTouchesHealthData() = runBlocking {
        val source = FixtureSource()
        val result = HealthServicesReader(source).read(HealthService.WEIGHT)
        assertEquals(HealthMetricStatus.PERMISSION_REQUIRED, result.status)
        assertEquals(0, source.readCount)
    }

    @Test fun midReadRevocationDiscardsSensitiveData() = runBlocking {
        val source = FixtureSource(setOf(HealthService.WEIGHT.permission), data) {
            grants = emptySet()
        }
        val result = HealthServicesReader(source).read(HealthService.WEIGHT)
        assertEquals(HealthMetricStatus.PERMISSION_REQUIRED, result.status)
        assertTrue(result.values.isEmpty())
        assertTrue(result.origins.isEmpty())
    }

    @Test fun aGrantedBodyMetricCanBeReadWithoutActivityOrWritePermission() = runBlocking {
        val source = FixtureSource(setOf(HealthService.WEIGHT.permission), data)
        val result = HealthServicesReader(source).read(HealthService.WEIGHT)
        assertEquals(HealthMetricStatus.READY, result.status)
        assertEquals(72.5, result.values.single().value, 0.001)
        assertEquals(1, source.readCount)
    }

    @Test fun providerFailureHasNoStaleValuesAndDoesNotBlockTheNextService() = runBlocking {
        val source = FixtureSource(setOf(HealthService.WEIGHT.permission), data) {
            throw IllegalStateException("private provider error must not be shown")
        }
        assertEquals(HealthMetricStatus.ERROR, HealthServicesReader(source).read(HealthService.WEIGHT).status)
        source.onRead = {}
        assertEquals(HealthMetricStatus.READY, HealthServicesReader(source).read(HealthService.WEIGHT).status)
    }

    @Test fun providerSecurityExceptionMapsToPermissionRequired() = runBlocking {
        val source = FixtureSource(setOf(HealthService.WEIGHT.permission), data) { throw SecurityException() }
        val result = HealthServicesReader(source).read(HealthService.WEIGHT)
        assertEquals(HealthMetricStatus.PERMISSION_REQUIRED, result.status)
        assertTrue(result.values.isEmpty())
    }

    @Test fun backgroundCancellationMustNotBecomeAProviderError() = runBlocking {
        val source = FixtureSource(setOf(HealthService.WEIGHT.permission), data) { throw CancellationException() }
        try {
            HealthServicesReader(source).read(HealthService.WEIGHT)
            fail("Cancellation should propagate")
        } catch (_: CancellationException) { }
    }

    private class FixtureSource(
        var grants: Set<String> = emptySet(),
        private val result: HealthMetricResult = HealthMetricResult(HealthService.WEIGHT, HealthMetricStatus.NO_DATA),
        var onRead: FixtureSource.() -> Unit = {},
    ) : HealthServiceSource {
        var readCount = 0
        override suspend fun grantedPermissions() = grants
        override suspend fun read(service: HealthService): HealthMetricResult {
            readCount++
            onRead()
            return result
        }
    }
}
