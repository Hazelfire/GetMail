from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import sys
import json

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'

users = ['Personal', 'Uni', 'RESA', 'TPC']
def main():
    for user in users:
        """Shows basic usage of the Gmail API.
        Lists the user's Gmail labels.
        """
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        store = file.Storage(user + '.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
            creds = tools.run_flow(flow, store)
        service = build('gmail', 'v1', http=creds.authorize(Http()))

        # Call the Gmail API
        results = service.users().messages().list(userId='me', maxResults=3, q='is:unread').execute()
        messages = results.get('messages', [])

        print()
        print(user)
        if not messages:
            print('No emails found.')
        else:
            for message in messages:
                message_result = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
                
                subject = ""
                email_from = ""
                for header in message_result.get('payload')['headers']:
                    if header['name'] == 'Subject':
                        subject = header['value']
                print(subject)

if __name__ == '__main__':
    main()


