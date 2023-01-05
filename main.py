import base64
import json
import os.path
from pathlib import Path
import subprocess

import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def search_messages(service, query, ):
    result = service.users().messages().list(userId='me',q=query).execute()
    messages = [ ]
    if 'messages' in result:
        messages.extend(result['messages'])
    while 'nextPageToken' in result:
        page_token = result['nextPageToken']
        result = service.users().messages().list(userId='me',q=query, pageToken=page_token).execute()
        if 'messages' in result:
            messages.extend(result['messages'])
    return messages

def create_service():
    creds = None
    if os.path.exists('config/token.json'):
        creds = Credentials.from_authorized_user_file('config/token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'config/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('config/token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('gmail', 'v1', credentials=creds)
    return service


if __name__ == '__main__':
    service = create_service()
    data = json.load(open('config/data.json'))

    after_str = data["after"]
    before_str = data["before"]
    after = int(pd.to_datetime(after_str).timestamp())
    before = int(pd.to_datetime(before_str).timestamp())
    ROOT = f"data/{before_str}_{after_str}"
    Path(ROOT).mkdir(exist_ok=True, parents=True)
    for label in data["target_labels"]:
        Path(ROOT + "/" + label["name"]).mkdir(exist_ok=True)

        messages= search_messages(service, f"in:inbox label:{label['name']} after:{after} before:{before}")
        print(f"Found {len(messages)} messages for label: {label['name']}")

        for ind, message in enumerate(messages):
            msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
            if label['type'] == "html":
                if 'data' in msg['payload']['parts'][0]['body'].keys():
                    body = msg['payload']['parts'][0]['body']['data']
                else:
                    body = msg['payload']['parts'][0]['parts'][0]['body']['data']
                b_res = base64.urlsafe_b64decode(body).decode()
                path = ROOT + "/" + label["name"] + "/" + pd.to_datetime(msg['internalDate'], unit='ms').strftime(
                    "%Y-%m-%d_%H-%M-%S") + ".txt"
                with open(path, 'w') as f:
                    f.write(b_res)
                p = subprocess.run(["lowriter", "--headless", "--convert-to", "pdf", path, "--outdir",  ROOT + "/" + label["name"]])
                os.remove(path)
            else:
                for part in msg["payload"]["parts"]:
                    if part["mimeType"] in ['application/pdf', 'application/octet-stream']:
                        att = service.users().messages().attachments().get(userId='me', messageId=msg["id"],id=part["body"]["attachmentId"]).execute()
                        data = att['data']
                        file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                        path = ROOT + "/" + label["name"] + "/" + pd.to_datetime(msg['internalDate'],unit='ms').strftime("%Y-%m-%d_%H-%M-%S") + ".pdf"

                        with open(path, 'wb') as f:
                            f.write(file_data)

