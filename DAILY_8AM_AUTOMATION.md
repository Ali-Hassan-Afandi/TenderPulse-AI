# Daily 8:00 AM Tender Email Automation
Streamlit Community Cloud can sleep, so do not schedule the 8 AM job inside Streamlit.
Recommended production architecture:
1. Daily cloud job runs at 08:00 Pakistan time.
2. It discovers public tenders, normalizes them, scores them against saved company profiles.
3. It writes tenders/matches to Supabase.
4. It emails only new qualifying matches and records alerts.

For the hackathon, the UI includes manual "Send email now". For unattended daily delivery, deploy a Supabase Edge Function (or GitHub Actions scheduled workflow) and trigger it with Supabase Cron. Keep SMTP/Groq credentials in that scheduler's secret store. Do not move them into GitHub or TOML committed to the repo.
Pakistan Standard Time is UTC+5, so 08:00 PKT corresponds to 03:00 UTC when a scheduler expects UTC. Verify the scheduler timezone before saving the job.
