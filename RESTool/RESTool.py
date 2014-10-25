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

import os
import ConfigParser
import json
import sqlite3
import codecs


def _expand(path):
    return os.path.expanduser(path)


def get_firefox():
    print "Getting firefox path..."
    base = _expand("~/.mozilla/firefox/")
    profile_folder = None
    profile_file = "jetpack/jid1-xUfzOsOFlzSOXg@jetpack/simple-storage/store.json"
    profiles = ConfigParser.RawConfigParser()
    profiles.read(os.path.join(base, 'profiles.ini'))
    profiles.remove_section('General')

    if len(profiles.sections()) < 2:
        profile_folder = profiles.get(profiles.sections()[0], 'Path')
    else:
        profile_dict = {}
        for index, profile in enumerate(profiles.sections()):
            profile_dict[index] = [profiles.get(profiles.sections()[index], 'Name'),
                                   profiles.get(profiles.sections()[index], 'Path')]
        while not profile_folder:
            for key, value in profile_dict.items():
                print "{}: {}".format(key, value[0])
            user_input = raw_input(
                "Enter the number of the profile you want to use:\n>>>")

            try:
                i = int(user_input)
                profile_folder = profile_dict[i][1]
            except:
                print "Invalid input"
    try:
        return os.path.join(base, profile_folder, profile_file)
    except AttributeError:
        print "Could not find valid firefox path"


def get_chrome():
    print "Getting chrome path..."
    c_file = "~/.config/google-chrome/Default/Local Storage/chrome-extension_kbmfpngjjgdllneeigpgjifpgocmfgmb_0.localstorage"
    abs_file = _expand(c_file)
    if os.path.exists(abs_file):
        return abs_file
    else:
        print "Could not fnd valid chrome path"


def chrome_to_ff():
    chrome_path = get_chrome()
    firefox_path = get_firefox()

    if not chrome_path or not firefox_path:
        print "Can not find all required files"
        return

    print "Connecting database..."
    con = sqlite3.connect(chrome_path)
    c = con.cursor()
    print "Getting database data..."
    db = c.execute(
        'SELECT key, CAST(value AS TEXT) FROM ItemTable').fetchall()
    print "Opening firefox file..."
    with codecs.open(firefox_path, 'w', 'utf-8') as firefox_out:
        dump = json.dumps(dict(db))
        print "Writing to firefox file..."
        firefox_out.write(dump)
    print "Done!"


def ff_to_chorme():
    chrome_path = get_chrome()
    firefox_path = get_firefox()

    if not chrome_path or not firefox_path:
        print "Can not find all required files"
        return

    print "Connecting database..."
    conn = sqlite3.connect(chrome_path)
    c = conn.cursor()
    print "Opening firefox file..."
    with codecs.open(firefox_path, "r", "utf-8") as firefox_in:
        print "Getting database data..."
        ff_json = json.load(firefox_in)

    ff_data = [(key, value) for key, value in ff_json.items()]
    print "Inserting new data..."
    c.executemany(
        "INSERT OR IGNORE INTO ItemTable (key,value) VALUES(?,?)", ff_data)
    print "Updating new data..."
    for data in ff_data:
        c.execute(
            "UPDATE ItemTable SET value=? WHERE  key=?", (data[1], data[0]))
    print "Commiting changes..."
    conn.commit()
    c.close()
    print "Done!"


if __name__ == '__main__':
    while True:
        print "*" * 50
        print "1.Chrome to firefox\n2.Firefox to chrome"
        user_input = raw_input(
            "Pick an option or just press enter to quit\n>>>")
        if user_input == "1":
            chrome_to_ff()
        elif user_input == "2":
            ff_to_chorme()
        else:
            break
