import sys
import json
import os
import socket
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime # <--- NEW: For parsing email dates
from gmail_service import get_gmail_service, fetch_unread_messages, get_message_details, mark_messages_as_read
from sheets_service import get_sheets_service, append_to_sheet
from email_parser import parse_email
import config

# Fix Timeout
socket.setdefaulttimeout(600)

def load_processed_ids():
    if os.path.exists(config.STATE_FILE):
        with open(config.STATE_FILE, "r") as f:
            try:
                return set(json.load(f))
            except json.JSONDecodeError:
                return set()
    return set()

def save_processed_ids(processed_ids):
    with open(config.STATE_FILE, "w") as f:
        json.dump(list(processed_ids), f)

def main():
    print("Authenticate...")
    try:
        gmail_service = get_gmail_service()
        sheets_service = get_sheets_service()
    except Exception as e:
        print(f"Authentication Failed: {e}")
        return

    processed_ids = load_processed_ids()
    print("Checking for new emails...")
    
    # --- MODIFICATION TASK: Define 24-hour cutoff ---
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
    print(f"Modification Task Active: Filtering emails received after {cutoff_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    
    messages = fetch_unread_messages(gmail_service)
    
    if not messages:
        print("No unread emails found.")
        return

    print(f"Found {len(messages)} unread emails. Processing...")

    current_batch_rows = []
    current_batch_ids = []

    for index, msg in enumerate(messages):
        msg_id = msg['id']
        if msg_id in processed_ids:
            continue

        try:
            msg_detail = get_message_details(gmail_service, msg_id)
            email_data = parse_email(msg_detail)
            
            # --- START MODIFICATION LOGIC ---
            # Check if the email is older than 24 hours
            try:
                # Parse the date string from Gmail headers into a datetime object
                email_date = parsedate_to_datetime(email_data['Date'])
                
                # Compare email date with our cutoff time
                if email_date < cutoff_time:
                    print(f"Skipping old email from {email_date} (Older than 24h)")
                    
                    # We mark it as read so we don't fetch it again next time
                    mark_messages_as_read(gmail_service, [msg_id])
                    processed_ids.add(msg_id)
                    continue
            except Exception as e:
                print(f"Warning: Date parsing error for email {msg_id}: {e}. Processing anyway.")
            # --- END MODIFICATION LOGIC ---
            
            # Truncate content to 30k chars
            clean_content = email_data['Content']
            if len(clean_content) > 30000:
                clean_content = clean_content[:30000] + "... [TRUNCATED]"

            current_batch_rows.append([
                email_data['From'], 
                email_data['Subject'], 
                email_data['Date'], 
                clean_content
            ])
            current_batch_ids.append(msg_id)
            print(f"Parsed {index + 1}/{len(messages)}", end="\r")

            # UPLOAD BATCH
            if len(current_batch_rows) >= config.BATCH_SIZE:
                print(f"\nUploading batch of {len(current_batch_rows)}...")
                append_to_sheet(sheets_service, current_batch_rows)
                mark_messages_as_read(gmail_service, current_batch_ids)
                processed_ids.update(current_batch_ids)
                save_processed_ids(processed_ids)
                
                current_batch_rows = []
                current_batch_ids = []
                print("Batch saved!")

        except KeyboardInterrupt:
            print("\nUser stopped script.")
            break
        except Exception as e:
            print(f"Error processing {msg_id}: {e}")

    # FINAL BATCH
    if current_batch_rows:
        print(f"\nUploading final batch of {len(current_batch_rows)}...")
        append_to_sheet(sheets_service, current_batch_rows)
        mark_messages_as_read(gmail_service, current_batch_ids)
        processed_ids.update(current_batch_ids)
        save_processed_ids(processed_ids)
        print("Final batch saved!")
    
    # Save state one last time to be safe
    save_processed_ids(processed_ids)
    print("\nJob Done.")

if __name__ == '__main__':
    main()