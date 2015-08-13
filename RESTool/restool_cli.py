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

import argparse
import os
import sys
from logbook import FileHandler, Logger, CRITICAL
from browsers import Chrome, Chromium, Firefox, Safari, Canary
import json
from appdirs import AppDirs

log = Logger("CLI")
if os.path.exists("application.log"):
    log_handler = FileHandler('application.log')
    log_handler.push_application()
else:
    log.level = CRITICAL


class CommandLine(object):
    def __init__(self):
        self.chrome = Chrome()
        self.firefox = Firefox()
        self.safari = Safari()
        self.chromium = Chromium()
        self.canary = Canary()
        self.all_browsers = {'chrome': self.chrome,
                             'firefox': self.firefox,
                             'safari': self.safari,
                             'chromium': self.chromium,
                             'canary': self.canary}

        self.dirs = AppDirs("RESTool", "nikolak")
        self.backup_folder = "res_backups"
        if os.path.exists('settings.json'):
            with open('settings.json') as settings:
                config = json.load(settings)
                if config['sys_dir_bak']:
                    self.backup_folder = self.dirs.user_data_dir
                elif config['bak_folder']:
                    self.backup_folder = config['bak_folder']
                else:
                    log.debug("No custom backup folder set")
        log.info('Backup/restore folder set to {}'.format(self.backup_folder))

    def list_browsers(self):
        print "Browsers and profiles that contain RES:"
        print '-' * 40
        for browser in self.all_browsers.values():
            if browser.res_exists:
                if hasattr(browser, 'available_profiles'):
                    print "'{}' Profiles:".format(browser.name.title())
                    for profile_name in browser.available_profiles:
                        browser.change_profile(profile_name)
                        if browser.res_exists:
                            print "\t Profile: '{}' [RES FOUND]".format(
                                profile_name)
                        else:
                            print "\t Profile: '{}' [RES NOT FOUND]".format(
                                profile_name)
                else:
                    if browser.res_exists:
                        print browser.name.title() + " [RES FOUND] (Profiles not supported)"
                    else:
                        print browser.name.title() + " [RES NOT FOUND] (Profiles not supported)"

    def _verify(self, browser_name, profile_name=None):
        if browser_name.lower() not in self.all_browsers.keys():
            return "Browser not found, did you enter the name correctly?"

        browser = self.all_browsers[browser_name.lower()]
        if profile_name:
            if not hasattr(browser, 'available_profiles'):
                return "{} does not support profiles".format(browser_name)
            elif profile_name not in browser.available_profiles:
                return "{} is not in list of available profiles for {}".format(
                    profile_name, browser_name
                )
            else:
                log.debug('Setting profile for {} to {}'.format(browser_name,
                                                                profile_name))
                browser.change_profile(profile_name)
        else:
            if hasattr(browser, 'available_profiles'):
                print "Please specify profile name you want to backup."
                return "Avialable profiles: {}".format(
                    ','.join(browser.available_profiles.keys()))

        if not browser.res_exists:
            return "RES was not found in the specified browser and/or profile"

        return browser

    def backup(self, browser_name, profile_name=None):
        browser = self._verify(browser_name, profile_name)
        if isinstance(browser, str):  # it's an error
            return browser

        if browser.backup(self.backup_folder, "%Y-%m-%d"):
            return "{} backed up to {} sucessfully".format(browser_name,
                                                           self.backup_folder)

    def restore(self, browser_name, profile_name=None, backup_file=None):
        browser = self._verify(browser_name, profile_name)
        if isinstance(browser, str):  # it's an error
            return browser



def execute(cli_args):
    args = None
    parser = argparse.ArgumentParser(prog='RESTool Command Line Interface. '
                                          'See github for usage examples.')
    parser.add_argument('-l', '--list', action='store_true',
                        help="List all available browsers and profiles to use for other commands.")

    parser.add_argument('-b', '--backup', action='store_true',
                        help="Backup the specified browser and profile RES settings to the backup folder "
                             "specified in the settings.json if it exists, otherwise backup to local 'res_backups' folder")

    parser.add_argument('-r', '--restore', type=str,
                        help="Restore the backup from the selected file. You can use 'latest' to restore backup "
                             "from the latest file found in the backups folder. RES Tool will search "
                             "for previous backup files in the res backups folder specified in settings.json or "
                             "the default location res_backups in the current directory")

    parser.add_argument('-w', '--browser', type=str,
                        help="Name of the browser to execute specified command on.")

    parser.add_argument('-p', '--profile', type=str,
                        help="Name of the profile in the specified browser to run the command on. (optional, case sensitive) "
                             "Note: Not all browsers support profiles. Run --list to see supported browsers and their profiles.")

    parser.add_argument('-d', '--debug', action='store_true',
                        help="Create log file for debugging.")
    if cli_args:
        args = parser.parse_args(cli_args)
    else:
        parser.print_help()
        exit()

    if args.debug:
        with open("application.log", "w") as _:
            print "application.log file created, please run the commands again" \
                  "and see the github page on how to properly submit a bug report." \
                  "https://github.com/Nikola-K/RESTool"
        exit()

    app = CommandLine()

    if args.list:
        app.list_browsers()
    elif args.backup:
        if not args.browser:
            print "You need to specify which browser to backup"
            exit()
        print app.backup(args.browser, args.profile)
    elif args.restore:
        if not args.browser:
            print "You need to specify which browser to backup"
            exit()
        print app.restore(args.browser, args.profile, args.restore)
