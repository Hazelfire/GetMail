import os
from . import Config


def get_default_profile():
    conf = Config(os.path.expanduser("~/.config/calendar/"))
    profiles = conf.list_profiles()
    if len(profiles) > 0:
        return conf.get_profile(conf.list_profiles()[0])
    else:
        return None


def get_default_selected_calendar():
    conf = Config(os.path.expanduser("~/.config/calendar/"))
    return conf.get_selected_calendar()
