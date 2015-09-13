.. :changelog:

History
-------

0.3.0dev (TBD)
--------------

* Command line interface for automating tasks using cron or windows task scheduler

* Fixed a bug where converting data to chrome would fail

* Improved checks that verify that the data provided is valid

* Added checks that notify the user if one of the selected browsers is running

* Added profile support for Google Chrome and Google Canary

* Code cleanup

* Backups list is now sorted from latest to oldest

0.2.1 (2015-05-29)
------------------

* Fix error when converting data from firefox to sqlite database when value is a long int.

* Reduce Windows executable startup time by up to 80%.

* Fix Windows Runtime Error (R6034)

* Update check enabled by default

0.2.0 (2015-05-17)
------------------

New features:

* Completely rewritten and improved GUI

* Full OS X Support (For all features)

* Windows 10 Support

* Chromium Support

* Safari (OS X) Support

* Chrome Canary Support (OS X, Windows)

* Custom settings

* Built in logging toggle and easier bug reporting

* Automatic update checks (opt-in, default off)

* Removed donation links

Code changes:

* Moved logic code out of GUI class

* Improved migrating logic to make sure files exist

* Made logging more descriptive

* Code reorganization

* Moved browsers to separate package

* Support for additional browsers and operating systems

* py2app support

* Custom settings directories for different operating systems

* Proper handling of data checks before doing any sqlite changes

* Browser class with some commonly shared methods

* Logbook integrated logging for everything

Other changes:

* Slightly improved docs

* Custom landing page using github pages

0.1.0 (2014-10-28)
------------------

First public release.

New features:

* Backup RES settings from Chrome and Firefox

* Restore RES settings

* Migrate data between browsers

* Restore settings into a different browser

* Linux and Windows (Vista and above) supported


0.1.0dev (2014-10-25)
---------------------

* Initial commit to github.

0.1.0dev (2014-10-24)
---------------------

* Development started
