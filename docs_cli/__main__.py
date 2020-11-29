import click
import re
import sys
import os
import pickle
import os.path
import yaml
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/documents']


CONFIG_DIR = os.path.expanduser("~/.config/docs")
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
    return build('docs', 'v1', credentials=creds)


@click.group()
def cli():
    pass


def strip_element(element):
    return element["paragraph"]


@cli.command()
@click.argument('doc')
def cat(doc):
    desktop_file = doc + ".desktop"
    contents = open(desktop_file).read()

    id = re.search("document/d/([^/]+)/edit", contents).group(1)
    service = get_service()

    document = service.documents().get(documentId=id).execute()
    elements = document["body"]["content"]
    stripped_elements = [
        strip_element(element)
        for element in elements if 'paragraph' in element
    ]
    print(yaml.dump(stripped_elements))


def main():
    return cli()


if __name__ == "__main__":
    sys.exit(main())
