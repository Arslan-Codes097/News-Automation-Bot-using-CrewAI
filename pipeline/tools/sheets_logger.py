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
        try:
            scopes = ["https://www.googleapis.com/auth/spreadsheets"]
            creds_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")
            
            # Robust parsing for GitHub Actions secrets that might contain surrounding quotes
            if creds_json.startswith("'") and creds_json.endswith("'"):
                creds_json = creds_json[1:-1]
            elif creds_json.startswith('"') and creds_json.endswith('"'):
                creds_json = creds_json[1:-1]
                
            creds_dict = json.loads(creds_json)
            if "private_key" in creds_dict:
                creds_dict["private_key"] = creds_dict["private_key"].replace('\\n', '\n')
            
            credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)

            client = gspread.authorize(credentials)
            sheet_id = os.getenv("GOOGLE_SHEET_ID")
            sheet = client.open_by_key(sheet_id).sheet1

            row = [datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"), headline, summary, link]
            sheet.append_row(row)

            return f"Logged to Sheets: {headline}"
        except Exception as e:
            print(f"Error in Google Sheets Logger: {e}")
            return f"Error logging to Sheets: {e}"
