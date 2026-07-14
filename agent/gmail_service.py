import os
import base64
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def authenticate_gmail():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                raise FileNotFoundError("Missing credentials.json! Please download it from Google Cloud Console.")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
    return creds

def create_gmail_draft(target_email: str, subject: str, body: str):
    """Create and insert a draft email."""
    try:
        creds = authenticate_gmail()
        service = build('gmail', 'v1', credentials=creds)

        message = EmailMessage()
        message.set_content(body)
        message['To'] = target_email
        message['From'] = 'me'
        message['Subject'] = subject

        # Encode the message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'message': {'raw': encoded_message}}

        # Create Draft
        draft = service.users().drafts().create(userId="me", body=create_message).execute()
        return f"✅ Draft successfully created in your Gmail! (Draft ID: {draft['id']})"
        
    except Exception as error:
        return f"❌ An error occurred: {error}"

import re
def get_job_alerts():
    """Reads recent emails from LinkedIn or Indeed to extract job URLs."""
    try:
        creds = authenticate_gmail()
        service = build('gmail', 'v1', credentials=creds)
        
        # Search for emails from linkedin or indeed in the last 24h
        query = "(from:jobalerts-noreply@linkedin.com OR from:alert@indeed.com) newer_than:1d"
        results = service.users().messages().list(userId='me', q=query, maxResults=5).execute()
        messages = results.get('messages', [])
        
        urls = []
        for msg in messages:
            msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
            snippet = msg_data.get('snippet', '')
            found_urls = re.findall(r'(https?://[^\s]+)', snippet)
            urls.extend(found_urls)
            
        # Clean up and filter for actual job links
        job_urls = [url for url in urls if 'job' in url.lower() or 'view' in url.lower()]
        return job_urls
        
    except Exception as error:
        print(f"❌ Error reading Gmail alerts: {error}")
        print("💡 Hint: You might need to delete token.json and re-authenticate to grant read permissions.")
        return []