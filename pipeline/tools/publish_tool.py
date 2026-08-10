import os
import json
import time
import requests
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

class PublishToolInput(BaseModel):
    headline: str = Field(description="Article headline")
    summary: str = Field(description="Short summary of the article")
    link: str = Field(description="Source URL of the article")

class PublishTool(BaseTool):
    name: str = "publish_news"
    description: str = "Publishes a news update by posting it to Slack AND logging it to Google Sheets simultaneously."
    args_schema: type[BaseModel] = PublishToolInput

    def _run(self, headline: str, summary: str, link: str) -> str:
        # Sleep for 15 seconds to respect Gemini API free tier rate limit
        time.sleep(15)
        
        # 1. Post to Slack
        webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        slack_link = link
        if not slack_link.startswith("http") and slack_link.lower() not in ["n/a", "none", "", "null"]:
            slack_link = "https://" + slack_link
            
        if slack_link.lower() in ["n/a", "none", "", "null"]:
            text = f"*{headline}*\n{summary}"
        else:
            text = f"*{headline}*\n{summary}\n<{slack_link}|Read more>"

        message = {"text": text}
        try:
            response = requests.post(webhook_url, json=message, timeout=15)
            response.raise_for_status()
        except Exception as e:
            return f"Error posting to Slack: {e}"

        # 2. Log to Sheets
        try:
            scopes = ["https://www.googleapis.com/auth/spreadsheets"]
            creds_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
            creds_dict = json.loads(creds_json)
            credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
            client = gspread.authorize(credentials)
            sheet_id = os.getenv("GOOGLE_SHEET_ID")
            sheet = client.open_by_key(sheet_id).sheet1
            row = [datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"), headline, summary, link]
            sheet.append_row(row)
        except Exception as e:
            return f"Error logging to Sheets: {e}"

        return f"Successfully published to Slack and logged to Sheets: {headline}"
