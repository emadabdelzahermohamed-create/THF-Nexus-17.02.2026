#!/usr/bin/env bash
set -Eeuo pipefail

# THF ReleaseOps RC16 — least-privilege SSH/IAP grants for GitHub Actions.
# No VM start/stop/delete permission is granted here.
# No production signing, Play, Cloudflare, Solana, or WAVE action is performed.

PROJECT_ID="project-b5e10d7e-8ce8-4aa4-a15"
AUTOMATION_SA="thf-release-builder@project-b5e10d7e-8ce8-4aa4-a15.iam.gserviceaccount.com"
VM_ATTACHED_SA="1035420130588-compute@developer.gserviceaccount.com"
MEMBER="serviceAccount:${AUTOMATION_SA}"

echo "[1/3] Grant OS Login (non-admin)"
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="$MEMBER" \
  --role="roles/compute.osLogin" \
  --condition=None

echo "[2/3] Grant IAP TCP tunnel access"
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="$MEMBER" \
  --role="roles/iap.tunnelResourceAccessor" \
  --condition=None

echo "[3/3] Allow acting as the VM-attached service account for OS Login authorization"
gcloud iam service-accounts add-iam-policy-binding "$VM_ATTACHED_SA" \
  --project="$PROJECT_ID" \
  --member="$MEMBER" \
  --role="roles/iam.serviceAccountUser"

echo "THF_IAP_OSLOGIN_IAM_GRANTS=REQUESTED"
echo "Next: GitHub Actions SSH/IAP smoke test only."
