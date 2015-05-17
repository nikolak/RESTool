=======
RESTool
=======

**For stable release please see download link below, the current master branch is for development only and may be broken and lead to loss of data!**

Unofficial cross platform tool for migrating between browsers, backing up, and restoring from backups,
"Reddit Enhancement Suite" aka RES settings.

**This application is in no way affiliated with RES** and all issues should be reported to RESTool author and not RES authors
or subreddits that are used for RES troubleshooting/issue reporting.

See Features_ for a list of software features, Screenshots_ to see how it looks like, or
simply jump to Downloads_ to use it.

For explanation of the options available see Usage_ section and for any issues Help_ section
and for other common questions see FAQs_.

If you have any questions you can contact me directly via email that's visible on
my `GitHub Profile <https://github.com/Nikola-K>`_

Seeing how this is version 0.2 manual backup, just in case something goes wrong, of RES settings file is recommended.
See `This page <https://www.reddit.com/r/Enhancement/wiki/backing_up_res_settings>`_ for information on
how to make manual backup

* License: Apache license Version 2.0. See LICENSE file for more info.

Features
========

* Works for all major browsers: Chrome, Chrome Canary, Chromium, Firefox, Safari

* Backup RES settings for all browsers listed.

* Restore RES settings from backups.

* Migrate data between browsers (e.g. Firefox to Chrome).

* Restore backed up settings into a different browser.

* Cross platform Linux (All), Windows (Vista and up), OS X (Mavericks and up)

* Simple to use GUI (see screenshot below)

Screenshots
===========

Linux xubuntu 15.04:
--------------------

.. image :: docs/0.1.0dev_linux.png

Windows 10:
-----------

.. image :: docs/0.2.0windows.PNG

OS X Mavericks:
---------------

.. image :: docs/0.2.0osx.PNG


Downloads
=========

Windows
-------

**Note:** The only requirement is `Microsoft Visual C++ 2008 Redistributable <http://www.microsoft.com/en-us/download/details.aspx?id=29>`_
which you probably already have installed, but if you can not get the app to run
try installing visual c++ 2008 redistributable from the link above.

You can find the latest stable build here: https://github.com/Nikola-K/RESTool/releases

Windows Vista and up are supported. Tested on Windows 7 32bit.

OS X
----
Apple OS X distribution is packed as a .app package and can be downloaded here: https://github.com/Nikola-K/RESTool/releases


Linux
-----

There is no binary provided for linux but the only requirements are Python 2.7 and pyqt, both of which
are available in most distro repos. You can run the application, after installing pyqt, by simply downloading
the source from releases and running `RESTool_main.py` from your command line.

Tested on xubuntu 64bit.

Usage
=====

This section gives short description of main features:

Profile
-------

Some browsers like Firefox support multiple profiles; you can pick (if you have more than one) which profile to use for
the other features from the dropdown box.

First Browser To The Second
---------------------------

This will take all RES settings from browser and profile selected as "First Browser" in the upper part of the window,
and move them to the "Second Browser" that you selected.

**Note:** Migrating settings may fail, or make no changes to RES settings, if one or both browsers are running.

Second Browser To The First
---------------------------

Opposite of the above.

Takes RES settings from the browser and profile picked under "Second Browser" section of the app and copies them
to the "First Browser" that you picked.

**Note:** Migrating settings may fail, or make no changes to RES settings, if one or both browsers are running.

Backup First Browser
--------------------

Takes RES Settings from the browser you selected as first in the app and copies the settings to the backup folder.
Default is "res_backups" folder, but you can pick one yourself or use system specific directories for saving data.

If the backup folder does not exist it will be created. Make sure you have the necessary permissions to do so.

Backup Second Browser
---------------------

Takes RES Settings from the browser you selected as first in the app and copies the settings to the backup folder.
Default is "res_backups" folder, but you can pick one yourself or use system specific directories for saving data.

If the backup folder does not exist it will be created. Make sure you have the necessary permissions to do so.


Restore selected backup to the First Browser
--------------------------------------------

Pretty self explanatory, takes RES settings from the backup you selected on the right and copies it to the first browser.

Source browser of the backup is irrelevant.

**Note:** Browser MUST be closed for changes to take effect.

Restore selected backup to the Second Browser
---------------------------------------------

Pretty self explanatory, takes RES settings from the backup you selected on the right and copies it to the second browser.

Source browser of the backup is irrelevant.

**Note:** Browser MUST be closed for changes to take effect.

Delete selected backup file
---------------------------

Remove the selected backup file in the list permanently from the disk. This can not be undone.


Help
====

Can not start the application
-----------------------------

Make sure you have `Microsoft Visual C++ 2008 Redistributable <http://www.microsoft.com/en-us/download/details.aspx?id=29>`_ installed

How to report issues
--------------------

Click on Settings tab then click on "Enable Logging" button, a file named "application.log" will be created.

Close the app and restart it, recreate the issue you're having. Open Settings tab again and click on "Submit Bug Report" and follow instructions.

Attach the created application.log file if possible.

Once you're done to disable logging click on "Disable Logging" in the Settings menu, restart may be necessary to fully eliminate it.

If you're running Windows XP or browsers other than Firefox, Chrome, Chromium, Chrome Canary, Safari (OS X)
those operating systems and browsers are not supported so I can not guarantee that the issue you're having
will be fixed.

**Important:** As of version 0.2.0 the log file *may* (in very rare circumstances) contain some personal data, or even passwords (if they are saved using RES) you should remove any personal data you're not comfortable with sharing from the log file before submitting it.

Settings
========

This section will briefly go over the existing options in the Settings tab.

Backup Folder
-------------
Backup folder means which folder will be used by default for saving RES backups

If you check "use automatic system specific directory" checkbox the backups will be saved in following locations:

OS X:

    `/Users/<username>/Library/Application Support/RESTool`

Linux:

    `/home/<username>/.local/share/RESTool`

Windows:

    `C:\Users\<username>\AppData\Local\nikolak\RESTool`

Backup Time Format
------------------

Backup filename looks like this: `<browser name>.<time format>.<5 char unique id>.resbak`

You can change `<time format>` to whatever you want to which by default is `%Y-%m-%d` which produces e.g. `2015-05-17`

for a list of supported variables see: https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior

Portable RES Settings
---------------------

If you enable this the file `settings.json` will be created in case your config is different than default one.

If you disable portable settings the file `settings.json` will be saved in the same system locations that the automatic backup folder uses.

The two buttons allow you to easily remove those files without having to search for them automatically.

In case both local and system config files exist the system one is used.

Debugging
---------

The buttons are self explanatory and enable you to easily enable and disable application logging, which can be manually enabled by having `application.log` file in the same location as the app.

Automatic Update
----------------

The automatic update checkbox will simply allow app to check for  updates on startup.

No downloads or anything else is started if update is found, only a small text is displayed on the main page.

The update check does not send absolutely any private data - not even the current version or OS info.

**By default this feature is disabled.**

FAQs
====

Q: Why is the windows .exe or OS X .app size so big?
----------------------------------------------------

A: This application is written using Python and PyQt and "compiled" into an exe file using py2exe. (py2app for OS X)
Due to the nature of Python programming language, which does not offer native option to generate a single .exe,
the whole python and all the application dependencies are packed into one .exe file and extracted upon runtime.

Q: Why isn't [your favorite browser] supported?
-----------------------------------------------

A: Either there has been no requests for it or it's not officially supported by RES team.
(Browsers that are not officially supported by RES will not be added)

Q: Option ____ failed. What now?
--------------------------------

See the Help_ section on how to make the application log all the relevant data to a log file which you can then send to author to troubleshoot and fix the issue
