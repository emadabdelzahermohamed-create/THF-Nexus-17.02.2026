package com.topherofit.thf.pulse;

import android.app.Activity;
import android.graphics.Color;
import android.os.Bundle;
import android.view.Gravity;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import java.util.Locale;

public final class PermissionsRationaleActivity extends Activity {
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        boolean ar = Locale.getDefault().getLanguage().startsWith("ar");
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setGravity(Gravity.CENTER);
        root.setPadding(48,48,48,48);
        root.setBackgroundColor(0xFF07111F);
        TextView title = new TextView(this);
        title.setTextColor(Color.WHITE); title.setTextSize(24);
        title.setText(ar ? "بيانات الصحة واللياقة" : "Health & fitness data");
        TextView body = new TextView(this);
        body.setTextColor(0xFFCBD5E1); body.setTextSize(16); body.setPadding(0,24,0,32);
        body.setText(ar ? "يستخدم Top Hero Fit بيانات الخطوات وجلسات التمرين بعد موافقتك فقط لعرض التقدم ومزامنة الجلسات. يمكنك إلغاء الصلاحيات في أي وقت من Health Connect."
                : "Top Hero Fit uses steps and exercise sessions only after your permission to show progress and synchronize workouts. You can revoke access at any time in Health Connect.");
        Button done = new Button(this);
        done.setText(ar ? "فهمت" : "Got it"); done.setOnClickListener(v -> finish());
        root.addView(title); root.addView(body); root.addView(done);
        setContentView(root);
    }
}
