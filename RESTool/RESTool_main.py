#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2014 Nikola Kovacevic <nikolak@outlook.com
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
__version__ = '0.1.0'

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


def exception_hook(type, value, tback):
    log.exception("".join(traceback.format_exception(type, value, tback)))
    sys.__excepthook__(type, value, tback)


sys.excepthook = exception_hook

# Link to donation page for RES project that this software uses
RES_DONATE_URL = "http://redditenhancementsuite.com/contribute.html"
# Links to valid paypal checkout pages for the amounts specified as keys
PAYPAL_PAYMENT_OPTIONS = {
    "$1.99": "https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=QL25GUJ62G6UL",
    "$4.99": "https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=3TSJ7LSD5F8LG",
    "$9.99": "https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=BXPXJB2QUDSY2"}


class RESToolUI(QtGui.QMainWindow, restoolgui.Ui_MainWindow):
    # noinspection PyUnresolvedReferences
    def __init__(self, parent=None):
        super(RESToolUI, self).__init__(parent)
        self.setupUi(self)

        self.os = platform.system().lower()
        log.info("Operating system detected: %s" % str(platform.uname()))

        self.chrome_path = self.get_chrome_path()
        self.firefox_path = None
        self.firefox_profiles = {}
        self.get_firefox_profiles()
        log.info("Chrome path set to: %s" % self.chrome_path)
        log.info("Firefox profiles available: {}".format(self.firefox_profiles))
        if len(self.firefox_profiles) < 2:
            log.info("Only one profile available, using it by default")
            self.firefox_path = self.get_firefox_path()

        log.info("Firefox path set to: %s" % self.firefox_path)
        self.lbl_os.setText("Not detected" if not self.os else self.os)

        self.lbl_version.setText(__version__)

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
        pass

    def _expand(self, path):
        log.debug("Expanding: %s" % path)
        if self.os == "linux":
            return os.path.expanduser(path)
        elif self.os == "windows":
            return os.path.expandvars(path)
        else:
            log.error("Unsupported OS. Expanding failed.")
            return None

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
                                  QtGui.QMessageBox.Cancel, QtGui.QMessageBox.No,
                                  QtGui.QMessageBox.Yes)

        if result == QtGui.QMessageBox.Cancel:
            return False
        elif result == QtGui.QMessageBox.No:
            return False
        elif result == QtGui.QMessageBox.Yes:
            return True
        else:
            log.debug("Returned unknown value from _prompt, %s" %result)
            return False

    # noinspection PyCallByClass,PyTypeChecker
    def _critical(self, msg, title="Error"):
        QtGui.QMessageBox.critical(self, title, msg, QtGui.QMessageBox.Ok)

    def update_ui(self):
        self.lbl_firefox.setText(str(bool(self.firefox_path)))
        self.lbl_chrome.setText(str(bool(self.chrome_path)))
        if not self.chrome_path or not self.firefox_path:
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

    def change_profile(self):
        self.firefox_path = self.get_firefox_path()

    def get_chrome_path(self):
        log.debug("Getting chrome path")
        folder = None
        res_file = "chrome-extension_kbmfpngjjgdllneeigpgjifpgocmfgmb_0.localstorage"

        if self.os == 'linux':
            folder = self._expand("~/.config/google-chrome/Default/Local Storage/")
        elif self.os == 'windows':
            if platform.release() == "XP":
                log.error("Unsupported OS (Windows XP). Returning None")
                return None
            # todo: Check if it's possible for folder to be in %APPDATA% instead
            folder = self._expand("%LOCALAPPDATA%\\Google\\Chrome\\User Data\\Default\\Local Storage\\")
        else:
            log.error("Unsupported OS. Returning None")
            return None
        try:
            log.debug("Chrome folder set to: %s" % folder)
            full_path = os.path.join(folder, res_file)
            log.debug("Full chrome path set to %s" % full_path)
            if os.path.exists(full_path):
                log.debug("Full chrome path exists")
                return full_path
            else:
                log.warn("Full chrome path does not exist. RES Not installed?")
                return None
        except AttributeError:
            log.warn("Chrome joining failed for '%s' and '%s'" % (folder, res_file))
            return None

    def get_firefox_profiles(self):
        log.debug("Gettin firefox profiles")

        profiles_folder = None

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
        log.debug("Firefox folder set to %s" % profiles_folder)
        try:
            profiles_path = os.path.join(profiles_folder, "profiles.ini")
            log.debug("profiles.ini path: %s" % profiles_path)
        except AttributeError:
            log.error("Joining folder and profiles.ini failed. Returning None")
            return None

        if not os.path.exists(profiles_path):
            # If profiles.ini does not exist no profile folder exists either
            log.error("Profiles path not found. New FF installation?. Returning None")
            return None

        profiles = ConfigParser.RawConfigParser()
        profiles.read(profiles_path)
        profiles.remove_section('General')

        for index, profile in enumerate(profiles.sections()):
            name = profiles.get(profiles.sections()[index], 'Name')
            path = profiles.get(profiles.sections()[index], 'Path')
            self.firefox_profiles[name] = path
            self.cbo_ff_profile.addItem(name)

    def get_firefox_path(self):
        log.debug("Gettin firefox path")

        folder = None
        profile = self.firefox_profiles.get(str(self.cbo_ff_profile.currentText()))
        res_file = "jetpack/jid1-xUfzOsOFlzSOXg@jetpack/simple-storage/store.json"

        if not profile:
            log.error("Could not get selected profile path for %s " % self.cbo_ff_profile.currentText())
            return None

        if self.os == 'linux':
            folder = self._expand("~/.mozilla/firefox/")
        elif self.os == 'windows':
            if platform.release() == "XP":
                log.error("Unsupported OS (Windows XP). Returning None")
                return None
            folder = self._expand("%APPDATA%\\Mozilla\\Firefox\\")
        else:
            log.error("Unsupported OS. Returning None")
            return None
        try:
            log.debug("Firefox folder set to: %s" % folder)
            full_path = os.path.join(folder, profile, res_file)
            log.debug("Full firefox path set to %s" % full_path)
            if os.path.exists(full_path):
                log.debug("Full firefox path exists")
                return full_path
            else:
                log.warn("Full firefox path does not exist. RES Not installed?")
                return None
        except AttributeError:
            log.warn("Chrome joining failed for '%s', %s and '%s'" % (folder, profile, res_file))
            return None


    def chrome_to_firefox(self, chrome_path=None, firefox_path=None):
        if not chrome_path:
            chrome_path = self.chrome_path
        if not firefox_path:
            firefox_path = self.firefox_path
        if chrome_path is None or firefox_path is None:
            log.error("Chrome or firefox path is invalid")
            log.debug("Firefox %s ; Chrome %s" % (firefox_path, chrome_path))
            return

        try:
            log.debug("Connecting database. %s" % chrome_path)
            con = sqlite3.connect(chrome_path)
            c = con.cursor()
            log.debug("Getting database data...")
            db = c.execute('SELECT key, CAST(value AS TEXT) FROM ItemTable').fetchall()
            log.debug("Opening firefox file...")
            with codecs.open(firefox_path, 'w', 'utf-8') as firefox_out:
                dump = json.dumps(dict(db))
                log.debug("Writing to firefox file...")
                firefox_out.write(dump)
        except:
            self._warn("Migrating settings failed!")
            if DEBUG:raise
            return

        self._info("Migrating settings from Chrome to Firefox complete!")
        log.info("Chrome to firefox done!")

    def firefox_to_chrome(self, chrome_path=None, firefox_path=None):
        if not chrome_path:
            chrome_path = self.chrome_path
        if not firefox_path:
            firefox_path = self.firefox_path
        if chrome_path is None or firefox_path is None:
            log.error("Chrome or firefox path is invalid")
            log.debug("Firefox %s ; Chrome %s" % (firefox_path, chrome_path))
            return

        try:
            log.debug("Connecting database...")
            conn = sqlite3.connect(chrome_path)
            c = conn.cursor()
            log.debug("Opening firefox file...")
            with codecs.open(firefox_path, "r", "utf-8") as firefox_in:
                log.debug("Getting database data...")
                ff_json = json.load(firefox_in)

            ff_data = [(key, value) for key, value in ff_json.items()]
            log.debug("ff data elements {}".format(len(ff_data)))
            log.debug("Dropping table...")
            c.execute("DROP TABLE IF EXISTS ItemTable;")
            log.debug("Creating table...")
            c.execute("CREATE TABLE ItemTable (key TEXT, value TEXT);")
            log.debug("Inserting new data...")
            c.executemany('INSERT OR IGNORE INTO ItemTable (key,value) VALUES(?,?)', ff_data)
            log.debug("Commiting changes...")
            conn.commit()
            c.close()
        except:
            self._warn("Migrating settings failed!")
            if DEBUG:raise
            return

        log.info("Firefox to chrome done!")
        self._info("Migrating settings from firefox to Chrome complete!")

    def backup_file(self, path, fname):
        if not os.path.exists(path):
            log.eror("Backup file %s not found" % path)
            return False

        if not os.path.exists("res_backups"):
            try:
                os.makedirs("res_backups")
            except IOError:
                log.error("Creating res_backups folder failed")
                return False

        destination = os.path.join("res_backups", fname)
        log.debug("Trying to copy %s to %s" % (path, destination))
        try:
            shutil.copy(path, destination)
            self.update_backup_list()
            return True
        except IOError:
            log.error("Copy failed due to IOError")
            return False

    def backup_chrome(self):
        if self.chrome_path:
            fname = "chrome.{}.backup".format(strftime("%Y-%m-%d"))
            if self.backup_file(self.chrome_path, fname):
                self._info("Chrome backup successfully created!")
            else:
                self._warn("Chrome backup failed!")

    def backup_firefox(self):
        if self.firefox_path:
            fname = "firefox.{}.backup".format(strftime("%Y-%m-%d"))
            if self.backup_file(self.firefox_path, fname):
                self._info("Firefox backup successfully created!")
            else:
                self._warn("Firefox backup failed!")

    def restore_chrome(self):
        log.debug("Restoring chrome")
        try:
            filename = str(self.list_backups.selectedItems()[0].text())
        except IndexError:
            self._warn("No backup selected from the list to restore.")
            log.error("No file selected to restore from")
            return

        full_path = os.path.join("res_backups", filename)
        if not os.path.exists(full_path):
            log.error("File not found at %s " % full_path)
            return
        browser = filename.split('.')[0]

        try:
            if browser == "firefox":
                self.firefox_to_chrome(firefox_path=full_path)
                self._info("Chrome restored from firefox backup")
            elif browser == "chrome":
                shutil.copy(full_path, self.chrome_path)
                self._info("Chrome restored from backup")
            else:
                self._warn("Restore aborted. Unknown backup format")
                log.error("Unknown browser: %s" % browser)
        except:
            self._warn("Restoring Chrome failed!")
            if DEBUG:raise

    def restore_firefox(self):
        log.debug("Restoring firefox")
        try:
            filename = str(self.list_backups.selectedItems()[0].text())
        except IndexError:
            self._warn("No backup selected from the list to restore.")
            log.error("No file selected to restore from")
            return

        full_path = os.path.join("res_backups", filename)
        if not os.path.exists(full_path):
            log.error("File not found at %s " % full_path)
            return
        browser = filename.split('.')[0]
        try:
            if browser == "chrome":
                self.chrome_to_firefox(chrome_path=full_path)
                self._info("Firefox restored from Chrome backup")
            elif browser == "firefox":
                shutil.copy(full_path, self.firefox_path)
                self._info("Firefox restored")
            else:
                self._warn("Restore aborted. Unknown backup format")
                log.error("Unknown browser: %s" % browser)
        except:
            self._warn("Restoring Firefox failed!")
            if DEBUG:raise

    def delete_backup_file(self):
        try:
            filename = str(self.list_backups.selectedItems()[0].text())
        except IndexError:
            log.debug("No file selected for deltion. IndexError")
            return
        full_path = os.path.join("res_backups", filename)
        log.debug("Trying to remove %s" % full_path)
        os.remove(full_path)
        self.update_backup_list()

    def update_backup_list(self):
        self.list_backups.clear()
        if os.path.exists("res_backups"):
            backup_files = [x for x in os.listdir("res_backups") if x.endswith("backup")]
            for backup_name in backup_files:
                self.list_backups.addItem(backup_name)


def main():
    app = QtGui.QApplication(sys.argv)
    form = RESToolUI()
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()