# THF Fitness Android Production Signing Contract

This contract is release-only and fail-closed. It does not store signing material in source.

Required GitHub Actions secrets:
- `ANDROID_UPLOAD_KEYSTORE_B64` — base64 of the Play upload keystore.
- `ANDROID_UPLOAD_STORE_PASSWORD`
- `ANDROID_UPLOAD_KEY_ALIAS`
- `ANDROID_UPLOAD_KEY_PASSWORD`

The CI workflow checks only whether all four inputs are present. Values are never printed. When present, the keystore is decoded into the ephemeral GitHub runner, `apply_android_signing.py` patches the downloaded canonical RC2 Gradle file, and Gradle receives credentials through environment variables.

The signed AAB is still not publishable until the remaining Android/physical-device and Play gates pass.

If the existing Play app does not recognize the supplied upload certificate, the owner must use Google Play Console's Play App Signing upload-key reset/registration flow. Do not replace the app signing key.
