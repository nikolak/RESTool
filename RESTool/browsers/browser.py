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
import os
import platform
import shutil
from time import strftime

from logbook import FileHandler, Logger

if os.path.exists("application.log"):
    log_handler = FileHandler('application.log')
    log_handler.push_application()
log = Logger("Browser")


class Browser(object):
    def _expand(self, path):
        log.debug("Expanding: {}".format(path))

        if self.os == "linux" or self.os == "darwin":
            return os.path.expanduser(path)
        elif self.os == "windows" and platform.release() != "XP":
            return os.path.expandvars(path)
        else:
            log.error("Unsupported OS: {} - expanding failed.".format(self.os))
            return None

    def _backup_file(self, bak_dir, source_path, dest_name):
        log.debug(" _backup_file with bak_dir={} path={} fname={}".format(bak_dir,
                                                                          source_path, dest_name))

        if not os.path.exists(source_path):
            log.error("Path not found {}".format(source_path))
            return False

        if not os.path.exists(bak_dir):
            try:
                os.makedirs(bak_dir)
            except IOError as e:
                log.error("IOError encountered while trying to create res_backups folder. Aborting.")
                log.exception(e)
                return False
            except Exception as e:
                log.error("Exception occurred while trying to create res_bacups folder.")
                log.exception(e)
                return False

        destination = os.path.join(bak_dir, dest_name)
        log.debug("Source and destination exist. Trying to copy {} to {}".format(source_path, destination))
        try:
            shutil.copy(source_path, destination)
            return True
        except IOError as e:
            log.exception(e)
            log.error("Copy failed due to IOError")
            return False
        except Exception as e:
            log.exception(e)

    def backup(self, dir_path=None, time_format=None):
        log.debug("backup dir_path={}, time_format={}".format(dir_path,
                                                              time_format))
        bak_dir = dir_path if dir_path else "res_backups"
        t_format = time_format if time_format else "%Y-%m-%d"

        file_name = "{}.{}.resbak".format(self.name, strftime(t_format))
        full_path = os.path.join(bak_dir, file_name)
        log.debug("full path backup:{}".format(full_path))
        try:
            return self._backup_file(bak_dir, self.path, file_name)
        except Exception as e:
            log.exception(e)
            return False
