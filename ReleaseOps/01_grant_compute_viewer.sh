#!/usr/bin/env bash
set -Eeuo pipefail

# THF ReleaseOps RC16 — minimal read-only IAM unblock
# This script grants the release-builder service account Compute Viewer only.
# It does NOT start/stop/delete VMs, deploy, sign builds, touch WAVE, or publish anything.

PROJECT_ID="project-b5e10d7e-8ce8-4aa4-a15"
SERVICE_ACCOUNT="thf-release-builder@project-b5e10d7e-8ce8-4aa4-a15.iam.gserviceaccount.com"
ROLE="roles/compute.viewer"

printf 'Project: %s\n' "$PROJECT_ID"
printf 'Service account: %s\n' "$SERVICE_ACCOUNT"
printf 'Role to grant: %s (read-only)\n' "$ROLE"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="$ROLE" \
  --condition=None

echo "THF_GCP_COMPUTE_VIEWER_GRANT=REQUESTED"
echo "Next: rerun GitHub Actions workflow 'THF GCP WIF Smoke'."
