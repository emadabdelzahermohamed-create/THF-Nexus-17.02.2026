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
            text = getString(R.string.health_permissions_rationale)
        }
        val column = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(Color.rgb(7, 18, 25))
            addView(text, ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT))
        }
        setContentView(ScrollView(this).apply { addView(column) })
    }
}
