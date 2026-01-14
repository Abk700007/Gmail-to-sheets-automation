import base64
from bs4 import BeautifulSoup

def clean_text(text):
    """Removes extra whitespace and newlines."""
    if text:
        return " ".join(text.split())
    return ""

def parse_email(message):
    """
    Extracts From, Subject, Date, and Body from a Gmail message object.
    """
    payload = message.get('payload', {})
    headers = payload.get('headers', [])

    # 1. Extract Headers
    subject = "No Subject"
    sender = "Unknown"
    date_received = ""

    for h in headers:
        name = h.get('name', '').lower()
        if name == 'subject':
            subject = h.get('value')
        elif name == 'from':
            sender = h.get('value')
        elif name == 'date':
            date_received = h.get('value')

    # 2. Extract Body
    body = ""
    if 'parts' in payload:
        for part in payload['parts']:
            mime_type = part.get('mimeType')
            data = part['body'].get('data')
            if mime_type == 'text/plain' and data:
                body = base64.urlsafe_b64decode(data).decode()
                break # Prefer plain text
            elif mime_type == 'text/html' and data:
                html_content = base64.urlsafe_b64decode(data).decode()
                soup = BeautifulSoup(html_content, 'html.parser')
                body = soup.get_text() # Fallback to stripped HTML
    elif 'body' in payload:
        data = payload['body'].get('data')
        if data:
            try:
                # Try decoding as standard text/html
                content = base64.urlsafe_b64decode(data).decode()
                if "DOCTYPE" in content or "<html" in content:
                    soup = BeautifulSoup(content, 'html.parser')
                    body = soup.get_text()
                else:
                    body = content
            except:
                pass

    return {
        "id": message['id'],
        "From": sender,
        "Subject": subject,
        "Date": date_received,
        "Content": clean_text(body)
    }