import click
import sys
import os
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://mail.google.com/']


CONFIG_DIR = os.path.expanduser("~/.config/gmail")
if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)


def get_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    token_file = CONFIG_DIR + "/token.pickle"
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CONFIG_DIR + '/credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)


@click.group()
def cli():
    pass


@cli.command()
@click.option('--unread', '-u', is_flag=True)
def list(unread):
    service = get_service()

    batch = service.new_batch_http_request()

    def print_email(_, response, __):
        for message in response['messages']:
            subject = [header for header in message['payload']
                       ['headers'] if header['name'] == 'Subject']
            print(subject[0]['value'])

    for thread in service.users().threads().list(userId='me', q='is:unread' if unread else '').execute().get('threads', []):
        tdata = service.users().threads().get(userId='me', id=thread['id'])
        batch.add(tdata, callback=print_email)
    batch.execute()


def main():
    return cli()


if __name__ == "__main__":
    sys.exit(main())
