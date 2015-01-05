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

from browsers import Chrome, Firefox

try:
    from RESTool import restoolgui2
except ImportError:
    import restoolgui2

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

class RESToolUI(QtGui.QMainWindow, restoolgui2.Ui_MainWindow):

    # noinspection PyUnresolvedReferences
    def __init__(self, parent=None):
        super(RESToolUI, self).__init__(parent)
        self.setupUi(self)

        self.choices_first = None
        self.choices_second = None

        self.first_browser = None
        self.second_browser = None

        self.cboFirstBrowser.currentIndexChanged.connect(self._first_browser_changed)
        self.cboFirstBrowserProfile.currentIndexChanged.connect(self._first_browser_profile_changed)
        self.cboSecondBrowser.currentIndexChanged.connect(self._second_browser_changed)
        self.cboSecondBrowserProfile.currentIndexChanged.connect(self._second_browser_profile_changed)

        self.btnFirstToSecond.clicked.connect(self.migrate_first_to_second)
        self.btnSecondToFirst.clicked.connect(self.migrate_second_to_first)

        self.btnBackupFirst.clicked.connect(self.backup_first)
        self.btnBackupSecond.clicked.connect(self.backup_second)
        self.btnRestoreToFirst.clicked.connect(self.resotre_to_first)
        self.btnBackupSecond.clicked.connect(self.restore_to_second)

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

    def _get_available_browsers(self):
        pass

    def _populate_choices(self):
        pass

    def _first_browser_changed(self):
        pass

    def _first_browser_profile_changed(self):
        pass

    def _second_browser_changed(self):
        pass

    def _second_browser_profile_changed(self):
        pass

    def _update_main_buttons(self):
        pass

    def _update_backups_list(self):
        pass

    def migrate_first_to_second(self):
        pass

    def migrate_second_to_first(self):
        pass

    def backup_first(self):
        pass

    def backup_second(self):
        pass

    def resotre_to_first(self):
        pass

    def restore_to_second(self):
        pass


class RESToolUI_old(QtGui.QMainWindow, restoolgui.Ui_MainWindow):
    # noinspection PyUnresolvedReferences
    def __init__(self, parent=None):
        super(RESToolUI, self).__init__(parent)
        self.setupUi(self)

        self.lbl_os.setText("Not detected" if not platform.system() else platform.system())

        self.lbl_version.setText(__version__)
        self.chrome = Chrome()
        self.firefox = Firefox()

        if self.firefox.profile:
            self.cbo_ff_profile.addItem(self.firefox.profile)

        for profile in [p for p in self.firefox.available_profiles.keys() if p != self.firefox.profile]:
            self.cbo_ff_profile.addItem(profile)

        self.btn_ch_to_ff.clicked.connect(self.chrome_to_firefox)
        self.btn_ff_to_ch.clicked.connect(self.firefox_to_chrome)
        self.btn_backup_ch.clicked.connect(self.backup_chrome)
        self.btn_backup_ff.clicked.connect(self.backup_firefox)
        self.btn_restore_ch.clicked.connect(self.restore_chrome)
        self.btn_restore_ff.clicked.connect(self.restore_firefox)
        self.btn_del_backup.clicked.connect(self.delete_backup_file)

        self.cbo_ff_profile.currentIndexChanged.connect(self.change_profile)
        self.cbo_ff_profile.currentIndexChanged.connect(self.update_ui)

        self.btn_donate_res.clicked.connect(slot=lambda: webbrowser.open(RES_DONATE_URL))

        self.update_ui()
        self.update_backup_list()


    def update_ui(self):
        self.lbl_firefox.setText(str(self.firefox.res_exists))
        self.lbl_chrome.setText(str(self.chrome.res_exists))
        if not self.chrome.res_exists or not self.firefox.res_exists:
            self.btn_ch_to_ff.setEnabled(False)
            self.btn_ff_to_ch.setEnabled(False)

        if not self.chrome.res_exists:
            self.btn_backup_ch.setEnabled(False)
            self.btn_restore_ch.setEnabled(False)

        if not self.firefox.res_exists:
            self.btn_backup_ff.setEnabled(False)
            self.btn_restore_ff.setEnabled(False)
        else:  # to handle profile change
            self.btn_backup_ff.setEnabled(True)
            self.btn_restore_ff.setEnabled(True)

        if self.chrome.res_exists and self.firefox.res_exists:
            self.btn_ch_to_ff.setEnabled(True)
            self.btn_ff_to_ch.setEnabled(True)

    def chrome_to_firefox(self):
        if not self.chrome.res_exists or not self.firefox.res_exists:
            # fixme: can this even happen?
            return

        try:
            chrome_data = self.chrome.get_data()
            if not chrome_data:
                self._warn("Could not get Chrome data")
                return

            if self.firefox.set_data(chrome_data):
                self._info("Migrating settings from Chrome to Firefox done!")
            else:
                self._warn("Migrating settings from Chrome to Firefox failed!")
        except:
            if DEBUG:
                raise

            self._warn("Error occurred while migrating settings from Chrome to Firefox")


    def firefox_to_chrome(self):
        if not self.chrome.res_exists or not self.firefox.res_exists:
            # fixme: can this even happen?
            return

        try:
            firefox_data = self.firefox.get_data()
            if not firefox_data:
                self._warn("Could not get Firefox data")
                return

            if self.chrome.set_data(firefox_data):
                self._info("Migrating settings from Firefox to Chrome done!")
            else:
                self._warn("Migrating settings from Firefox to Chrome failed!")
        except:
            if DEBUG:
                raise

            self._warn("Error occurred while migrating settings from Chrome to Firefox")


    def backup_chrome(self):
        try:
            if self.chrome.backup():
                self._info("Backing up Chrome done!")
            else:
                self._warn("Backing up Chrome failed!")

            self.update_backup_list()
        except:
            if DEBUG:
                raise

            self._warn("Error occurred while backing up Chrome")

    def backup_firefox(self):
        try:
            if self.firefox.backup():
                self._info("Backing up Firefox done!")
            else:
                self._warn("Backing up Firefox failed!")
            self.update_backup_list()
        except:
            if DEBUG:
                raise

            self._warn("Error occurred while backing up Firefox")


    def restore_chrome(self):
        backup_fname = str(self.list_backups.selectedItems()[0].text())
        backup_path = os.path.join("res_backups", backup_fname)
        browser = backup_fname.split('.')[0]

        try:
            if browser == "firefox":
                data = self.firefox.get_data(backup_path)
            elif browser == "chrome":
                if self.chrome.restore_from_self(backup_path):
                    self._info("Chrome restored from backup")
                else:
                    self._warn("Restoring Chrome from backup failed")
                return
            else:
                self._warn("Invalid backup file name")
                return

            if not data:
                self._warn("Invalid backup data")
                return

            self.chrome.set_data(data)
        except:
            if DEBUG:
                raise

            self._warn("Error processing the selected file")
            return


    def restore_firefox(self):
        backup_fname = str(self.list_backups.selectedItems()[0].text())
        backup_path = os.path.join("res_backups", backup_fname)
        browser = backup_fname.split('.')[0]

        try:
            if browser == "firefox":
                if self.firefox.restore_from_self(backup_path):
                    self._info("Firefox restored from backup")
                else:
                    self._warn("Restoring Firefox from backup failed.")
                return
            elif browser == "chrome":
                data = self.chrome.get_data(backup_path)
            else:
                self._warn("Invalid backup file name")
                return

            if not data:
                self._warn("Invalid backup data")
                return

            self.chrome.set_data(data)
        except:
            if DEBUG:
                raise

            self._warn("Error processing the selected file")
            return


    def delete_backup_file(self):
        fname = str(self.list_backups.selectedItems()[0].text())
        try:
            os.remove(os.path.join("res_backups", fname))
        except:
            if DEBUG:
                raise

            self._warn("File removal failed")
        self.update_backup_list()
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


def main():
    app = QtGui.QApplication(sys.argv)
    form = RESToolUI()
    form.show()
    app.exec_()


def cli():
    pass


if __name__ == '__main__':
    main()