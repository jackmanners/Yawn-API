import time, re, os, base64, json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

class study_email:
    def __init__(self, base_email):
        self.base_email = base_email
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
        
    def extract_urls(self, text):
        urls = re.findall(r'(https?://\S+)', text)
        return urls
        
    def authenticate(self):
        creds_rpath = os.path.join(os.path.abspath('.'), 'gmail_credentials.json')
        flow = InstalledAppFlow.from_client_secrets_file(
            creds_rpath, self.SCOPES)
        creds = flow.run_local_server(port=0)

        return creds

    def get_most_recent_email_sent_to(self, recipient_email):

        credentials = self.authenticate()
        service = build('gmail', 'v1', credentials=credentials)
        
        max_attempts = 6
        attempt_interval = 5

        for attempt in range(max_attempts):
            query = f'to:{recipient_email}'
            response = service.users().messages().list(userId='me', q=query, maxResults=1).execute()
            messages = response.get('messages', [])

            if not messages:
                print(f'No emails found sent to {recipient_email}.')
                print(response)
            else:
                message_id = messages[0]['id']
                message = service.users().messages().get(userId='me', id=message_id, format='full').execute()
                message_payload = message['payload']

                if 'parts' in message_payload:
                    for part in message_payload['parts']:
                        if part['mimeType'] == 'text/html':
                            message_content = part['body']['data']
                            decoded_content = base64.urlsafe_b64decode(message_content).decode('utf-8')
                            urls = self.extract_urls(decoded_content)
                            return urls[0]

                if 'body' in message_payload:
                    content = message_payload['body']['data']
                    decoded_content = base64.urlsafe_b64decode(content).decode('utf-8')
                    urls = self.extract_urls(decoded_content)
                    filtered_urls = [url for url in urls if 'account.withings' in url]
                    
                    if filtered_urls: return filtered_urls[0]

            if attempt < max_attempts - 1:
                print(f'No matching email found. Waiting for {attempt_interval} seconds before checking again...')
                time.sleep(attempt_interval)

        print('No matching email found after the maximum number of attempts.')
        return None
    
    def get_email(self, recipient):
        time.sleep(10)
        auth_url = self.get_most_recent_email_sent_to(recipient)
        if auth_url: 
            return auth_url
        else: 
            print(f"Could not get authentication link for {recipient}")
            raise Exception