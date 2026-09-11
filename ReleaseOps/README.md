# THF ReleaseOps — RC16

> Platform/release operations only. No THF service/game/UX logic changes. WAVE is untouched.

## Current gate

- Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`
- GCP project: `project-b5e10d7e-8ce8-4aa4-a15`
- GCP project number: `1035420130588`
- WIF pool: `thf-github-pool`
- WIF provider: `thf-github-provider`
- WIF provider resource: `projects/1035420130588/locations/global/workloadIdentityPools/thf-github-pool/providers/thf-github-provider`
- Service account: `thf-release-builder@project-b5e10d7e-8ce8-4aa4-a15.iam.gserviceaccount.com`
- Private builder VM: `thf-wave-builder`
- Zone: `europe-west1-b`
- Machine type: `e2-standard-4`
- Persistent service-account key: **not required**

## Safety boundary / حدود الأمان

The first GitHub Actions gate is deliberately read-only against GCP. It authenticates with OIDC/WIF, verifies the project identity, and reads the prepared builder VM metadata. It does **not** deploy Cloud Run, start/stop/delete the VM, create keys, sign production builds, publish to Google Play, alter Cloudflare, or touch Solana.

أول اختبار GitHub Actions مقصود أن يكون للقراءة فقط داخل GCP: يتحقق من WIF وهوية المشروع ووجود VM البناء. لا يقوم بالنشر أو التوقيع أو حذف/تشغيل موارد أو تعديل WAVE.

## RC16 next executable gate

After WIF runtime verification passes, stage the exact RC16 source artifacts to the prepared private x86_64 builder and run the existing unsigned/test build + package-inspection chain. Collect APK/AAB/evidence SHA only. Production signing and irreversible Play actions remain outside this gate.

See `rc16-intake.json` for the exact pinned source contracts and hashes.
