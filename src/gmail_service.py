import os
from google.oauth2.credentials import Credentials  
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import config

def get_gmail_service():
    """Authenticates and returns the Gmail service."""
    creds = None
    # 1. Try to load existing token
    if os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', config.SCOPES)
        except Exception:
            creds = None 

    # 2. If no valid token, create a new one
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None # Refresh failed, force re-login

        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials/credentials.json', config.SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the new token
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
    return build('gmail', 'v1', credentials=creds)

def fetch_unread_messages(service):
    results = service.users().messages().list(userId='me', q='is:unread').execute()
    return results.get('messages', [])

def get_message_details(service, msg_id):
    return service.users().messages().get(userId='me', id=msg_id).execute()

def mark_messages_as_read(service, msg_ids):
    if not msg_ids:
        return
    service.users().messages().batchModify(
        userId='me',
        body={'ids': msg_ids, 'removeLabelIds': ['UNREAD']}
    ).execute()