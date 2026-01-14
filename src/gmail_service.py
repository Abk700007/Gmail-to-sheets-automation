import os
import time  
import socket 
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import config

def get_gmail_service():
    """Authenticates and returns the Gmail service."""
    creds = None
    if os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', config.SCOPES)
        except Exception:
            creds = None 

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None 

        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials/credentials.json', config.SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
    return build('gmail', 'v1', credentials=creds)

def fetch_unread_messages(service):
    """Fetches unread messages with auto-retry for stability."""
    max_retries = 3
    for attempt in range(max_retries):  # <--- THIS IS THE BONUS LOGIC
        try:
            results = service.users().messages().list(userId='me', q='is:unread').execute()
            return results.get('messages', [])
        except (socket.error, Exception) as e:
            print(f"Network glitch ({e}). Retrying... ({attempt + 1}/{max_retries})")
            time.sleep(2) # Wait 2 seconds before retrying
            
    print("Failed to connect after 3 attempts.")
    return []

def get_message_details(service, msg_id):
    """Fetches message details with auto-retry."""
    for attempt in range(3):
        try:
            return service.users().messages().get(userId='me', id=msg_id).execute()
        except Exception:
            time.sleep(1)
    return None

def mark_messages_as_read(service, msg_ids):
    if not msg_ids:
        return
    try:
        service.users().messages().batchModify(
            userId='me',
            body={'ids': msg_ids, 'removeLabelIds': ['UNREAD']}
        ).execute()
    except Exception as e:
        print(f"Warning: Could not mark as read: {e}")
