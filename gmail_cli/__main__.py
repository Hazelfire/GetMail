import click
import sys
import os
import pickle
import yaml
import os.path
import base64
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


def print_subject(message):
    subject = [header for header in message['payload']
               ['headers'] if header['name'] == 'Subject']
    click.echo("{} - {}".format(message['id'], subject[0]['value']))


@cli.command()
@click.option('--unread', '-u', is_flag=True)
def list(unread):
    service = get_service()

    batch = service.new_batch_http_request()

    def print_email(_, response, __):
        for message in message["messages"]:
            print_subject(message)

    for thread in service.users().threads().list(userId='me', q='is:unread' if unread else '').execute().get('threads', []):
        tdata = service.users().threads().get(userId='me', id=thread['id'])
        batch.add(tdata, callback=print_email)
    batch.execute()


@cli.command()
@click.argument('id')
def cat(id):
    service = get_service()
    mdata = service.users().messages().get(userId='me', id=id).execute()
    print(yaml.dump(mdata["payload"]["headers"]))
    # print((mdata["payload"]["body"]["data"]))


@cli.command()
@click.argument('query')
def search(query):
    service = get_service()

    batch = service.new_batch_http_request()

    def print_email(_, response, __):
        print_subject(response)

    messages = service.users().messages().list(userId='me', q=query).execute()
    for message in messages["messages"]:
        mdata = service.users().messages().get(userId='me', id=message['id'])
        batch.add(mdata, callback=print_email)

    batch.execute()


def main():
    return cli()


if __name__ == "__main__":
    sys.exit(main())
