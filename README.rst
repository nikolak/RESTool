=======
RESTool
=======


Unofficial cross platform tool for migrating between browsers, backing up, and restoring from backups,
"Reddit Enhancement Suite" aka RES settings.

**This application is in no way affiliated with RES** and all issues should be reported to author and not RES authors
or subreddits that are used for RES troubleshooting/issue reporting.

See Features_ for a list of software features, Screenshots_ to see how it looks like or
simply jump to Downloads_ to see how you can get it.

For explanation of the options available see Usage_ section and for any issues Help_ section
and for other common questions see FAQs_.

If you have any questions you can contact me directly via email that's visible on
my `GitHub Profile <https://github.com/Nikola-K>`_

Seeing how this is version 0.1 manual backup, just in case something goes wrong, of RES settings file is recommended.
See `This page <https://www.reddit.com/r/Enhancement/wiki/backing_up_res_settings>`_ for information on
how to make manual backup

* License: Apache license Version 2.0. See LICENSE file for more info.

Features
========

* Backup RES settings from Chrome and Firefox

* Restore RES settings

* Migrate data between browsers

* Restore settings into a different browser

* Cross platform (linux and windows only at the moment)

* Simple to use GUI (see screenshot below)

Screenshots
===========

Linux xubuntu 14.04:
--------------------

.. image :: docs/0.1.0dev_linux.png


Downloads
=========

You can pay for this software if you want, this helps fund the development
but it is not required for using all available features. See FAQs_ for more info.

Windows
-------

**Note:** The only requirement is `Microsoft Visual C++ 2008 Redistributable <http://www.microsoft.com/en-us/download/details.aspx?id=29>`_
which you probably already have installed, but if you can not get the app to run
try installing visual c++ 2008 redistributable from the link above.


+--------------------+-------------+------------------------------+
| Description        | Link        | Note                         |
+====================+=============+==============================+
| Pay $1.99 (PayPal) | paypal1_    | Use same link as             |
+--------------------+-------------+ free download                |
| Pay $4.99 (PayPal) | paypal2_    | for actually downloading     |
+--------------------+-------------+ the software                 |
| Pay $9.99 (PayPal) | paypal3_    |                              |
+--------------------+-------------+------------------------------+
| Free download      | releases_   |  (Windows exe, linux source) |
+--------------------+-------------+------------------------------+


.. _paypal1: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=QL25GUJ62G6UL

.. _paypal2: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=3TSJ7LSD5F8LG

.. _paypal3: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=BXPXJB2QUDSY2

.. _releases: https://github.com/Nikola-K/RESTool/releases

Windows Vista and up are supported. Tested on Windows 7 32bit.

Linux
-----

There is no binary provided for linux but the only requirements are python 2.7 and pyqt, both of which
are available in most distro repos. You can run the application, after installing pyqt, by simply downloading
the source and running `RESTool_main.py` from your command line.

Tested on xubuntu 32bit.

Usage
=====

This section gives short description of every feature available:

Firefox profile
---------------

Firefox supports multiple profiles, you can pick (if you have more than one) which profile to use for
the other features.

Chrome to Firefox
-----------------

Copies data from firefox RES settings file into Chrome file. Changes to settings are saved when the browser closes
so if you make a change be sure to close firefox before using this feature to ensure that all settings are
properly transferred.

Firefox to Chrome
-----------------

Copies data from Chrome RES settings file into Firefox file. Changes to settings are saved when the browser closes
so if you make a change be sure to close Chrome before using this feature to ensure that all settings are
properly transferred.

Backup Chrome
-------------

Copy the RES settings file from its location in Chrome data folder to subfolder named `res_backups` in the same
directory as the application. If the folder does not exist it will be created. Make sure that your account has the
necessary permissions to write changes to the location of the application.

Backup Firefox
--------------

Copy the RES settings file from its location in Firefox data folder to subfolder named `res_backups` in the same
directory as the application. If the folder does not exist it will be created. Make sure that your account has the
necessary permissions to write changes to the location of the application.

Restore selected backup to Chrome
---------------------------------

Restores the currently selected backup file in the list on the right to Chrome RES settings.

The backup file can be either backup created either using "Backup Chrome" or "Backup Fireofx" feature.

Restore selected backup to Firefox
----------------------------------

Restores the currently selected backup file in the list on the right to Chrome RES settings.

The backup file can be either backup created either using "Backup Chrome" or "Backup Fireofx" feature.

Pay for RESTool
---------------

Opens a paypal link to pay the amount picked in the dropbox on the right. See FAQs_ for more info about
paid vs free option.

Donate to RES
-------------

Opens website with info on how you can donate to RES and its author.

Delete selected backup file
---------------------------

Remove the selected backup file in the list permanently from the disk. This can not be undone.


Help
====

Can not start the application
-----------------------------

Make sure you have `Microsoft Visual C++ 2008 Redistributable <http://www.microsoft.com/en-us/download/details.aspx?id=29>`_ installed

How to report the issues
------------------------

Create a file named `log.txt` in the same location as the application and the necessary debug information should be
saved in it. Try running the application and reproducing the issue. You can report the issue by opening a new issue
on github, sending an email or contacting the author some other way.

You can upload the log file to pastebin.com, for example, if it's long.

If you're running OSX or Windows XP (or older) or browsers other than Firefox and Chrome
those operating systems and browsers are not supported so I can not guarantee that the issue you're having
will be fixed.


FAQs
====

Q: What is the difference between paying and downloading this for free?
-----------------------------------------------------------------------

A: There is no difference. PayPal does not allow me to accept donations so on top of providing free downloads
there is also option to pay for the application, paying supports further development and all users who pay $4.99 or more
will receive any paid options for free that may be introduced in the future. There is no guarantee that those
will be added but I am experimenting with automatic cloud backups.

Q: Why is the windows .exe size so big?
---------------------------------------

A: This application is written using Python and PyQt and "compiled" into an exe file using py2exe.
Due to the nature of Python programming language, which does not offer native option to generate a single .exe,
the whole python and all the application dependencies are packed into one .exe file and extracted upon runtime.

Q: Why isn't OSX and/or [your favorite browser] supported?
----------------------------------------------------------

A: I simply do not use them and no OS data is available for RES usage so I just picked two OS that I use and two
most popular browsers(Firefox and Chrome). If there is enough interest and support for the application regarding
adding more browsers and/or OS it will be added.
(Browsers that are not officially supported by RES will not be added)
