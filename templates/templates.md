Test Template API
=================

Test files are made by jinja2 template engine http://jinja.pocoo.org
Look here for template language documentation http://jinja.pocoo.org/docs/jinja-docs.pdf

General
-------

* modules_path - Path to modules inside test host system
* local_modules_path - Path to modules where tests files are made. Could be same as modules_path
* internal_modules_path - Path to modules inside guest VM
* internal_manifests_path - Path to manifests inside guest VM
* tests_directory_path - Path to directory where tests files will be saved

PuppetModule
------------

* module.name - Module's name
* module.path - Path to module on system where tests are made
* module.tests - List of PuppetTest objects

PuppetTest
----------

* PuppetTest

* test.name - Name of this test
* test.path - Path to this test. Relative to module's path and without file name.
* test.file - File of this test

Examples
--------

Puppet modules are in /etc/puppet/modules
Module: ntpd

ntpd.name = ntpd
ntpd.path = /etc/puppet/modules/ntpd

This module has one test: tests/init.pp

test.name = init
test.path = tests
test.file = init.pp

