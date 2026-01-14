import os
from google.oauth2.credentials import Credentials # <--- CRITICAL: MUST BE oauth2
from googleapiclient.discovery import build
import config

def get_sheets_service():
    """Authenticates and returns the Sheets service."""
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', config.SCOPES)
        return build('sheets', 'v4', credentials=creds)
    else:
        raise FileNotFoundError("token.json not found. Run Gmail service first to authenticate.")

def append_to_sheet(service, rows):
    """Appends rows to the configured spreadsheet."""
    body = {'values': rows}
    service.spreadsheets().values().append(
        spreadsheetId=config.SPREADSHEET_ID, 
        range="Sheet1!A1",
        valueInputOption="RAW", 
        body=body
    ).execute()