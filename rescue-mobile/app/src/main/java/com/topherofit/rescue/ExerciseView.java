package com.topherofit.rescue;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.os.SystemClock;
import android.view.View;

final class ExerciseView extends View {
    private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private boolean running;
    private int mode;

    ExerciseView(Context context) {
        super(context);
        paint.setStrokeCap(Paint.Cap.ROUND);
        running = false;
    }

    void setRunning(boolean value) { running = value; invalidate(); }
    void setMode(int value) { mode = value; invalidate(); }

    @Override protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        canvas.drawColor(Color.rgb(20, 32, 41));
        float w = getWidth();
        float h = getHeight();
        float phase = running ? (float) Math.sin(SystemClock.uptimeMillis() / 230.0) : 0f;
        float cx = w * 0.5f;
        float cy = h * 0.48f;
        float squat = mode == 1 ? Math.abs(phase) * h * 0.08f : 0f;
        float knee = mode == 2 ? Math.max(0f, phase) * h * 0.08f : 0f;
        float arm = (mode == 0 || mode == 3) ? phase * w * 0.12f : phase * w * 0.04f;
        float leg = mode == 0 ? phase * w * 0.10f : 0f;

        paint.setColor(Color.rgb(0, 210, 165));
        paint.setStyle(Paint.Style.STROKE);
        paint.setStrokeWidth(Math.max(8f, w / 38f));
        float headY = cy - h * 0.22f + squat;
        canvas.drawCircle(cx, headY, Math.min(w, h) * 0.055f, paint);
        canvas.drawLine(cx, cy - h * 0.14f + squat, cx, cy + h * 0.10f + squat, paint);
        canvas.drawLine(cx, cy - h * 0.07f + squat, cx - w * 0.14f - arm, cy + h * 0.02f - Math.abs(arm) * 0.25f + squat, paint);
        canvas.drawLine(cx, cy - h * 0.07f + squat, cx + w * 0.14f + arm, cy + h * 0.02f - Math.abs(arm) * 0.25f + squat, paint);
        canvas.drawLine(cx, cy + h * 0.10f + squat, cx - w * 0.10f - leg, cy + h * 0.28f + squat - knee, paint);
        canvas.drawLine(cx, cy + h * 0.10f + squat, cx + w * 0.10f + leg, cy + h * 0.28f + squat + knee, paint);

        paint.setStyle(Paint.Style.FILL);
        paint.setColor(Color.WHITE);
        paint.setTextSize(Math.max(24f, w / 18f));
        canvas.drawText(running ? "AUTO MOTION" : "PAUSED", 20f, h - 24f, paint);
        if (running) postInvalidateOnAnimation();
    }
}
