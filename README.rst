=========
Migranite
=========

Tool for manage migrations in your project.

-------
Install
-------

.. code-block ::

    pip install migranite

If you want to use MongoDB as database for migrations:

.. code-block ::

    pip install 'migranite[mongo]'

------------
How to start
------------

To initialize the migranite in your project run:

.. code-block ::

    migranite init --migrations migrations_dir --templates templates_dir

This command creates the config file (``.migranite``) and two directories (``migrations_dir`` and ``templates_dir``).

Create the first migration:

.. code-block ::

    migranite create my-first-migration

This is create the file ``migrations_dir/001-my-first-migration.py`` with an empty migration.
You need to write a module docstring and implement function ``run()`` with your migration logic.

Show the available migrations with statuses:

.. code-block ::

    migranite list

Run all migrations that haven't been started earlier:

.. code-block ::

    migranite run

Run only specified migrations:

.. code-block ::

    migranite run my-first-migration

Run the migrations that were started earlier:

.. code-block ::

    migranite run --force my-first-migration


-----------
Config file
-----------

A config file is a simple ini-file with three sections.

[migrations]
------------

Migrations settings.

:path: Path to directory with migrations.
:digits: Number of digits in migration number. Default ``3``.

[templates]
-----------

Templates settings.

:path: Path to directory with templates.
:default: Default template file name.

[database]
----------

Database settings. Currently only JSON file and MongoDB is supported.

:backend: Type of database backend (``json`` or ``mongo``).

Other settings are backend-specified.

**json**

:path: path to json file.

**mongo**

:host: Hostname or ip address. Default ``localhost``.
:port: Default ``27017``.
:name: Name of database. Required.
:collection: Name of collection. Default ``migrations``.
