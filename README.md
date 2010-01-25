tuxedo
======

An improved version of the [Bouncer](https://wiki.mozilla.org/Bouncer) mirror
management software.

Bouncer is a Mozilla project. The new admin backend was originally written by
Frederic Wenzel (fwenzel@mozilla.com).

Getting Started
---------------

### Python
You need Python 2.6. Also, you probably want to run this application in a
[virtualenv][virtualenv] environment.

Run ``easy_install pip`` followed by ``pip install -r requirements.txt``
to install the required Python libraries.

[virtualenv]: http://pypi.python.org/pypi/virtualenv

### Initial Database Setup
If you're installing a new copy of Bouncer, run ``./manage.py syncdb``
followed by ``./manage.py migrate`` (see "Database Migrations" below).

### Database Migrations
I am using [South](http://south.aeracode.org/) to keep track of database
migrations. ``./manage.py migrate`` will apply these migrations when
necessary.

### Upgrading an older version of Bouncer
If you are upgrading from an earlier version of Bouncer that isn't locale-
aware yet, apply ``sql/bouncer-add-lang.sql`` first.

Then, apply ``sql/incremental.sql`` to bring the DB up to date.

Finally, run the following steps to initialize Django and South:

    ./manage.py syncdb   # initialize django
    # (answer "no" to the "add a new admin?" question)
    ./manage.py migrate mirror 0001 --fake   # initialize South
    ./manage.py migrate   # apply all existing migrations

Language and Product Details
----------------------------
The list of known languages is provided by ``languages.json`` in the directory
``inc/product-details/json``. The source of the data is the [Mozilla
product-details library]. Feel free to update the JSON files from there.

[prod-details]: http://svn.mozilla.org/libs/product-details/

Why "tuxedo"?
-------------
In my silly mind, I chose to interpret "Bouncer" as "doorman" and subsequently
decided that its new version should be codenamed like what fancy bouncers wear:
a tuxedo.

Licensing
---------
This software is licensed under the [Mozilla Tri-License][MPL]:

    ***** BEGIN LICENSE BLOCK *****
    Version: MPL 1.1/GPL 2.0/LGPL 2.1

    The contents of this file are subject to the Mozilla Public License Version
    1.1 (the "License"); you may not use this file except in compliance with
    the License. You may obtain a copy of the License at
    http://www.mozilla.org/MPL/

    Software distributed under the License is distributed on an "AS IS" basis,
    WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
    for the specific language governing rights and limitations under the
    License.

    The Original Code is tuxedo.

    The Initial Developer of the Original Code is Mozilla.
    Portions created by the Initial Developer are Copyright (C) 2010
    the Initial Developer. All Rights Reserved.

    Contributor(s):
      Frederic Wenzel <fwenzel@mozilla.com>

    Alternatively, the contents of this file may be used under the terms of
    either the GNU General Public License Version 2 or later (the "GPL"), or
    the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),
    in which case the provisions of the GPL or the LGPL are applicable instead
    of those above. If you wish to allow use of your version of this file only
    under the terms of either the GPL or the LGPL, and not to allow others to
    use your version of this file under the terms of the MPL, indicate your
    decision by deleting the provisions above and replace them with the notice
    and other provisions required by the GPL or the LGPL. If you do not delete
    the provisions above, a recipient may use your version of this file under
    the terms of any one of the MPL, the GPL or the LGPL.

    ***** END LICENSE BLOCK *****

[MPL]: http://www.mozilla.org/MPL/

