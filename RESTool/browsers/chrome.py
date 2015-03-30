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
import logging
import os
import platform
import shutil
import sqlite3
from time import strftime

log = logging.getLogger()

DEBUG = True  # FIXME


class Chrome(object):
    def __init__(self):
        log.debug("Starting chrome initialization")
        self.os = platform.system().lower()

        self.path = None
        self.path = self._find_res()
        self.res_exists = self.path is not None
        pass

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
        log.debug("Finding Chrome RES")

        # res_folder = None
        res_file = "chrome-extension_kbmfpngjjgdllneeigpgjifpgocmfgmb_0.localstorage"

        if self.os == 'linux':
            res_folder = self._expand("~/.config/google-chrome/Default/Local Storage/")

        elif self.os == 'windows':
            if platform.release() == "XP":
                log.error("Unsupported OS (Windows XP). Returning None")
                return None

            # todo: Check if it's possible for folder to be in %APPDATA% instead
            res_folder = self._expand("%LOCALAPPDATA%\\Google\\Chrome\\User Data\\Default\\Local Storage\\")

        else:
            log.error("Unsupported OS. Returning None")
            return None

        log.debug("Chrome res_folder set to : {}".format(res_folder))

        if not os.path.exists(res_folder):
            log.error("Selected chrome folder does not exist")
            return None

        try:
            full_path = os.path.join(res_folder, res_file)
            log.debug("Full chrome path set to {}".format(full_path))

            if os.path.exists(full_path):
                log.debug("Full chrome path exists")
                return full_path
            else:
                log.warn("Full chrome path does not exist. RES Not installed?")
                return None

        except AttributeError:
            log.warn("Chrome joining failed for {} and {}".format(res_folder, res_file))
            return None
        except:
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
            except Exception as e:
                log.error("Exception occurred while trying to create res_bacups folder.")
                log.exception("Exception: {}".format(repr(e)))
                return False

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
            if DEBUG:
                raise
            else:
                return False

    def get_data(self, chrome_path=None):
        log.debug("Chrome get data")

        if not chrome_path:
            chrome_path = self.path

        if chrome_path is None:
            log.error("Chrome path invalid")
            return None

        log.debug("Chrome path set to: {}".format(chrome_path))

        if not os.path.exists(chrome_path):
            log.debug("chrome_path refers to an invalid location")
            return None

        try:
            log.debug("Connecting to database.")
            con = sqlite3.connect(chrome_path)
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

            log.info("Returning chrome data!")
            return chrome_data
        except:
            log.debug("Exception when converting data from chrome to firefox")
            if DEBUG:
                raise
            else:
                return None


    def set_data(self, json_data):
        log.info("Chrome setting data")
        if not json_data:
            log.debug("json_data empty, aborting.")
            # todo: verify json_data is valid RES data
            return False

        try:
            log.debug("Connecting to database...")
            conn = sqlite3.connect(self.path)
            c = conn.cursor()
            # todo fetchone to verify it's a valid RES database

            log.debug("Generating list of key, value tuples")
            ff_data = [(key, value) for key, value in json_data.items()]
            log.debug("Tuples generated. Count: {}".format(len(ff_data)))

            log.debug("Executing DROP TABLE")
            c.execute("DROP TABLE ItemTable;")

            log.debug("Dropping table done. Executing CREATE TABLE")
            c.execute("CREATE TABLE ItemTable (key TEXT, value TEXT);")

            log.debug("Creating table done. Inserting data from json_data into the database")
            c.executemany('INSERT OR IGNORE INTO ItemTable (key,value) VALUES(?,?)', ff_data)
            # fixme: 'OR IGNORE' needed?

            log.debug("Inserting data done. Committing changes")
            conn.commit()
            log.debug("Changes committed. Closing database")
            c.close()
            log.info("Setting chrome data complete!")
            return True
        except:
            log.debug("Exception when converting data from firefox to chrome")
            if DEBUG:
                raise
            else:
                return False

    def backup(self):
        if self.path:
            fname = "chrome.{}.backup".format(strftime("%Y-%m-%d"))
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
        log.info("Chrome restore from self")

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


if __name__ == '__main__':
    pass