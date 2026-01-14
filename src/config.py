# src/config.py

SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify', 
    'https://www.googleapis.com/auth/spreadsheets'
]

# PASTE YOUR WORKING SPREADSHEET ID HERE
SPREADSHEET_ID = "Enter you spreadsheet ID" 

STATE_FILE = "processed_emails.json"
BATCH_SIZE = 20
