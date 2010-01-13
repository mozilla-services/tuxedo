tuxedo
======

An improved version of the [Bouncer](https://wiki.mozilla.org/Bouncer) mirror
management software.

Bouncer is a Mozilla project. The new admin backend was originally written by
Frederic Wenzel (fwenzel@mozilla.com).

Getting Started
---------------
If you're migrating from an older version of Bouncer, you want to run
``sql/incremental.sql`` to bring the DB up to date, followed by a
``python manage.py syncdb`` to create Django-specific tables.

If you're installing a new copy, just the ``...syncdb`` command should do.

LICENSE
-------
tuxedo is licensed under the New BSD License. Check the file LICENSE for more
information.

Why "tuxedo"?
-------------
In my silly mind, I chose to interpret "Bouncer" as "doorman" and subsequently
decided that its new version should be codenamed like what fancy bouncers wear:
a tuxedo.

