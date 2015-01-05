#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Firefox(object):
    def __init__(self):
        log.info("Firefox initialization starting")
        self.os = platform.system().lower()
        self.path = None
        self.profile = None
        self.available_profiles = {}

        self.available_profiles = self._get_profiles()
        self.path = self._find_res()

        self.res_exists = self.path is not None

    def _expand(self, path):
        log.debug("Chrome expanding: {}".format(path))

        if self.os == "linux":
            return os.path.expanduser(path)
        elif self.os == "windows" and platform.release() != "XP":
            return os.path.expandvars(path)
        else:
            log.error("Unsupported OS: {} - expanding failed.".format(self.os))
            return None

    def _find_res(self):
        log.info("Firefox finding RES")

        if not self.available_profiles:
            log.debug("Profiles not found in _find_res, aborting")
            return None

        for profile_name in self.available_profiles.keys():
            res = self._get_res(profile_name)

            if res and res is not None:
                self.profile = profile_name
                return res

        return None

    def _get_profiles(self):
        log.info("Getting firefox profiles")

        if self.os == 'linux':
            profiles_folder = self._expand("~/.mozilla/firefox/")

        elif self.os == 'windows':
            if platform.release() == "XP":
                log.error("Unsupported OS (Windows XP). Returning None")
                return None

            profiles_folder = self._expand("%APPDATA%\\Mozilla\\Firefox\\")

        else:
            log.error("Unsupported OS. Returning None")
            return None

        log.debug("Firefox profiles root folder set to {}".format(profiles_folder))

        if not os.path.exists(profiles_folder):
            log.error("profiles_folder does not exists, returning {}")
            return {}

        try:
            profiles_path = os.path.join(profiles_folder, "profiles.ini")
            log.debug("profiles.ini path: {}".format(profiles_path))
        except AttributeError:
            log.error("Joining folder and profiles.ini failed. Returning None")
            return {}
        except:
            log.error("Unhandeled exception")
            if DEBUG:
                raise
            else:
                return {}

        if not os.path.exists(profiles_path):
            # If profiles.ini does not exist no profile folder exists either
            # or does it...
            log.error("Profiles path not found. New FF installation?. Returning None")
            return {}

        profiles = ConfigParser.RawConfigParser()
        profiles.read(profiles_path)
        profiles.remove_section('General')

        available_profiles = {}
        for index, profile in enumerate(profiles.sections()):
            name = profiles.get(profiles.sections()[index], 'Name')
            path = profiles.get(profiles.sections()[index], 'Path')
            available_profiles[name] = path

        return available_profiles

    def _get_res(self, profile_name):
        log.debug("Getting firefox path for profile name: {}".format(profile_name))

        ff_profile = self.available_profiles.get(profile_name)
        res_file = "jetpack/jid1-xUfzOsOFlzSOXg@jetpack/simple-storage/store.json"

        if not ff_profile:
            log.error("Could not get selected profile path for {}".format(profile_name))
            return None

        if self.os == 'linux':
            res_folder = self._expand("~/.mozilla/firefox/")

        elif self.os == 'windows':
            if platform.release() == "XP":
                log.error("Unsupported OS (Windows XP). Returning None")
                return None

            res_folder = self._expand("%APPDATA%\\Mozilla\\Firefox\\")

        else:
            log.error("Unsupported OS: {} Returning None".format(self.os))
            return None

        log.debug("Firefox res_folder set to: {}".format(res_folder))

        try:
            full_path = os.path.join(res_folder, ff_profile, res_file)
            log.debug("Full firefox path set to {}".format(full_path))

            if os.path.exists(full_path):
                log.debug("Full firefox path exists")
                return full_path
            else:
                log.warn("Full firefox path does not exist. RES Not installed?")
                return None

        except AttributeError:
            log.warn("Firefox joining failed for {}, {} and {}".format(res_folder, ff_profile, res_file))
            return None

        except:
            log.error("Unhandeled exception")
            if DEBUG:
                raise
            else:
                return None


    def _backup_file(self, path, fname):
        log.debug("Chrome _backup_file with path={} fname={}".format(path, fname))
        if not os.path.exists(path):
            log.eror("Path not found {}".format(path))
            return False

        if not os.path.exists("res_backups"):
            try:
                os.makedirs("res_backups")
            except IOError:
                log.error("IOError encountered while trying to create res_backups folder. Aborting.")
                return False
            except:
                log.error("Unahandeled exception occurred while trying to create res_bacups folder.")
                if DEBUG:
                    raise
                else:
                    pass

        destination = os.path.join("res_backups", fname)
        log.debug("Source and destination exist. Trying to copy {} to {}".format(path, destination))
        try:
            shutil.copy(path, destination)
            # TODO: self.update_backup_list()
            return True
        except IOError:
            log.error("Copy failed due to IOError")
            return False
        except:
            log.error("Unhandeled exception occured")
            if DEBUG:
                raise
            else:
                return False

    def change_profile(self, profile_name):
        log.info("Firefox changing profile to {}".format(profile_name))

        if profile_name not in self.available_profiles.keys():
            log.debug("selected profile not in available profiles")
            return False

        self.path = self._get_res(profile_name)

    def get_data(self, firefox_path=None):
        log.debug("Firefox get data")

        if not firefox_path:
            firefox_path = self.path

        if firefox_path is None:
            log.error("Firefox path invalid")
            return None

        log.debug("Firefox path set to: {}".format(firefox_path))

        if not os.path.exists(firefox_path):
            log.debug("firefox_path refers to an invalid location")
            return None

        try:
            log.debug("Opening firefox_path file with 'r' flag, utf-8 mode")
            with codecs.open(firefox_path, "r", "utf-8") as firefox_in:
                log.debug("json.load firefox file")
                ff_json = json.load(firefox_in)

            if not ff_json:
                log.debug("Loading json data from firefox path returned no data. Aborting")
                return None
            else:
                log.debug("ff_json contains some data")
                return ff_json
        except:
            log.debug("Unhandeled exception occured")
            if DEBUG:
                raise
            else:
                pass

    def set_data(self, json_data):
        log.info("Firefox setting data")
        if not json_data:
            log.debug("json_data empty, aborting.")
            # todo: verify json_data is valid RES data
            return False

        try:
            with codecs.open(self.path, 'w', 'utf-8') as firefox_out:
                log.debug("Writing dump to firefox file")
                firefox_out.write(json_data)
            return True
        except:
            log.error("Unhandeled exception")
            if DEBUG:
                raise
            else:
                return False

    def backup(self):
        if self.path:
            fname = "firefox.{}.backup".format(strftime("%Y-%m-%d"))
            try:
                return self._backup_file(self.path, fname)
            except:
                if DEBUG:
                    raise
                else:
                    return False
        else:
            return False

    def restore_from_self(self, backup_path):
        log.info("Firefox restore from self")

        if not self.res_exists or not backup_path:
            return False

        try:
            shutil.copy(backup_path, self.path)
            return True
        except:
            if DEBUG:
                raise
            else:
                return False
