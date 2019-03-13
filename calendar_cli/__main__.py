"""
Google Calendar CLI
"""
from __future__ import print_function
import sys
import os
import argparse
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google_cli import make_google_parser, decorate_arguments
from httplib2 import Http
from oauth2client import file, client, tools
from . import Config, CalendarApi

SCOPES = 'https://www.googleapis.com/auth/calendar'


def selected_calendar_from_args(args):
    if args.select:
        return args.select
    else:
        return args.config.get_selected_calendar()


def build_service(creds):
    return build('calendar', 'v3', http=creds.authorize(Http()))


def print_events(_, response, error):
    events = response["items"]
    for event in events:
        if "summary" in event:
            print("{} - {}".format(event["id"], event["summary"]))


def print_event(event):
    start_time = event["start"]["dateTime"] if "dateTime" in event["start"] else event["start"]["date"]
    end_time = event["end"]["dateTime"] if "dateTime" in event["end"] else event["end"]["date"]
    location = event.get("location", "NA")
    description = event.get("description", "")
    print("{}\nFrom {} to {}\nLocation: {}\n{}".format(
        event["summary"], start_time, end_time, location, description))


def calendars_command(subparsers):
    """ lists available calendars """
    parser = subparsers.add_parser("calendars", help=calendars_command.__doc__)

    def run(args):
        service = build_service(args.profile)
        calendars = service.calendarList().list().execute()
        for calendar in calendars["items"]:
            print("{} - {}".format(calendar["id"], calendar["summary"]))

    parser.set_defaults(run=run)


def list_command(subparsers):
    """ Lists events on selected calendar """
    parser = subparsers.add_parser("list", help=list_command.__doc__)

    def run(args):
        service = build_service(args.profile)
        token = None
        needsLoop = True
        while needsLoop:
            events = service.events().list(
                calendarId=args.select,
                timeMin=datetime.utcnow().isoformat() + "Z",
                pageToken=token
            ).execute()
            print_events(None, events, None)
            if "nextPageToken" in events:
                token = events["nextPageToken"]
            else:
                token = None
                needsLoop = False
    parser.set_defaults(run=run)


def schedule_command(subparsers):
    """ Prints all events that are coming up """
    parser = subparsers.add_parser("schedule", help=schedule_command.__doc__)

    def run(args):
        service = build_service(args.profile)
        calendars = service.calendarList().list().execute()
        batch = service.new_batch_http_request()
        for calendar in calendars["items"]:
            batch.add(service.events().list(calendarId=calendar["id"], timeMin=datetime.utcnow().isoformat(
            ) + "Z", timeMax=(datetime.now() + timedelta(days=5)).isoformat() + "Z"), callback=print_events)
        batch.execute()
    parser.set_defaults(run=run)


def print_command(subparsers):
    """ Prints details for an event """
    parser = subparsers.add_parser("print", help=print_command.__doc__)
    parser.add_argument("event", help="The id of the event you want to detail")

    def run(args):
        service = build_service(args.profile)
        calendar_id = args.select
        event_id = args.event
        event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
        print_event(event)

    parser.set_defaults(run=run)


def edit_command(subparsers):
    """ Edits an event """
    parser = subparsers.add_parser("edit", help=edit_command.__doc__)
    parser.add_argument("event", help="The id of the event you want to edit")
    parser.add_argument(
        "-l",
        "--location",
        help="Changes the location of the event"
    )

    def run(args):
        service = build_service(args.profile)
        calendar_id = args.select
        event_id = args.event
        patches = {}
        if args.location:
            patches["location"] = args.location
        service.events().patch(calendarId=calendar_id,
                               eventId=event_id, body=patches).execute()

    parser.set_defaults(run=run)


def new_command(subparsers):
    """ Creates a new event """
    parser = subparsers.add_parser("new", help=new_command.__doc__)
    parser.add_argument(
        "specification",
        help="Specification of the event in plain text"
    )

    def run(args):
        service = build_service(args.profile)
        calendar_id = args.select
        quick_add = args.specification
        service.events().quickAdd(calendarId=calendar_id, text=quick_add).execute()

    parser.set_defaults(run=run)


def select_command(subparsers):
    """ Selects a calendar """
    parser = subparsers.add_parser("select", help=select_command.__doc__)
    parser.add_argument(
        "selected",
        help="Selects a calendar for future commands"
    )

    def run(args):
        args.config.set_selected_calendar(args.selected)
    parser.set_defaults(run=run)


def create_parser():
    """ Creates the main parser """
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="subcommands help")
    make_google_parser(parser, subparsers)

    parser.add_argument(
        "-s", "--select", help="Select a calendar to apply to")

    calendars_command(subparsers)
    list_command(subparsers)
    schedule_command(subparsers)
    print_command(subparsers)
    edit_command(subparsers)
    new_command(subparsers)
    select_command(subparsers)
    return parser


def calendar_decorate_args(args):
    """ Decorates the arguments object with richer objects """

    if not args.config:
        args.config = os.path.expanduser("~/.config/calendar/")
    args = decorate_arguments(args, Config)
    args.select = selected_calendar_from_args(args)
    return args


def main():
    """ Main Module """
    parser = create_parser()
    args = parser.parse_args()
    args = calendar_decorate_args(args)
    args.select = selected_calendar_from_args(args)

    if not args.config.has_credentials_file():
        print("Please put your credentials.json at {}".format(
            args.config.get_credentials_file()))
        return 1
    return args.run(args)


if __name__ == '__main__':
    sys.exit(main())
