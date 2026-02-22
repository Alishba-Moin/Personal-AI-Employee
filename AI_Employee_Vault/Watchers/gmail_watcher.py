import os
import pickle
import base64
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime

from base_watcher import Watcher

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailWatcher(Watcher):
    def __init__(self, output_dir="../../Needs_Action", credentials_path='credentials.json', interval=60):
        super().__init__(interval)
        self.output_dir = output_dir
        self.credentials_path = credentials_path
        self.service = self._authenticate_gmail()
        os.makedirs(output_dir, exist_ok=True)

    def _authenticate_gmail(self):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        return build('gmail', 'v1', credentials=creds)

    def check_for_new_items(self):
        results = self.service.users().messages().list(userId='me', q='is:unread in:inbox category:primary').execute()
        messages = results.get('messages', [])

        if not messages:
            print("No new unread messages found.")
        else:
            print(f"Found {len(messages)} new unread messages.")
            for message in messages:
                msg = self.service.users().messages().get(userId='me', id=message['id'], format='full').execute()
                self._process_message(msg)
                self.service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()

    def _process_message(self, msg):
        headers = msg['payload']['headers']
        subject = next(header['value'] for header in headers if header['name'] == 'Subject')
        sender = next(header['value'] for header in headers if header['name'] == 'From')
        date_received = next(header['value'] for header in headers if header['name'] == 'Date')

        email_body = self._get_email_body(msg['payload'])

        filename_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_subject = "".join(c for c in subject if c.isalnum() or c in (' ', '_')).replace(' ', '_')
        output_filepath = os.path.join(self.output_dir, f"email_{filename_timestamp}_{filename_subject}.md")

        content = f"---\n"
        content += f"type: email\n"
        content += f"from: {sender}\n"
        content += f"date: {date_received}\n"
        content += f"subject: {subject}\n"
        content += f"---\n\n"
        content += f"# Email from {sender}\n\n"
        content += f"## Subject: {subject}\n\n"
        content += f"### Date: {date_received}\n\n"
        content += f"\n\n{email_body}"

        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Processed email '{subject}' from {sender} and saved to {output_filepath}")

    def _get_email_body(self, payload):
        body_data = ""
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    body_data = part['body'].get('data', '')
                    break
                elif part['mimeType'] == 'text/html':
                    # Optionally process HTML if plain text is not available or preferred
                    body_data = part['body'].get('data', '')
                    break
        elif 'body' in payload:
            body_data = payload['body'].get('data', '')

        if body_data:
            return base64.urlsafe_b64decode(body_data).decode('utf-8')
        return "No body content found."

if __name__ == "__main__":
    # The output directory is relative to the current working directory of gmail_watcher.py
    # If gmail_watcher.py is in AI_Employee_Vault/Watchers,
    # then ../../Needs_Action points to AI_Employee_Vault/Needs_Action
    watcher = GmailWatcher(output_dir="../../AI_Employee_Vault/Needs_Action")
    watcher.run()
