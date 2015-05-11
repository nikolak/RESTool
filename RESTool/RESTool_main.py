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
import copy
from collections import OrderedDict

from browsers import Chrome, Firefox

try:
    from RESTool import restoolgui
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

class RESToolUI(QtGui.QMainWindow, restoolgui.Ui_MainWindow):

    # noinspection PyUnresolvedReferences
    def __init__(self, parent=None):
        super(RESToolUI, self).__init__(parent)
        self.setupUi(self)
        self.labelMessage.setVisible(False)

        self.choices_first = OrderedDict({"None":None})
        self.choices_second = OrderedDict({"None":None})
        self.profile_choices_first = OrderedDict({"None":None})
        self.profile_choices_second = OrderedDict({"None":None})

        self.first_browser = None
        self.second_browser = None
        self.first_br_profile = None
        self.second_br_profile = None

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

        self._set_available_browsers()
        self._set_available_profiles()
        self._update_backups_list()

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

    def _show_warning_label(self, msg):
        self.labelMessage.setText(msg)
        self.labelMessage.setVisible(True)

    def _set_available_browsers(self):
        chrome = Chrome()
        firefox = Firefox()


        if chrome.res_exists:
            self.choices_first['Chrome'] = chrome
            self.choices_second['Chrome'] = copy.copy(chrome)

        if firefox.res_exists:
            self.choices_first['Firefox'] = firefox
            self.choices_second['Firefox'] = copy.copy(firefox)

        for browser_name in self.choices_first:
            self.cboFirstBrowser.addItem(browser_name)
            self.cboSecondBrowser.addItem(browser_name)

        if not self.choices_first:
            self._warn("RES could not be found in Firefox or Chrome!")

    def _set_available_profiles(self):
        #TODO: Get real profiles and populate cbo

        for key in self.profile_choices_first:
            self.cboFirstBrowserProfile.addItem(key)

        for key in self.profile_choices_second:
            self.cboSecondBrowserProfile.addItem(key)

    def _first_browser_changed(self):
        self.first_browser = self.choices_first.get(str(self.cboFirstBrowser.currentText()))

        if not self.first_browser:
            self.first_br_profile = None
            self.cboFirstBrowserProfile.setCurrentIndex(0)
        self._update_ui_elements()

    def _first_browser_profile_changed(self):
        pass

    def _second_browser_changed(self):
        self.second_browser = self.choices_second.get(str(self.cboSecondBrowser.currentText()))

        if not self.second_browser:
            self.second_br_profile = None
            self.cboSecondBrowserProfile.setCurrentIndex(0)


        self._update_ui_elements()

    def _second_browser_profile_changed(self):
        pass

    def _update_ui_elements(self):

        if self.first_browser:
            self.FirstBrowserRESLabel.setText("Yes" if
                                              self.first_browser.res_exists
                                              else "No")
        else:
            self.FirstBrowserRESLabel.setText("N/A")

        if self.second_browser:
            self.SecondBrowserRESLabel.setText("Yes" if
                                               self.second_browser.res_exists
                                               else "No")
        else:
            self.SecondBrowserRESLabel.setText("N/A")

        if not self.first_browser and not self.second_browser:
            self.btnBackupFirst.setEnabled(False)
            self.btnBackupSecond.setEnabled(False)
            self.btnFirstToSecond.setEnabled(False)
            self.btnSecondToFirst.setEnabled(False)
            self.btnRestoreToFirst.setEnabled(False)
            self.btnRestoreToSecond.setEnabled(False)
            return

        if type(self.first_browser) == type(self.second_browser):
            if self.first_br_profile == self.second_br_profile:
                self._show_warning_label("Pick different browsers and/or profiles!")
                self.btnBackupFirst.setEnabled(False)
                self.btnBackupSecond.setEnabled(False)
                self.btnFirstToSecond.setEnabled(False)
                self.btnSecondToFirst.setEnabled(False)
                self.btnRestoreToFirst.setEnabled(False)
                self.btnRestoreToSecond.setEnabled(False)
                return

        if self.labelMessage.isVisible():
            self.labelMessage.setVisible(False)

        if self.first_browser and not self.second_browser:
            self.btnBackupFirst.setEnabled(True)
            self.btnRestoreToFirst.setEnabled(True)

            self.btnBackupSecond.setEnabled(False)
            self.btnRestoreToSecond.setEnabled(False)
            self.btnFirstToSecond.setEnabled(False)
            self.btnSecondToFirst.setEnabled(False)
            return

        if self.second_browser and not self.first_browser:
            self.btnBackupSecond.setEnabled(True)
            self.btnRestoreToSecond.setEnabled(True)

            self.btnBackupFirst.setEnabled(False)
            self.btnRestoreToFirst.setEnabled(False)
            self.btnFirstToSecond.setEnabled(False)
            self.btnSecondToFirst.setEnabled(False)
            return

        self.btnBackupFirst.setEnabled(True)
        self.btnBackupSecond.setEnabled(True)
        self.btnFirstToSecond.setEnabled(True)
        self.btnSecondToFirst.setEnabled(True)
        self.btnRestoreToFirst.setEnabled(True)
        self.btnRestoreToSecond.setEnabled(True)

    def _update_backups_list(self):
        self.listBackups.clear()
        if not os.path.exists("res_backups"):
            return
        backup_files = os.listdir("res_backups")
        for backup in backup_files:
            self.listBackups.addItem(backup)

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

def main():
    app = QtGui.QApplication(sys.argv)
    form = RESToolUI()
    form.show()
    app.exec_()


def cli():
    pass


if __name__ == '__main__':
    main()