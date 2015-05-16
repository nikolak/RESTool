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
import sys
from PyQt4 import QtGui
import copy
from collections import OrderedDict

from logbook import FileHandler, Logger

if os.path.exists("application.log"):
    log_handler = FileHandler('application.log')
    log_handler.push_application()
else:  # py2exe otherwise shows annoying popup if there's something in stderr
    err = sys.stderr
    out = sys.stdout
    sys.stderr = out

log = Logger("Main Qt")

from browsers import Chrome, Firefox, Safari, Chromium

try:
    from RESTool import restoolgui
except ImportError:
    import restoolgui


class RESToolUI(QtGui.QMainWindow, restoolgui.Ui_MainWindow):
    # noinspection PyUnresolvedReferences
    def __init__(self, parent=None):
        super(RESToolUI, self).__init__(parent)
        log.info("setting up")
        self.setupUi(self)
        self.labelMessage.setVisible(False)

        self.choices_first = OrderedDict({"None": None})
        self.choices_second = OrderedDict({"None": None})
        self.profile_choices_first = OrderedDict({"None": None})
        self.profile_choices_second = OrderedDict({"None": None})

        self.first_browser = None
        self.second_browser = None
        self.first_br_profile = None
        self.second_br_profile = None

        self.all_browsers = {"firefox": Firefox,
                             "chrome": Chrome,
                             "safari": Safari}

        self.cboFirstBrowser.currentIndexChanged.connect(self._first_browser_changed)
        self.cboFirstBrowserProfile.currentIndexChanged.connect(self._first_browser_profile_changed)
        self.cboSecondBrowser.currentIndexChanged.connect(self._second_browser_changed)
        self.cboSecondBrowserProfile.currentIndexChanged.connect(self._second_browser_profile_changed)

        self.btnFirstToSecond.clicked.connect(self.migrate_first_to_second)
        self.btnSecondToFirst.clicked.connect(self.migrate_second_to_first)

        self.btnBackupFirst.clicked.connect(self.backup_first)
        self.btnBackupSecond.clicked.connect(self.backup_second)
        self.btnRestoreToFirst.clicked.connect(self.restore_to_first)
        self.btnRestoreToSecond.clicked.connect(self.restore_to_second)

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
        safari = Safari()
        chromium = Chromium()

        if chrome.res_exists:
            self.choices_first['Chrome'] = chrome
            self.choices_second['Chrome'] = copy.copy(chrome)

        if firefox.res_exists:
            self.choices_first['Firefox'] = firefox
            self.choices_second['Firefox'] = copy.copy(firefox)

        if safari.res_exists:
            self.choices_first['Safari'] = safari
            self.choices_second['Safari'] = copy.copy(safari)

        if chromium.res_exists:
            self.choices_first['Chromium'] = chromium
            self.choices_second['Chromium'] = copy.copy(chromium)

        for browser_name in self.choices_first:
            self.cboFirstBrowser.addItem(browser_name)
            self.cboSecondBrowser.addItem(browser_name)

        log.info("Available choices first {}".format(self.choices_first))

        if not self.choices_first:
            self._warn("RES could not be found in neither Firefox nor Chrome!")

    def _set_available_profiles(self):
        first = self.choices_first.get(str(self.cboFirstBrowser.currentText()))
        second = self.choices_first.get(str(self.cboSecondBrowser.currentText()))
        self.cboFirstBrowserProfile.clear()
        self.cboSecondBrowserProfile.clear()

        if first:
            try:
                for key in first.available_profiles:
                    self.cboFirstBrowserProfile.addItem(key)
            except AttributeError:
                self.cboFirstBrowserProfile.addItem("None")
        else:
            self.cboFirstBrowserProfile.addItem("None")

        if second:
            try:
                for key in second.available_profiles:
                    self.cboSecondBrowserProfile.addItem(key)
            except AttributeError:
                self.cboSecondBrowserProfile.addItem("None")
        else:
            self.cboSecondBrowserProfile.addItem("None")

    def _first_browser_changed(self):
        self.first_browser = self.choices_first.get(str(self.cboFirstBrowser.currentText()))

        if not self.first_browser:
            self.first_br_profile = None
            self.cboFirstBrowserProfile.setCurrentIndex(0)
        self._set_available_profiles()
        self._update_ui_elements()

    def _first_browser_profile_changed(self):
        pass

    def _second_browser_changed(self):
        self.second_browser = self.choices_second.get(str(self.cboSecondBrowser.currentText()))

        if not self.second_browser:
            self.second_br_profile = None
            self.cboSecondBrowserProfile.setCurrentIndex(0)
        self._set_available_profiles()
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

    def __migrate(self, from_browser, to_browser):
        from_name = from_browser.name
        to_name = to_browser.name
        log.info("Migrating '{}' to '{}'".format(from_name, to_name))

        if from_name == to_name:
            if to_browser.restore_from_self(from_browser.path):
                log.info("Migration done - restore_from_self returned True")
                self._info("Migrating from {} to {} complete!".format(from_name, to_name))
            else:
                log.info("Migration failed - restore_from_self not True")
                self._warn("Migrating data from {} to {} failed.".format(from_name, to_name))
        else:
            migration_data = from_browser.get_data()
            if not migration_data:
                log.warn("Did not get any data from first browser type {}".format(migration_data))
                self._warn("Migrating data from {} to {} failed.".format(from_name, to_name))
                return

            if to_browser.set_data(migration_data):
                log.info("Migration with set_data done successfully")
                self._info("Migrating from {} to {} complete!".format(from_name, to_name))
            else:
                log.info("Migrating data with set_data failed.")
                self._warn("Migrating data from {} to {} failed.".format(from_name, to_name))

    def migrate_first_to_second(self):
        self.__migrate(self.first_browser, self.second_browser)

    def migrate_second_to_first(self):
        self.__migrate(self.second_browser, self.first_browser)

    def __backup(self, browser):
        log.info("Backing up {}".format(browser.name))

        if not browser:
            return

        if browser.backup():
            self._update_backups_list()
        else:
            self._warn("Backing up failed.")

    def backup_first(self):
        self.__backup(self.first_browser)

    def backup_second(self):
        self.__backup(self.second_browser)

    def __restore(self, browser):
        log.info("Restoring backup to {}".format(browser))
        try:
            selected_backup = str(self.listBackups.selectedItems()[0].text())
        except IndexError:
            self._warn("No backup file selected.")
            return

        restore_format = browser.name
        backup_browser = selected_backup.split('.')[0]
        backup_path = os.path.join("res_backups", selected_backup)
        log.debug("Selected backup:{}".format(selected_backup))
        log.debug("Restore format")

        if backup_browser == restore_format:
            if not browser.restore_from_self(backup_path):
                self._warn("Restoring from same browser backup format failed.")
        elif backup_browser in self.all_browsers.keys():
            try:
                restore_data = self.all_browsers[backup_browser]().get_data(backup_path)
                if not restore_data:
                    self._warn("Restoring failed due to internal exception.")
                    return
            except Exception as e:
                log.exception(e)
                self._warn("Restoring failed due to internal exception.")
                return

            if not browser.set_data(restore_data):
                self._warn("Restoring from a different browser failed.")
        else:
            self._warn("Unknown backup format.")

    def restore_to_first(self):
        self.__restore(self.first_browser)

    def restore_to_second(self):
        self.__restore(self.second_browser)


def main():
    app = QtGui.QApplication(sys.argv)
    form = RESToolUI()
    form.show()
    app.exec_()


def cli():
    pass


if __name__ == '__main__':
    main()
