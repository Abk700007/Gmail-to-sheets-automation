# Gmail to Google Sheets Automation

## Project Overview
This tool automates the process of reading incoming emails from a Gmail account and logging them into a Google Sheet. It uses the official Google APIs to fetch unread emails, parses their content, and appends them to a spreadsheet while ensuring no duplicates are created.

## Architecture
**Flow:** `Gmail API` -> `Python Script` -> `State Check` -> `Google Sheets API`

1.  **Authentication:** Uses OAuth 2.0 (User Credentials) to securely access Gmail and Sheets.
2.  **Fetch:** Retrieves only messages marked as `UNREAD`.
3.  **Parse:** Extracts `From`, `Subject`, `Date`, and cleans the `Body` (HTML to Text).
4.  **Filter:** Checks `processed_emails.json` to skip emails already logged.
5.  **Upload:** Sends data to Google Sheets in batches of 20 to prevent timeouts.
6.  **Update:** Marks emails as `READ` and saves the new IDs to the local state file.

## Setup Instructions
1.  **Clone the repository**
2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Google Cloud Setup:**
    * Create a project in Google Cloud Console.
    * Enable **Gmail API** and **Google Sheets API**.
    * Create **OAuth 2.0 Client IDs** (Desktop App).
    * Download the JSON file and save it as `credentials/credentials.json`.
4.  **Configuration:**
    * Open `src/config.py`.
    * Add your `SPREADSHEET_ID`.
5.  **Run the Application:**
    ```bash
    python src/main.py
    ```

## Design Decisions
* **State Persistence:** I used a local JSON file (`processed_emails.json`) to store a set of unique Message IDs. This is faster (O(1) lookup time) than querying the Google Sheet to check if an email exists.
* **Batch Processing:** Instead of uploading emails one by one, the script processes them in batches of 20. This prevents API rate limits and network timeouts.
* **HTML Parsing:** Used `BeautifulSoup` to strip HTML tags from email bodies, ensuring the Google Sheet contains readable plain text.

## Challenges Faced & Solutions
1.  **Network Timeouts:** The script initially crashed when trying to upload 100+ emails at once. **Solution:** Implemented batching (20 emails per request) and increased the socket default timeout to 600 seconds.
2.  **Payload Size Limits:** Google Sheets API rejected requests with cells larger than 50,000 characters. **Solution:** Added logic to truncate email bodies to 30,000 characters before uploading.
3.  **OAuth Scopes:** Initially faced 403 Forbidden errors because the "Edit Sheets" permission wasn't checked during the consent screen. **Solution:** Deleted the token, re-authenticated, and explicitly checked all permission boxes.

## Limitations
* The script must be run locally; it is not deployed to the cloud.
* It does not handle email attachments, only text content.

## Submitted By Abhiranjan Kumar