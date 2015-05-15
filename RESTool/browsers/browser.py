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
import traceback

from logbook import FileHandler, Logger
import sys

if os.path.exists("application.log"):
    log_handler = FileHandler('application.log')
    log_handler.push_application()
log = Logger("Browser")

def extract_function_name():
    """Extracts failing function name from Traceback

    by Alex Martelli
    http://stackoverflow.com/questions/2380073/\
    how-to-identify-what-function-call-raise-an-exception-in-python
    """
    tb = sys.exc_info()[-1]
    stk = traceback.extract_tb(tb, 1)
    fname = stk[0][3]
    return fname


def log_exception(e):
    log.critical(
        "Function {function_name} raised {exception_class} ({exception_docstring}): {exception_message}".format(
            function_name=extract_function_name(),
            exception_class=e.__class__,
            exception_docstring=e.__doc__,
            exception_message=e.message))

class Browser(object):
    def _expand(self, path):
        log.debug("Expanding: {}".format(path))

        if self.os == "linux":
            return os.path.expanduser(path)
        elif self.os == "windows" and platform.release() != "XP":
            return os.path.expandvars(path)
        else:
            log.error("Unsupported OS: {} - expanding failed.".format(self.os))
            return None

    def _backup_file(self, path, fname):
        log.debug(" _backup_file with path={} fname={}".format(path, fname))
        if not os.path.exists(path):
            log.error("Path not found {}".format(path))
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
            return True
        except IOError:
            log.error("Copy failed due to IOError")
            return False
        except Exception as e:
            log_exception(e)
