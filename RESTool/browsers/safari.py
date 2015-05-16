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
from time import strftime

from logbook import FileHandler, Logger

from browser import Browser

if os.path.exists("application.log"):
    log_handler = FileHandler('application.log')
    log_handler.push_application()
log = Logger("Safari")


class Safari(Browser):
    def __init__(self):
        log.debug("Starting initialization")
        self.name = "safari"
        self.os = platform.system().lower()

        self.path = None
        self.path = self._find_res()
        self.res_exists = self.path is not None

    def _find_res(self):
        log.debug("searching for RES")

        if self.os == "darwin":
            res_folder = self._expand("~/Library/Safari/LocalStorage/")
        else:
            log.error("Unsupported OS. Returning None")
            return None

        log.debug("res_folder set to : {}".format(res_folder))

        if not os.path.exists(res_folder):
            log.error("Selected res folder does not exist")
            return None

        log.info("Searching for RES file in res_folder directory")

        name_start = "safari-extension_com.honestbleeps.redditenhancementsuite-"
        all_files = os.listdir(res_folder)

        try:
            res_file = [i for i in all_files if i.startswith(name_start)][0]
            log.info("RES file found as {}".format(res_file))
        except IndexError:
            log.error("RES file not found in file list")
            return

        try:
            full_path = os.path.join(res_folder, res_file)
            log.debug("Full safari path set to {}".format(full_path))

            if os.path.exists(full_path):
                log.debug("Full safari path exists")
                return full_path
            else:
                log.warn("Full safari path does not exist. RES Not installed?")
                return None

        except AttributeError:
            log.error("Joining failed for {} and {}".format(res_folder, res_file))
            return None
        except Exception as e:
            log.exception(e)

    def get_data(self, chrome_path=None):
        log.debug("Safari get data")

        if not chrome_path:
            chrome_path = self.path

        if chrome_path is None:
            log.error("Safari path invalid")
            return None

        log.debug("Safari path set to: {}".format(chrome_path))

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
        except Exception as e:
            log.exception(e)

    def set_data(self, json_data):
        log.info("Safari setting data")
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
        except Exception as e:
            log.error("Exception when converting json data to chrome")
            log.exception(e)

    def backup(self):
        if self.path:
            fname = "safari.{}.backup".format(strftime("%Y-%m-%d"))
            try:
                return self._backup_file(self.path, fname)
            except Exception as e:
                log.exception(e)

        else:
            return False

    def restore_from_self(self, backup_path):
        log.info("Safari restore from self")

        if not self.res_exists or not backup_path:
            return False

        try:
            shutil.copy(backup_path, self.path)
            return True
        except Exception as e:
            log.exception(e)
