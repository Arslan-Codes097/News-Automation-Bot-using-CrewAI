import os
import json
from http.server import BaseHTTPRequestHandler
import gspread
from google.oauth2.service_account import Credentials


def get_news_rows():
    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    creds_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    
    if not creds_json:
        raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON environment variable is empty or not set in Vercel.")
        
    # Strip any accidental single quotes added during copy-paste
    creds_json = creds_json.strip("'").strip('"')
    
    try:
        creds_dict = json.loads(creds_json)
    except json.JSONDecodeError:
        raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON is not valid JSON. Ensure you didn't paste extra text.")

    credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)

    client = gspread.authorize(credentials)
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    sheet = client.open_by_key(sheet_id).sheet1

    records = sheet.get_all_records()
    records.reverse()
    return records


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            rows = get_news_rows()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(rows).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
