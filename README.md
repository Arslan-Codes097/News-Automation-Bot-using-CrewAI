# News Automation Bot

Multi-agent CrewAI pipeline that fetches news, summarizes it, posts to
Slack, and logs it to Google Sheets — fully automated, no manual trigger.

## How it's split

- `pipeline/` runs entirely inside GitHub Actions, on a schedule (every 6
  hours). This is where the CrewAI agents, custom tools, and all the actual
  work happen. It is not deployed anywhere — it just runs on GitHub's
  servers and exits.
- `dashboard/` is a small read-only app deployed to Vercel. It reads the same
  Google Sheet the pipeline writes to, and displays it as a webpage. It has
  no CrewAI logic and does nothing on a schedule — it only responds when
  someone visits the page.

The two pieces never talk to each other directly. Google Sheets is the
shared data store connecting them.

## Setup

1. Create the Google Sheet and service account (see chat history / setup
   steps). Share the Sheet with the service account's email as Editor.
2. Copy `pipeline/.env.example` to `pipeline/.env` and fill in your real
   keys for local testing.
3. Test locally:
   ```
   cd pipeline
   pip install -r requirements.txt
   python main.py
   ```
4. Once it works locally, add the same 5 values as GitHub repo secrets:
   Settings > Secrets and variables > Actions > New repository secret.
5. Push to GitHub. Use the Actions tab > "Run News Pipeline" >
   "Run workflow" to trigger it manually and confirm it works before relying
   on the schedule.
6. Deploy the dashboard: import the repo into Vercel, set the root directory
   to `dashboard/`, add `GOOGLE_SHEET_ID` and `GOOGLE_SERVICE_ACCOUNT_JSON`
   as Vercel environment variables, deploy.

## Notes

- The Sheet's service account needs Editor access for the pipeline (it
  writes rows) and can stay Editor for the dashboard too, even though the
  dashboard only reads.
- `GOOGLE_SERVICE_ACCOUNT_JSON` should be pasted as the full JSON key
  content, on one line, into both GitHub secrets and Vercel env vars.
