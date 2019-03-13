import os
from . import Config


def get_default_profile():
    conf = Config(os.path.expanduser("~/.config/calendar/"))
    return conf.get_profile(conf.list_profiles()[0])


def get_default_selected_calendar():
    conf = Config(os.path.expanduser("~/.config/calendar/"))
    return conf.get_selected_calendar()
