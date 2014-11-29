#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_RESTool
----------------------------------

Tests for `RESTool` module.
"""

import unittest
import os
import shutil
from time import strftime
from RESTool.RESTool_main import Chrome, Firefox


class TestRES(unittest.TestCase):

    def setUp(self):
        self.chrome_sourcefile = "chrome.sqlite"
        self.firefox_sourcefile = "firefox.json"
        self.chrome = Chrome()
        self.firefox = Firefox()
        self.chrome.path =  self.chrome_sourcefile
        self.firefox.path = self.firefox_sourcefile


    def test_chrome_backup(self):
        backup_name = "chrome.{}.backup".format(strftime("%Y-%m-%d"))
        backup_path = os.path.join("res_backups", backup_name)

        self.assertTrue(self.chrome.backup())
        self.assertTrue(os.path.exists(backup_path))
        self.assertEqual(open(self.chrome_sourcefile).read(), open(backup_path).read())

        self.chrome.path = None
        self.assertFalse(self.chrome.backup())

        self.chrome.path = "invalid"
        self.assertFalse(self.chrome.backup())

    def test_ff_backup(self):
        backup_name = "firefox.{}.backup".format(strftime("%Y-%m-%d"))
        backup_path = os.path.join("res_backups", backup_name)

        self.assertTrue(self.firefox.backup())
        self.assertTrue(os.path.exists(backup_path))
        self.assertEqual(open(self.firefox_sourcefile).read(), open(backup_path).read())

        self.firefox.path = None
        self.assertFalse(self.firefox.backup())

        self.firefox.path = "invalid"
        self.assertFalse(self.firefox.backup())

    def test_chrome_to_ff(self):
        pass

    def test_ff_to_chrome(self):
        pass


    def tearDown(self):
        shutil.rmtree('res_backups', ignore_errors=True)

if __name__ == '__main__':
    unittest.main()