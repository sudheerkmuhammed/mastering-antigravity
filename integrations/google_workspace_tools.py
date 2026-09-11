"""
Google Workspace Integration for Google Antigravity.
Connects Antigravity with Google Sheets (audit logging, metric reporting)
and Gmail (triage, automatic incident notification).
"""

import os
import datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account


def get_sheets_service():
    """Initializes and returns the Google Sheets API v4 service."""
    creds_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_PATH", "service_account.json")
    if not os.path.exists(creds_path):
        raise FileNotFoundError(f"Service account file not found at: {creds_path}")

    credentials = service_account.Credentials.from_service_account_file(
        creds_path,
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    return build("sheets", "v4", credentials=credentials)


def append_incident_log(spreadsheet_id: str, service_name: str, issue: str, fix_summary: str):
    """
    Appends an incident record row to a Google Sheet.
    Columns: [Timestamp, Service Name, Issue Description, Fix Summary, Status]
    """
    service = get_sheets_service()
    timestamp = datetime.datetime.utcnow().isoformat() + "Z"

    row_data = [timestamp, service_name, issue, fix_summary, "RESOLVED"]

    body = {"values": [row_data]}
    result = (
        service.spreadsheets()
        .values()
        .append(
            spreadsheetId=spreadsheet_id,
            range="Sheet1!A:E",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body=body,
        )
        .execute()
    )

    print(f"[+] Appended row to Google Sheet. Updated cells: {result.get('updates', {}).get('updatedCells')}")
    return result


def send_gmail_notification(to_email: str, subject: str, body_text: str):
    """
    Sends an incident post-mortem / notification email via Gmail API or SMTP.
    """
    import smtplib
    from email.mime.text import MIMEText

    smtp_user = os.getenv("GMAIL_USER")
    smtp_pass = os.getenv("GMAIL_APP_PASSWORD")

    if not smtp_user or not smtp_pass:
        print("[!] GMAIL_USER or GMAIL_APP_PASSWORD not configured. Mocking email delivery:")
        print(f"To: {to_email}\nSubject: {subject}\nBody:\n{body_text}")
        return True

    msg = MIMEText(body_text)
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)

    print(f"[+] Email successfully dispatched to {to_email}")
    return True


if __name__ == "__main__":
    print("[*] Testing Google Workspace Tool Mock Dispatch...")
    send_gmail_notification(
        to_email="devops-team@company.com",
        subject="[ALERT RESOLVED] Memory Leak in AuthService",
        body_text="Antigravity has patched the memory leak in auth_service.go and verified with go test.",
    )
