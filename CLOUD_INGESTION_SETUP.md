# TenderPulse V6 Cloud Ingestion Setup

## 1. Supabase
Run `supabase_v6_migration.sql` once in Supabase SQL Editor.

## 2. GitHub repository secrets
GitHub → repository → Settings → Secrets and variables → Actions → New repository secret.
Add:
SUPABASE_URL
SUPABASE_KEY
SMTP_HOST
SMTP_PORT
SMTP_USER
SMTP_PASSWORD
SMTP_FROM

Do not put secret values in GitHub files.

## 3. First manual cloud sync
GitHub → Actions → TenderPulse Public Tender Sync → Run workflow.
Then inspect the run log. The worker reports fetched/saved counts and connector health.

## 4. Automatic sync
`.github/workflows/tender-sync.yml` runs hourly at minute 17.
GitHub Actions scheduled jobs can be delayed under platform load; the database stores sync history.

## 5. Daily email
`.github/workflows/daily-email.yml` is scheduled at `0 3 * * *`, i.e. 03:00 UTC = 08:00 Pakistan Standard Time.
It reads saved companies and cached live tenders from Supabase, calculates matches and emails up to 10 matches.

## 6. Streamlit
No TOML change is required. Streamlit keeps its existing secrets.
The UI can read the same Supabase tables and show cached live records even when a source portal is temporarily unavailable.

## Connector policy
A connector returning zero records is NOT replaced with fake live data. The UI shows the connector state explicitly.
Government websites can change HTML without notice. Check `source_sync_runs` after deployments and when a portal changes.
