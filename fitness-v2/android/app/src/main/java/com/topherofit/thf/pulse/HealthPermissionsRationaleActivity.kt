package com.topherofit.thf.pulse

import android.app.Activity
import android.graphics.Color
import android.os.Bundle
import android.text.method.LinkMovementMethod
import android.view.ViewGroup
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView

class HealthPermissionsRationaleActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val padding = (24 * resources.displayMetrics.density).toInt()
        val text = TextView(this).apply {
            setTextColor(Color.rgb(239, 245, 247))
            textSize = 17f
            setPadding(padding, padding, padding, padding)
            movementMethod = LinkMovementMethod.getInstance()
            setText(
                """
                Top Hero Fit وHealth Connect

                نقرأ الخطوات، جلسات التمرين، المسافة والسعرات النشطة فقط لعرض ملخص نشاطك. نكتب جلسات THF التي تُكملها كي تظهر في التطبيقات المتوافقة. لا نطلب نبض القلب أو النوم أو الوزن في هذا الإصدار.

                يمكنك رفض أي إذن أو سحبه لاحقًا من إعدادات Health Connect. سيظل تسجيل التمرين المحلي يعمل دون اتصال.

                Top Hero Fit reads steps, exercise sessions, distance, and active calories only for your activity summary. Completed THF workouts can be written to Health Connect. Heart rate, sleep, and weight are not requested in this version. Permissions can be revoked at any time; offline workout logging continues to work.
                """.trimIndent(),
            )
        }
        val column = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(Color.rgb(7, 18, 25))
            addView(text, ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT))
        }
        setContentView(ScrollView(this).apply { addView(column) })
    }
}
