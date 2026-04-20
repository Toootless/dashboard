"""Service to interact with Gmail API"""

import os
import json
import base64
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GmailService:
    """Handles Gmail API interactions"""

    def __init__(self, config):
        self.config = config
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """
        Authenticate with Gmail API using OAuth 2.0.

        Flow:
        1. If a valid token.json exists, load and (if needed) refresh it.
        2. If no valid token exists, run the local OAuth browser flow to
           create one, then save it for future runs.

        The 403 'access blocked' error from Google means the Google Cloud
        project's OAuth consent screen is in **Testing** mode and the
        account being used hasn't been added as a test user.  Fix:
        https://console.cloud.google.com/apis/credentials/consent
        -> Add your Gmail address under "Test users".
        """
        creds = None
        token_file = self.config.get('TOKEN_FILE', 'token.json')
        credentials_file = self.config.get('CREDENTIALS_FILE', 'credentials.json')
        scopes = self.config.get('SCOPES', ['https://www.googleapis.com/auth/gmail.readonly'])

        # ------------------------------------------------------------------
        # Step 1: Load existing token if it's there
        # ------------------------------------------------------------------
        if os.path.exists(token_file):
            try:
                creds = Credentials.from_authorized_user_file(token_file, scopes)
                print(f"[Gmail] Loaded existing token from {token_file}")
            except Exception as e:
                print(f"[Gmail] Could not load token file ({e}) – will re-authenticate.")
                creds = None

        # ------------------------------------------------------------------
        # Step 2: Refresh if expired, or run the browser flow if no creds
        # ------------------------------------------------------------------
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    print("[Gmail] Token expired – refreshing...")
                    creds.refresh(Request())
                    print("[Gmail] Token refreshed successfully.")
                except Exception as e:
                    print(f"[Gmail] Token refresh failed ({e}) – will re-authenticate.")
                    creds = None

            if not creds or not creds.valid:
                # Need a brand-new authorisation
                if not os.path.exists(credentials_file):
                    print(
                        f"[Gmail] ERROR: credentials file '{credentials_file}' not found.\n"
                        "Download it from https://console.cloud.google.com/apis/credentials"
                    )
                    return

                print(
                    "[Gmail] Opening browser for Google OAuth consent...\n"
                    "        If you see 'Access blocked', go to:\n"
                    "        https://console.cloud.google.com/apis/credentials/consent\n"
                    "        and add your Gmail address under 'Test users'."
                )
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_file, scopes
                    )
                    # port=0 lets the OS pick a free port automatically
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    print(f"[Gmail] OAuth flow failed: {e}")
                    return

            # ----------------------------------------------------------------
            # Step 3: Save the (new or refreshed) token for next time
            # ----------------------------------------------------------------
            try:
                with open(token_file, 'w') as f:
                    f.write(creds.to_json())
                print(f"[Gmail] Token saved to {token_file}")
            except Exception as e:
                print(f"[Gmail] WARNING: Could not save token ({e}). You may need to re-auth next run.")

        # ------------------------------------------------------------------
        # Step 4: Build the Gmail API service
        # ------------------------------------------------------------------
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            print("[Gmail] Gmail service authenticated successfully.")
        except Exception as e:
            print(f"[Gmail] Failed to build Gmail service: {e}")

    # -----------------------------------------------------------------------
    # Public methods
    # -----------------------------------------------------------------------

    def get_job_emails(self):
        """Get emails from the configured Gmail folder/label"""
        if not self.service:
            print("[Gmail] Service not authenticated – skipping email fetch.")
            return []

        try:
            # Find the label ID for the configured folder name
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])

            job_folder = self.config.get('GMAIL_FOLDER', 'JobHunt')
            job_label_id = None
            for label in labels:
                if label['name'].lower() == job_folder.lower():
                    job_label_id = label['id']
                    break

            if not job_label_id:
                print(f"[Gmail] Label '{job_folder}' not found in Gmail. "
                      "Make sure the label exists exactly as configured.")
                return []

            # Fetch messages under that label
            results = self.service.users().messages().list(
                userId='me',
                labelIds=[job_label_id],
                q='is:unread OR subject:(reply OR response OR feedback OR interview)',
                maxResults=100
            ).execute()

            messages = results.get('messages', [])
            emails = []
            for msg in messages:
                email_data = self._parse_message(msg['id'])
                if email_data:
                    emails.append(email_data)

            print(f"[Gmail] Fetched {len(emails)} email(s) from '{job_folder}'.")
            return emails

        except HttpError as e:
            print(f"[Gmail] HTTP error while fetching emails: {e}")
            return []
        except Exception as e:
            print(f"[Gmail] Unexpected error fetching emails: {e}")
            return []

    # -----------------------------------------------------------------------
    # Private helpers
    # -----------------------------------------------------------------------

    def _parse_message(self, message_id):
        """Parse a single email message into a dict"""
        if not self.service:
            return None
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
            sender  = next((h['value'] for h in headers if h['name'] == 'From'), '')
            date    = next((h['value'] for h in headers if h['name'] == 'Date'), '')

            # Extract plain-text body (handles simple and multipart messages)
            body = self._extract_body(message['payload'])

            return {
                'id': message_id,
                'subject': subject,
                'from': sender,
                'date': date,
                'body': body[:500],
                'has_reply': self._contains_reply_keywords(
                    subject.lower() + ' ' + body.lower()
                )
            }

        except Exception as e:
            print(f"[Gmail] Error parsing message {message_id}: {e}")
            return None

    def _extract_body(self, payload):
        """Recursively extract text/plain body from a message payload"""
        if payload.get('mimeType') == 'text/plain':
            data = payload.get('body', {}).get('data', '')
            if data:
                return base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')

        for part in payload.get('parts', []):
            result = self._extract_body(part)
            if result:
                return result

        return ''

    def _contains_reply_keywords(self, text):
        """Return True if the text contains job-reply keywords"""
        keywords = [
            'response', 'interview', 'interested', 'thank',
            'offer', 'next step', 'schedule', 'call'
        ]
        return any(kw in text for kw in keywords)

    # -----------------------------------------------------------------------
    # Label monitoring
    # -----------------------------------------------------------------------

    def _get_label_id(self, label_name):
        """
        Return the Gmail label ID for a given label name, or None.

        Matches the full Gmail label path (e.g. 'JobHunt/Rejected') so that
        sub-labels nested inside a parent folder are found correctly.
        """
        try:
            results = self.service.users().labels().list(userId='me').execute()
            for label in results.get('labels', []):
                if label['name'].lower() == label_name.lower():
                    return label['id']
        except Exception as e:
            print(f"[Gmail] Could not look up label '{label_name}': {e}")
        return None

    def get_label_emails(self, label_name, max_results=50):
        """
        Fetch emails from a specific Gmail label.

        Returns a list of parsed email dicts, or an empty list if the label
        doesn't exist or the service isn't authenticated.
        """
        if not self.service:
            return []

        label_id = self._get_label_id(label_name)
        if not label_id:
            print(f"[Gmail] Label '{label_name}' not found – skipping.")
            return []

        try:
            results = self.service.users().messages().list(
                userId='me',
                labelIds=[label_id],
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])
            emails = []
            for msg in messages:
                parsed = self._parse_message(msg['id'])
                if parsed:
                    parsed['label'] = label_name  # tag so UI knows which label
                    emails.append(parsed)

            print(f"[Gmail] Label '{label_name}': {len(emails)} email(s).")
            return emails

        except HttpError as e:
            print(f"[Gmail] HTTP error fetching label '{label_name}': {e}")
            return []
        except Exception as e:
            print(f"[Gmail] Error fetching label '{label_name}': {e}")
            return []

    def get_monitored_label_data(self, monitored_labels):
        """
        Fetch email data for every label in monitored_labels.

        Labels are looked up as sub-labels of the configured GMAIL_FOLDER.
        For example, if GMAIL_FOLDER='JobHunt' and monitored_labels=['Rejected'],
        the Gmail API is queried for the label 'JobHunt/Rejected'.

        Returns a dict keyed by the short label name (no folder prefix):
            {
              'Rejected':  {'count': 5, 'emails': [...]},
              'Interview': {'count': 2, 'emails': [...]},
            }
        """
        parent_folder = self.config.get('GMAIL_FOLDER', 'JobHunt')
        data = {}
        for short_name in monitored_labels:
            # Build the full nested path that Gmail uses, e.g. 'JobHunt/Rejected'
            full_label_path = f"{parent_folder}/{short_name}"
            print(f"[Gmail] Looking up sub-label: '{full_label_path}'")
            emails = self.get_label_emails(full_label_path)
            # Store under the short display name so the template doesn't change
            data[short_name] = {
                'count': len(emails),
                'emails': emails,
                'full_path': full_label_path,
            }
        return data

