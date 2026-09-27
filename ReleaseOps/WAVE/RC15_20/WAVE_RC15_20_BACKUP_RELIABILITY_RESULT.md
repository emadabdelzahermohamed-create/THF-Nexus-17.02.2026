# WAVE RC15.20 Backup Reliability Result

Status: **PASS**

Verified at: 2026-09-27T03:55:06Z  
Candidate preserved: Android versionCode `15302` / versionName `1.0.0-rc15.15-twa-fix`  
Workflow source commit: `04828498140f908f64e53cdf6c281b470a535c0b`  
Workflow run: [36292648069](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/36292648069)

## What was verified

- Exported the current production Cloudflare D1 database `wave-mawja-prod`.
- Used the existing Cloudflare credentials and GitHub-to-GCP Workload Identity Federation; no long-lived JSON key was created.
- Staged the SQL export and its SHA-256 manifest privately at `~/wave-backups/RC15_20/36292648069/` on the authorized GCP builder.
- Confirmed the backup was fresh (5 seconds old at verification).
- Confirmed both staged files were non-empty: 2 files, 57,751 total bytes.
- Validated the stored checksum manifest.
- Restored `WAVE_D1_RC15_20_20260927T035242Z.sql` into an isolated temporary SQLite database.
- Ran SQLite `PRAGMA quick_check`; result was `ok`.
- Removed the temporary restored database after verification.
- Did not upload database contents to GitHub artifacts or print database contents to logs.

## Durable evidence

- Result: `RESULT=PASS`
- SQL restores verified: `1`
- Checksum manifests verified: `1`
- Evidence artifact: [WAVE-RC15-20-BACKUP-RELIABILITY-EVIDENCE / 10923106100](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/36292648069/artifacts/10923106100)
- Artifact ZIP SHA-256: `68d462ab9bbac5e6bc019f2d60c2c212663a681fe0d91aadc0d821ae647268df`
- Artifact retention expiry: 2026-10-27T03:55:06Z

The earlier read-only inventory run `36292511097` exposed that the prior RC15.3 backup was stale (2026-09-17). It is superseded by the fresh RC15.20 backup and is not counted as the release reliability PASS.

## Release impact

This closes the backup/reliability evidence gap without changing the live Worker, Android candidate, Play Internal release, authentication, DRM/paywall behavior, or approved application functionality.

The independent Google Play production-access blocker remains unchanged: the owner must run the Closed test with at least 12 real testers continuously for 14 days, then apply for production access.
