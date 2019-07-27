""" Config for Calendar """
import os


def make_folder(folder):
    """ Creates a folder if it does not exist """
    if not os.path.exists(folder):
        os.makedirs(folder)


class Config:
    """ Configuration for the Calendar CLI """

    def __init__(self, conf_path):
        self.conf_path = conf_path
        self.profiles_dir = self.conf_path + "profiles/"
        self.credentials_file = self.conf_path + "credentials.json"
        make_folder(conf_path)
        make_folder(self.profiles_dir)

    def list_profiles(self):
        """ List the profiles inside the config directory """
        return [path.split(".")[0] for path in os.listdir(self.profiles_dir)]

    def get_profile(self, profile):
        """ Gets the profile from the config """
        return self.profiles_dir + profile + ".json"

    def has_credentials_file(self):
        """ Checks if we have a credentials file """
        return os.path.isfile(self.credentials_file)

    def get_credentials_file(self):
        """ Gets the path of the credentials file """
        return self.credentials_file
