import os
import json
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class SheetsLoggerInput(BaseModel):
    headline: str = Field(description="Article headline")
    summary: str = Field(description="Short summary of the article")
    link: str = Field(description="Source URL of the article")


class SheetsLoggerTool(BaseTool):
    name: str = "sheets_logger"
    description: str = "Logs a news update as a new row in Google Sheets"
    args_schema: type[BaseModel] = SheetsLoggerInput

    def _run(self, headline: str, summary: str, link: str) -> str:
        import time
        time.sleep(15)
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]

        creds_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        creds_dict = json.loads(creds_json)
        credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)

        client = gspread.authorize(credentials)
        sheet_id = os.getenv("GOOGLE_SHEET_ID")
        sheet = client.open_by_key(sheet_id).sheet1

        row = [datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"), headline, summary, link]
        sheet.append_row(row)

        return f"Logged to Sheets: {headline}"
