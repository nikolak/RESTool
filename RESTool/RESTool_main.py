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
__version__ = '0.3.0'

import sys

try:
    from RESTool import restool_cli
except ImportError:
    import restool_cli

if len(sys.argv) > 1:
    if sys.argv[1] == "cli":
        restool_cli.execute(sys.argv[2:])
    print sys.arv
    exit()

import os
from PyQt4 import QtGui
import copy
import json
import webbrowser
from collections import OrderedDict
import urllib
import platform
import arrow

from PyQt4.QtCore import QThread, SIGNAL
from appdirs import AppDirs
from logbook import FileHandler, Logger, CRITICAL

log = Logger("Main Qt")
if os.path.exists("application.log"):
    log_handler = FileHandler('application.log')
    log_handler.push_application()
else:
    log.level = CRITICAL

from browsers import Chrome, Firefox, Safari, Chromium, Canary

try:
    from RESTool import restoolgui
except ImportError:
    import restoolgui


class checkUpdatesThread(QThread):
    def __init__(self, version):
        QThread.__init__(self)
        self.version = version
        self.update_exists = False

    def __del__(self):
        self.wait()

    def run(self):
        log.debug("Checking for updates...")
        self.running = True
        try:
            u = urllib.urlopen("https://api.github.com/repos/Nikola-K/RESTool/releases")
            j = json.load(u)
            tag = j[0]['tag_name']
            draft = j[0].get('draft', False)
            prerelease = j[0].get('prerelease', False)
            release_ver = tag.replace('v', '')
            log.debug("Latest release version {}".format(release_ver))
            if not prerelease and not draft:
                if self.version < release_ver:
                    self.update_exists = True
        except Exception as e:
            log.exception(e)

        if self.update_exists:
            log.info("Update exists, emitting yes.")
            self.emit(SIGNAL('update(QString)'), "yes")
        else:
            log.info("Update doesn't exist, emitting no.")
            self.emit(SIGNAL('update(QString)'), "no")

    def stop(self):
        self.running = False


class RESToolUI(QtGui.QMainWindow, restoolgui.Ui_MainWindow):
    # noinspection PyUnresolvedReferences
    def __init__(self, parent=None):
        super(RESToolUI, self).__init__(parent)
        log.info("setting up")
        self.setupUi(self)
        self.dirs = AppDirs("RESTool", "nikolak")
        self.config = None
        self.labelMessage.setVisible(False)
        self.lblUpdateAvailable.setVisible(False)
        self.lblVersion.setText("Version: {}".format(__version__))

        self.choices_first = OrderedDict({"None": None})
        self.choices_second = OrderedDict({"None": None})

        self.first_browser = None
        self.second_browser = None

        self.all_browsers = {"firefox": Firefox,
                             "chrome" : Chrome,
                             "safari" : Safari,
                             "canary" : Canary}
        self.backups = {}

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
        self.btnDeleteBackup.clicked.connect(self._delete_backup)

        # Settings

        self.btnBrowseBackupsFolder.clicked.connect(self.browse_backup_folder)
        self.btnEnableLogging.clicked.connect(self.enable_logging)
        self.btnDisableLogging.clicked.connect(self.disable_logging)
        self.btnSubmitBug.clicked.connect(self.submit_bug)
        self.btnRestoreSettings.clicked.connect(self.restore_settings)
        self.btnSaveSettings.clicked.connect(self.save_settings)
        self.btnRemoveLocalConfig.clicked.connect(self.remove_local_config)
        self.btnRemoveSystemConfig.clicked.connect(self.remove_sys_dir_config)

        self._set_available_browsers()
        self._set_available_profiles(True, True)

        self.load_settings()

        self._update_backups_list()

        if self.config['auto_update_check']:
            self.updateThread = checkUpdatesThread(__version__)
            self.connect(self.updateThread, SIGNAL("update(QString)"), self.update_status)
            self.updateThread.start()

    def update_status(self, status):
        if status == "yes":
            self.lblUpdateAvailable.setVisible(True)

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
            return None
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
        log.debug("_show_warning_label")
        self.labelMessage.setText(msg)
        self.labelMessage.setVisible(True)

    def _set_available_browsers(self):
        log.debug("_set_available_browsers")
        chrome = Chrome()
        firefox = Firefox()
        safari = Safari()
        chromium = Chromium()
        canary = Canary()

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

        if canary.res_exists:
            self.choices_first['Canary'] = canary
            self.choices_second['Canary'] = copy.copy(canary)

        for browser_name in self.choices_first:
            self.cboFirstBrowser.addItem(browser_name)
            self.cboSecondBrowser.addItem(browser_name)

        log.info("Available choices first {}".format(self.choices_first))

        if not self.choices_first:
            self._warn("RES could not be found in neither of the browsers!")

    def _set_available_profiles(self, for_first, for_second):
        log.debug("_set_available_profiles")
        first = self.choices_first.get(str(self.cboFirstBrowser.currentText()))
        second = self.choices_first.get(str(self.cboSecondBrowser.currentText()))

        if for_first:
            self.cboFirstBrowserProfile.clear()
            if first:
                try:
                    for key in first.available_profiles:
                        self.cboFirstBrowserProfile.addItem(key)
                except AttributeError:
                    self.cboFirstBrowserProfile.addItem("None")
            else:
                self.cboFirstBrowserProfile.addItem("None")

        if for_second:
            self.cboSecondBrowserProfile.clear()
            if second:
                try:
                    for key in second.available_profiles:
                        self.cboSecondBrowserProfile.addItem(key)
                except AttributeError:
                    self.cboSecondBrowserProfile.addItem("None")
            else:
                self.cboSecondBrowserProfile.addItem("None")

    def _first_browser_changed(self):
        log.debug("_first_browser_changed")
        self.first_browser = self.choices_first.get(str(self.cboFirstBrowser.currentText()))

        if not self.first_browser:
            self.cboFirstBrowserProfile.setCurrentIndex(0)
        self._set_available_profiles(for_first=True, for_second=False)
        self._update_ui_elements()

    def _first_browser_profile_changed(self):
        profile_name = str(self.cboFirstBrowserProfile.currentText())
        log.debug("Changing first browser profile to {}".format(profile_name))
        if profile_name == "None":
            return

        try:
            self.first_browser.change_profile(profile_name)
            self._update_ui_elements()
        except:
            log.warn("Browser does not support changing profiles.")

    def _second_browser_changed(self):
        log.debug("_second_browser_changed")
        self.second_browser = self.choices_second.get(str(self.cboSecondBrowser.currentText()))

        if not self.second_browser:
            self.second_br_profile = None
            self.cboSecondBrowserProfile.setCurrentIndex(0)
        self._set_available_profiles(for_first=False, for_second=True)
        self._update_ui_elements()

    def _second_browser_profile_changed(self):
        profile_name = str(self.cboSecondBrowserProfile.currentText())
        log.debug("Changing second browser profile to {}".format(profile_name))
        if profile_name == "None":
            return

        try:
            self.second_browser.change_profile(profile_name)
            self._update_ui_elements()
        except:
            log.warn("Browser does not support changing profiles.")

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
            if str(self.cboFirstBrowserProfile.currentText()) == \
                str(self.cboSecondBrowserProfile.currentText()):
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

        if (self.first_browser and not self.second_browser) or \
            (self.first_browser.res_exists and not self.second_browser.res_exists):
            self.btnBackupFirst.setEnabled(True)
            self.btnRestoreToFirst.setEnabled(True)

            self.btnBackupSecond.setEnabled(False)
            self.btnRestoreToSecond.setEnabled(False)
            self.btnFirstToSecond.setEnabled(False)
            self.btnSecondToFirst.setEnabled(False)
            return

        if (self.second_browser and not self.first_browser) or \
            (self.second_browser.res_exists and not self.first_browser.res_exists):
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
        log.debug("_update backups lis")
        self.listBackups.clear()
        self.backups = {}
        local_folder = self.config['bak_folder']
        system_folder = self.dirs.user_data_dir
        default_folder = "res_backups"
        folders_to_check = [local_folder, system_folder, default_folder]
        log.debug("folders to check {}".format(folders_to_check))
        for folder in folders_to_check:
            if os.path.exists(folder):
                try:
                    for item in os.listdir(folder):
                        if item.endswith(".resbak"):
                            self.backups[item] = os.path.join(folder, item)
                except Exception as e:
                    log.exception(e)
            else:
                log.debug("{} does not exist".format(folder))

        backup_names = self.backups.keys()
        backups_date_dict = {}
        for backup in backup_names:
            backup_date = backup.split('.')[1:2][0]
            backups_date_dict[backup]=arrow.get(backup_date)


        for backup_name in sorted(backups_date_dict,
                                  key=backups_date_dict.get,
                                  reverse=True):
            self.listBackups.addItem(backup_name)

    def _delete_backup(self):
        try:
            selected_backup = str(self.listBackups.selectedItems()[0].text())
        except IndexError:
            log.error("No backup selected for deletion")

        try:
            os.remove(self.backups.get(selected_backup))
        except Exception as e:
            log.exception(e)
            log.debug("Failed to remove backup at {}".format(selected_backup))

        self._update_backups_list()

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
        do_migration = True
        if self.second_browser.is_running:
            do_migration = self._prompt(msg="It seems like the second browser is running. "
                                            "All changes will most likely not be applied."
                                            "Are you sure you want to continue?")
        if do_migration:
            self.__migrate(self.first_browser, self.second_browser)
        else:
            self._info(msg="Migration canceled.")

    def migrate_second_to_first(self):
        do_migration = True
        if self.first_browser.is_running:
            do_migration = self._prompt(msg="It seems like the first browser is running. "
                                            "All changes will most likely not be applied."
                                            "Are you sure you want to continue?")
        if do_migration:
            self.__migrate(self.second_browser, self.first_browser)
        else:
            self._info(msg="Migration canceled.")

    def __backup(self, browser):
        log.info("Backing up {}".format(browser.name))
        use_bak_dir = self.config.get("sys_dir_bak")
        time_f = self.config.get("bak_format")
        if use_bak_dir:
            bak_dir = self.dirs.user_data_dir
        else:
            bak_dir = self.config.get("bak_folder")

        if not browser:
            return

        if browser.backup(bak_dir, time_f):
            self._update_backups_list()
            self._info("Backing up done successfully!")
        else:
            self._warn("Backing up failed.")

    def backup_first(self):
        if self.first_browser.is_running:
            self._warn(msg="It looks like the browser you're trying to back up is running. "
                           "To make sure the backup includes the latest data please close the browser.")
        self.__backup(self.first_browser)

    def backup_second(self):
        if self.second_browser.is_running:
            self._warn(msg="It looks like the browser you're trying to back up is running. "
                           "To make sure the backup includes the latest data please close the browser.")

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
        backup_path = self.backups.get(selected_backup)
        log.debug("Selected backup: {}".format(selected_backup))
        log.debug("Backup path: {}".format(backup_path))
        log.debug("Restore format")

        if backup_browser == restore_format:

            if browser.restore_from_self(backup_path):
                self._info("Restoring from backup done!")
            else:
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

            if browser.set_data(restore_data):
                self._info("Restoring from backup done!")
            else:
                self._warn("Restoring from a different browser failed.")
        else:
            self._warn("Unknown backup format.")

    def restore_to_first(self):
        do_restore = True
        if self.first_browser.is_running:
            do_restore = self._prompt(msg="It seems like the first browser is running. "
                                          "This could lead to failed restoration."
                                          "Are you sure you want to continue?")
        if do_restore:
            self.__restore(self.first_browser)
        else:
            self._info(msg="Aborting restore.")

    def restore_to_second(self):
        do_restore = True
        if self.second_browser.is_running:
            do_restore = self._prompt(msg="It seems like the first browser is running. "
                                          "This could lead to failed restoration."
                                          "Are you sure you want to continue?")
        if do_restore:
            self.__restore(self.second_browser)
        else:
            self._info(msg="Aborting restore.")

    # Settings Tab

    def browse_backup_folder(self):
        log.debug("browsing for backup folder")
        directory = QtGui.QFileDialog.getExistingDirectory(self,
                                                           "Backup Folder")

        if directory:
            log.debug("backup folder set as {}".format(directory))
            self.lneBackupFolder.setText(directory)

    def enable_logging(self):
        log.debug("enable_logging")
        if not os.path.exists("application.log"):
            try:
                with open("application.log", "w") as tmp:
                    tmp.write("Log Start")
                log.info("log file created")
                self.DebuggingStatusLabel.setText("Current logging status: Enabled")
                self._info("Log file created, all actions will now be saved to application.log file.\n"
                           "Please restart the application in order for all operations to be logged.\n"
                           "After you're done with sending the log press 'Disable Logging'\n")

            except Exception as e:
                log.exception(e)
                self._warn("Could not create the log file.\n"
                           "Try to create it manually.")

    def disable_logging(self):
        log.debug("disable_logging")
        if os.path.exists("application.log"):
            try:
                os.remove("application.log")
                log.info("log file removed")
                self.DebuggingStatusLabel.setText("Current logging status: Disabled")
                self._info("Application log file has been removed from your system.")
            except Exception as e:
                log.exception(e)
                self._warn("Could not remove the application log from your system!\n"
                           "Try to manually remove 'application.log' file.")

    def submit_bug(self):

        github_prompt = self._prompt(msg="Do you have a GitHub account? \n"
                                         "If not then your default email client will be used for reporting the issue")
        message_body = "Issue description:%0D%0A" \
                       "How to reproduce:%0D%0A" \
                       "Operating systems and/or browsers affected:%0D%0A" \
                       "RESTool version:{ver}%0D%0A" \
                       "Operating System version:{platform}%0D%0A" \
                       "----------------------------%0D%0A" \
                       "Attach a log file if possible.".format(ver=__version__,
                                                               platform=platform.platform()
                                                               )

        if github_prompt is None:  # Cancel
            return
        elif github_prompt is False:  # No
            webbrowser.open("mailto:nikolak@outlook.com?subject=RESTool Bug Report&body={}".format(message_body))
        else:  # Yes
            webbrowser.open("https://github.com/Nikola-K/RESTool/issues/new?body={}".format(message_body))

    def restore_settings(self):
        log.info("restore_settings")
        self.lneBackupFolder.setText("res_backups")
        self.chkAutomaticBakFolder.setChecked(False)
        self.lneBackupTimeFormat.setText("%Y-%m-%d")
        self.chkPortableSettings.setChecked(True)
        self.chkAutomaticUpdates.setChecked(False)
        self._info("Settings restored to their default values but not saved.\n"
                   "Use the 'Save Current Settings' button to write the changes.\n"
                   "Logging is not affected.")

    def save_settings(self):
        log.debug("save_settings")
        config_dir = None
        if self.chkPortableSettings.isChecked():
            config_file = "settings.json"
        else:
            config_dir = self.dirs.user_data_dir
            config_file = os.path.join(config_dir, "settings.json")

        log.info("saving file to {}".format(config_file))

        config = {"bak_folder"       : str(self.lneBackupFolder.text()),
                  "sys_dir_bak"      : self.chkAutomaticBakFolder.isChecked(),
                  "bak_format"       : str(self.lneBackupTimeFormat.text()),
                  "portable_config"  : self.chkPortableSettings.isChecked(),
                  "auto_update_check": self.chkAutomaticUpdates.isChecked()
                  }

        try:
            if config_dir and not os.path.exists(config_dir):
                log.debug("Creating config dir")
                os.makedirs(config_dir)

            with open(config_file, "w") as out_file:
                json.dump(config, out_file, indent=True)
            self.config = config
            log.info("Settings saved")
            self._info("Settings saved to {}".format(config_file))

        except Exception as e:
            log.exception(e)
            self._warn("Saving settings failed.")

    def remove_local_config(self):
        log.info("removing local config")
        if os.path.exists("settings.json"):
            try:
                os.remove("settings.json")
                log.debug("config file removed from settings.json")
                self._info("Config file removed.")
            except Exception as e:
                log.exception(e)
                self._warn("Removing local config file failed.")
        else:
            log.debug("no file to remove")

    def remove_sys_dir_config(self):
        log.info("removing local config")
        config_file = os.path.join(self.dirs.user_data_dir, "settings.json")
        if os.path.exists(config_file):
            try:
                os.remove(config_file)
                log.debug("config file removed from {}".format(config_file))
                self._info("Config file removed.")
            except Exception as e:
                log.exception(e)
                self._warn("Removing config file from system folder failed.")
        else:
            log.debug("no file to remove")

    def load_settings(self):
        log.info("Loading settings")
        config_dir = self.dirs.user_data_dir
        sys_config_file = os.path.join(config_dir, "settings.json")
        loc_config_file = "settings.json"
        if os.path.exists(sys_config_file):  # system file is preferred
            log.debug("system config file found")
            config_file = sys_config_file
        elif os.path.exists(loc_config_file):
            log.debug("local config file found")
            config_file = loc_config_file
        else:
            log.info("no config file found")
            config_file = None

        if config_file:
            with open(config_file) as input_file:
                try:
                    self.config = json.load(input_file)
                except Exception as e:
                    log.exception(e)
        else:
            log.info("setting default config")
            self.config = {
                "sys_dir_bak"      : False,
                "bak_format"       : "%Y-%m-%d",
                "bak_folder"       : "res_backups",
                "portable_config"  : True,
                "auto_update_check": True
            }

        self.lneBackupFolder.setText(self.config['bak_folder'])
        self.chkAutomaticBakFolder.setChecked(self.config['sys_dir_bak'])
        self.lneBackupTimeFormat.setText(self.config['bak_format'])
        self.chkPortableSettings.setChecked(self.config['portable_config'])
        self.chkAutomaticUpdates.setChecked(self.config['auto_update_check'])


def main():
    app = QtGui.QApplication(sys.argv)
    form = RESToolUI()
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()
