""" Command line utilities for google applications """
import argparse
from httplib2 import Http
from oauth2client import file, client, tools


def get_creds(profile, conf):
    """ Gets credentials for a particular profile """
    if profile:
        store = file.Storage(conf.get_profile(profile))
        return store.get()
    elif len(conf.list_profiles()) > 0:
        store = file.Storage(conf.get_profile(conf.list_profiles()[0]))
        return store.get()
    else:
        return None


def new_profile_action(args):
    profile_file = profiles_dir + args.name + '.json'
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


def decorate_arguments(args, config_class):
    args.config = config_class(args.config)
    args.profile = get_creds(args.profile, args.config)
    return args


def make_google_parser(parser, subparsers):
    parser.add_argument(
        "-p",
        "--profile",
        help="The profile that you want to use")

    parser.add_argument(
        "-C",
        "--config",
        help="The config directory")

    newprofile = subparsers.add_parser(
        "newprofile", help="Creates a new profile")
    newprofile.add_argument("name", help="The name of your new profile")

    newprofile.set_defaults(run=new_profile_action)
