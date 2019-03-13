from __future__ import print_function
import google_cli
import click
import pickle
import os.path
import argparse
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from oauth2client import file, client, tools
from . import SheetsApi
import sys

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Config Directory
config_dir = os.path.expanduser("~/.config/sheets/")
profiles_dir = config_dir + "profiles/"
credentials_file = config_dir + "credentials.json"

if not os.path.exists(config_dir):
    os.makedirs(config_dir)
    os.makedirs(profiles_dir)

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
SAMPLE_RANGE_NAME = 'Class Data!A2:E'

creds = None


def get_profiles():
    return [name.split(".")[0] for name in os.listdir(profiles_dir)]


def get_profile_path(name):
    return profiles_dir + name + ".json"


@click.option("--profile", help="The profile you want to run as")
@click.group()
def cli(profile):
    global creds
    profiles = get_profiles()
    if profiles:
        if not profile:
            profile = profiles[0]
        creds = file.Storage(get_profile_path(profile)).get()


@click.option("--name", help="Name of the profile you want to create")
@cli.command()
def new_profile(name):
    profile_file = profiles_dir + name + '.json'
    store = file.Storage(profile_file)
    if not os.path.isfile(profile_file):
        flow = client.flow_from_clientsecrets(credentials_file, SCOPES)
        parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            parents=[tools.argparser])
        creds = tools.run_flow(flow, store, flags=parser.parse_args([]))
    else:
        click.echo("profile exists")


@click.option("--sheet", help="Id of the sheet you want to detail")
@cli.command()
def describe(sheet):
    api = SheetsApi(creds)
    result = api.get_sheet(sheet)
    click.echo("{} ({})\nSheets:\n{}".format(
        result["properties"]["title"], sheet, "\n".join(
            [sheet["properties"]["title"] for sheet in result["sheets"]])))


if __name__ == "__main__":
    sys.exit(cli())


def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        print('Name, Major:')
        for row in values:
            # Print columns A and E, which correspond to indices 0 and 4.
            print('%s, %s' % (row[0], row[4]))
