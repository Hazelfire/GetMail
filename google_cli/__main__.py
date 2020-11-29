""" Google CLI
A general aws-cli thing for google apis
"""
from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import sys
import json
import os
import argparse
import base64
import quopri
import subprocess
from binascii import a2b_qp, a2b_base64

SCOPES = 'https://www.googleapis.com/auth/calendar'
calendar_conf_dir = os.path.expanduser("~/.config/calendar/")
profiles_dir = gmail_conf_dir + "profiles/"
credentials_file = gmail_conf_dir + "credentials.json"


def make_folder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)


def argument_after(argv, flag):
    return argv[argv.index(flag) + 1]


def get_creds(args, profiles):
    profile = ""
    if "-p" in sys.argv:
        profile = argument_after(sys.argv, "-p") + ".json"
    else:
        if len(profiles) > 0:
            profile = profiles[0]
        else:
            return None
    store = file.Storage(profiles_dir + profile)
    return store.get()


def get_unread(creds):
    service = build('gmail', 'v1', http=creds.authorize(Http()))

    # Call the Gmail API
    results = service.users().messages().list(
        userId='me', maxResults=20, q='is:unread').execute()
    return results.get('messages', [])


def get_message(creds, message_id):
    service = build('gmail', 'v1', http=creds.authorize(Http()))
    return service.users().messages().get(userId='me', id=message_id, format='full').execute()


def print_parts(parts):
    for part in parts:
        if "parts" in part:
            print_parts(part["parts"])
        elif part["mimeType"] == "text/plain":
            decoded = base64.urlsafe_b64decode(part["body"]["data"])
            print(decoded.decode("utf-8"))


def print_summary(_, thread, __): lthough,
 subject = ""
  email_from = ""
   for header in thread["messages"][-1].get('payload')['headers']:
        if header['name'] == 'Subject':
            subject = header['value']
    mid = ""
    if "-m" in sys.argv:
        mid = thread["messages"][-1]['id']
    else:
        mid = thread["id"]
    if "-i" in sys.argv:
        print(mid)
    else:
        print("{} - {}".format(mid, subject))


def main():
    make_folder(gmail_conf_dir)
    make_folder(profiles_dir)
    profiles = os.listdir(profiles_dir)
    if not os.path.isfile(credentials_file):
        print("Please put your credentials.json at {}".format(credentials_file))
        return
    if "newprofile" == sys.argv[1]:
        profile_file = profiles_dir + sys.argv[2] + '.json'
        store = file.Storage(profile_file)
        if not os.path.isfile(profile_file):
            flow = client.flow_from_clientsecrets(credentials_file, SCOPES)
            parser = argparse.ArgumentParser(
                description=__doc__,
                formatter_class=argparse.RawDescriptionHelpFormatter,
                parents=[tools.argparser])
            creds = tools.run_flow(flow, store, flags=parser.parse_args([]))
        else:
            print("profile exists")
    elif "list" == sys.argv[1]:
        creds = get_creds(sys.argv, profiles)
        service = build('gmail', 'v1', http=creds.authorize(Http()))

        more_messages = True
        token = None
        while more_messages:
            threads = service.users().threads().list(userId='me', maxResults=20,
                                                     q='is:unread', pageToken=token).execute()
            batch = service.new_batch_http_request()
            for thread in threads.get("threads", []):
                batch.add(service.users().threads().get(
                    userId='me', id=thread["id"], format='full'), callback=print_summary)
            batch.execute()
            if 'nextPageToken' in threads:
                more_messages = True
                token = threads['nextPageToken']
            else:
                more_messages = False

    elif sys.argv[1] == "print":
        creds = get_creds(sys.argv, profiles)
        message_result = get_message(creds, sys.argv[2])
        subject = ""
        email_from = ""
        for header in message_result.get('payload')['headers']:
            if header['name'] == 'Subject':
                subject = header['value']
            if header['name'] == 'From':
                email_from = header['value']
        print("Subject: {}\nFrom: {}".format(subject, email_from))
        print_parts(message_result["payload"]["parts"])
    elif sys.argv[1] == "page":
        message_ids = sys.argv[2:]
        pager = os.environ["PAGER"] if "PAGER" in os.environ else "more"
        command = ["bash", "-c", pager + " -f " + " ".join(
            ["<(gmail print {})".format(message_id) for message_id in message_ids])]
        subprocess.run(command)
    elif sys.argv[1] == "read":
        thread_ids = sys.argv[2:]
        creds = get_creds(sys.argv, profiles)
        service = build('gmail', 'v1', http=creds.authorize(Http()))
        batch = service.new_batch_http_request()
        for tid in thread_ids:
            batch.add(service.users().threads().modify(
                userId='me', id=tid, body={"removeLabelIds": ["UNREAD"]}))
        batch.execute()


if __name__ == '__main__':
    main()
