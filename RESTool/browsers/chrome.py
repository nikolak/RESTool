#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2015 Nikola Kovacevic <nikolak@outlook.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os
import platform
import shutil
import sqlite3
from glob import glob

from logbook import FileHandler, Logger, CRITICAL

from browser import Browser

log = Logger("Chrome")
if os.path.exists("application.log"):
    log_handler = FileHandler('application.log')
    log_handler.push_application()
else:
    log.level = CRITICAL


class Chrome(Browser):
    def __init__(self):
        log.debug("Starting initialization")
        self.name = "chrome"
        self.os = platform.system().lower()

        self.path = None
        self.profile = None
        self.available_profiles = self._get_profiles()
        self.path = self._find_res()
        self.res_exists = self.path is not None

    def _get_profiles(self):
        if self.os == 'linux':
            profiles_folder = self._expand("~/.config/google-chrome")

        elif self.os == 'windows':
            if platform.release() == "XP":
                log.error("Unsupported OS (Windows XP). Returning None")
                return None

            # todo: Check if it's possible for folder to be in %APPDATA%
            # instead
            profiles_folder = self._expand("%LOCALAPPDATA%\\Google\\Chrome\\User Data\\")

        elif self.os == "darwin":
            profiles_folder = self._expand("~/Library/Application Support/Google/Chrome/")

        else:
            log.error("Unsupported OS. Returning None")
            return None

        available_profiles = {}
        # Check if default directory exists
        default_profile = os.path.join(profiles_folder, "Default")
        if os.path.exists(default_profile):
            available_profiles['Default'] = default_profile
            log.debug("Default profile exists")

        for other_profile in glob(profiles_folder+os.sep+"Profile *"):
            try:
                profile_name = other_profile.split(os.sep)[-1:][0]
            except Exception as e:
                log.exception(e)
            log.debug("Additional profile {} at {} exists".format(profile_name,
                                                                    other_profile))
            available_profiles[profile_name] = other_profile

        return available_profiles

    def _find_res(self):
        log.info("searching for RES")

        if not self.available_profiles:
            log.info("Profiles not found in _find_res, aborting")
            return None

        for profile_name in self.available_profiles.keys():
            res = self._get_res(profile_name)

            if res and res is not None:
                self.profile = profile_name
                return res

        return None

    def _get_res(self, profile_name):
        log.debug("searching for RES")

        res_file = "chrome-extension_kbmfpngjjgdllneeigpgjifpgocmfgmb_0.localstorage"

        if self.os == 'linux':
            res_folder = self._expand("~/.config/google-chrome/{}/Local Storage/".format(profile_name))

        elif self.os == 'windows':
            if platform.release() == "XP":
                log.error("Unsupported OS (Windows XP). Returning None")
                return None

            # todo: Check if it's possible for folder to be in %APPDATA% instead
            res_folder = self._expand("%LOCALAPPDATA%\\Google\\Chrome\\User Data\\{}\\Local Storage\\".format(profile_name))

        elif self.os == "darwin":
            res_folder = self._expand("~/Library/Application Support/Google/Chrome/{}/Local Storage/".format(profile_name))

        else:
            log.error("Unsupported OS. Returning None")
            return None

        log.debug("res_folder set to : {}".format(res_folder))

        if not os.path.exists(res_folder):
            log.error("Selected folder does not exist")
            return None

        try:
            full_path = os.path.join(res_folder, res_file)
            log.debug("Full path set to {}".format(full_path))

            if os.path.exists(full_path):
                log.debug("Full path exists")
                return full_path
            else:
                log.warn("Full path does not exist. RES Not installed?")
                return None

        except AttributeError:
            log.error("Joining failed for {} and {}".format(res_folder, res_file))
            return None
        except Exception as e:
            log.exception(e)

    def change_profile(self, profile_name):
        log.info("Chrome changing profile to {}".format(profile_name))

        if profile_name not in self.available_profiles.keys():
            log.debug("selected profile not in available profiles")
            return False

        self.path = self._get_res(profile_name)
        self.res_exists = self.path is not None

    def get_data(self, file_path=None):
        log.debug("get_data")

        if not file_path:
            file_path = self.path

        if file_path is None:
            log.error("path invalid")
            return None

        log.debug("path set to: {}".format(file_path))

        if not os.path.exists(file_path):
            log.debug("file_path refers to an invalid location")
            return None

        try:
            log.debug("Connecting to database.")
            con = sqlite3.connect(file_path)
            c = con.cursor()
            log.debug("Executing SELECT query")
            db = c.execute('SELECT key, CAST(value AS TEXT) FROM ItemTable').fetchall()
            # todo: do some data verifying
            if not db:
                log.debug("SELECT query returned no data. Aborting.")
                return None
            else:
                log.debug("SELECT query returned data.")

            log.debug("Creating dict dump")
            chrome_data = json.dumps(dict(db))

            log.info("Returning data!")
            return chrome_data
        except Exception as e:
            log.exception(e)

    def set_data(self, json_data):
        log.info("set_data")
        if not json_data:
            log.debug("json_data empty, aborting.")
            # todo: verify json_data is valid RES data
            return False

        try:
            json_data = json.loads(json_data)
            log.debug("Connecting to database...")
            conn = sqlite3.connect(self.path)
            c = conn.cursor()
            # todo fetchone to verify it's a valid RES database

            log.debug("Generating list of key, value tuples")
            res_data = [(key, value) for key, value in json_data.items()]
            log.debug("Tuples generated. Count: {}".format(len(res_data)))
            log.debug("Checking tuple types")

            if not self.is_valid_sqlite_data(res_data):
                log.critical("Aborting setting data.")
                return

            log.debug("Executing DROP TABLE")
            c.execute("DROP TABLE ItemTable;")

            log.debug("Dropping table done. Executing CREATE TABLE")
            c.execute("CREATE TABLE ItemTable (key TEXT, value TEXT);")

            log.debug("Creating table done. Inserting data from json_data into the database")
            c.executemany('INSERT OR IGNORE INTO ItemTable (key,value) VALUES(?,?)', res_data)
            # fixme: 'OR IGNORE' needed?

            log.debug("Inserting data done. Committing changes")
            conn.commit()
            log.debug("Changes committed. Closing database")
            c.close()
            log.info("Setting data complete!")
            return True
        except Exception as e:
            log.error("Exception when converting json data")
            log.exception(e)

    def restore_from_self(self, backup_path):
        log.info("Restore from self")

        if not self.res_exists or not backup_path:
            return False

        try:
            shutil.copy(backup_path, self.path)
            return True
        except Exception as e:
            log.exception(e)
