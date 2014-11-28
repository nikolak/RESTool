#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2014 Nikola Kovacevic <nikolak@outlook.com>
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

__author__ = 'Nikola Kovacevic'
__email__ = 'nikolak@outlook.com'
__version__ = '0.2.0dev'

import os
import ConfigParser
import json
import sqlite3
import codecs
import sys
from PyQt4 import QtGui
import webbrowser
import platform
import traceback
import logging
import shutil
from time import strftime

try:
    from RESTool import restoolgui
except ImportError:
    import restoolgui

DEBUG = os.path.exists("log.txt")

if not DEBUG:
    err = sys.stderr
    out = sys.stdout
    sys.stderr = out  # disable stderr so that py2exe doesn't show that popup message

log = logging.getLogger('RESToolGUI')

if DEBUG:
    log.setLevel(logging.DEBUG)
    fh = logging.FileHandler('log.txt')
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    log.addHandler(ch)
    log.addHandler(fh)


def exception_hook(e_type, e_value, e_tback):
    log.exception("".join(traceback.format_exception(e_type, e_value, e_tback)))
    sys.__excepthook__(e_type, e_value, e_tback)


sys.excepthook = exception_hook

# Link to donation page for RES project that this software uses
RES_DONATE_URL = "http://redditenhancementsuite.com/contribute.html"
# Links to valid paypal checkout pages for the amounts specified as keys
PAYPAL_PAYMENT_OPTIONS = {
    "$1.99": "https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=QL25GUJ62G6UL",
    "$4.99": "https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=3TSJ7LSD5F8LG",
    "$9.99": "https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=BXPXJB2QUDSY2"}


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


class RESToolUI(QtGui.QMainWindow, restoolgui.Ui_MainWindow):
    # noinspection PyUnresolvedReferences
    def __init__(self, parent=None):
        super(RESToolUI, self).__init__(parent)
        self.setupUi(self)

        self.lbl_os.setText("Not detected" if not platform.system() else platform.system())

        self.lbl_version.setText(__version__)
        self.res = RES()

        self.btn_ch_to_ff.clicked.connect(self.chrome_to_firefox)
        self.btn_ff_to_ch.clicked.connect(self.firefox_to_chrome)
        self.btn_backup_ch.clicked.connect(self.backup_chrome)
        self.btn_backup_ff.clicked.connect(self.backup_firefox)
        self.btn_restore_ch.clicked.connect(self.restore_chrome)
        self.btn_restore_ff.clicked.connect(self.restore_firefox)
        self.btn_del_backup.clicked.connect(self.delete_backup_file)

        self.cbo_ff_profile.currentIndexChanged.connect(self.change_profile)
        self.cbo_ff_profile.currentIndexChanged.connect(self.update_ui)

        self.btn_paypal_pay.clicked.connect(self.__paypal_checkout)
        self.btn_donate_res.clicked.connect(slot=lambda: webbrowser.open(RES_DONATE_URL))

        self.update_ui()
        self.update_backup_list()

    def __paypal_checkout(self):
        log.debug("Starting paypal checkout process")
        amount_picked = str(self.cb_paypal_option.currentText())
        log.debug("Amount picked: {}".format(amount_picked))
        checkout_page = PAYPAL_PAYMENT_OPTIONS.get(amount_picked)

        if checkout_page:
            log.debug("Got checkout page opening in browser...")
            webbrowser.open(checkout_page)
        else:
            log.error("Got empty checkout page... {}".format(checkout_page))

    # noinspection PyCallByClass,PyTypeChecker
    def _warn(self, msg, title="Warnning"):
        QtGui.QMessageBox.warning(self, title, msg,
                                  QtGui.QMessageBox.Ok)

    # noinspection PyCallByClass,PyTypeChecker
    def _info(self, msg, title="Info"):
        QtGui.QMessageBox.information(self, title, msg,
                                      QtGui.QMessageBox.Ok)

    # noinspection PyCallByClass,PyTypeChecker
    def _prompt(self, msg, title="Prompt"):
        result = QtGui.QMessageBox.question(self, title, msg,
                                            QtGui.QMessageBox.Cancel,
                                            QtGui.QMessageBox.No,
                                            QtGui.QMessageBox.Yes)

        if result == QtGui.QMessageBox.Cancel:
            return False
        elif result == QtGui.QMessageBox.No:
            return False
        elif result == QtGui.QMessageBox.Yes:
            return True
        else:
            log.debug("Returned unknown value from _prompt, %s" % result)
            return False

    # noinspection PyCallByClass,PyTypeChecker
    def _critical(self, msg, title="Error"):
        QtGui.QMessageBox.critical(self, title, msg, QtGui.QMessageBox.Ok)

    def update_ui(self):
        self.lbl_firefox.setText(str(bool(self.res.firefox_path)))
        self.lbl_chrome.setText(str(bool(self.res.chrome_path)))
        if not self.chrome_path or not self.res.firefox_path:
            self.btn_ch_to_ff.setEnabled(False)
            self.btn_ff_to_ch.setEnabled(False)

        if not self.chrome_path:
            self.btn_backup_ch.setEnabled(False)
            self.btn_restore_ch.setEnabled(False)

        if not self.firefox_path:
            self.btn_backup_ff.setEnabled(False)
            self.btn_restore_ff.setEnabled(False)
        else:  # to handle profile change
            self.btn_backup_ff.setEnabled(True)
            self.btn_restore_ff.setEnabled(True)

        if self.chrome_path and self.firefox_path:
            self.btn_ch_to_ff.setEnabled(True)
            self.btn_ff_to_ch.setEnabled(True)

    def chrome_to_firefox(self):
        pass

    def firefox_to_chrome(self):
        pass

    def backup_chrome(self):
        pass

    def backup_firefox(self):
        pass

    def restore_chrome(self):
        # self.list_backups.selectedItems()[0].text()
        pass

    def restore_firefox(self):
        # self.list_backups.selectedItems()[0].text()
        pass

    def delete_backup_file(self):
        # self.list_backups.selectedItems()[0].text()
        # self.update_backup_list()
        pass

    def change_profile(self):
        self.res.change_profile(str(self.cbo_ff_profile.currentText()))
        pass


    def update_backup_list(self):
        self.list_backups.clear()
        if os.path.exists("res_backups"):
            backup_files = [x for x in os.listdir("res_backups") if x.endswith("backup")]
            for backup_name in backup_files:
                self.list_backups.addItem(backup_name)


    def delete_backup_file(self, filename):
        full_path = os.path.join("res_backups", filename)
        log.debug("Trying to remove %s" % full_path)
        os.remove(full_path)


def main():
    app = QtGui.QApplication(sys.argv)
    form = RESToolUI()
    form.show()
    app.exec_()


def cli():
    pass


if __name__ == '__main__':
    main()