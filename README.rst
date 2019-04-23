.. role:: raw-html-m2r(raw)
   :format: html



.. raw:: html

   <p align="center">
     <img align="center" src="frontend/src/assets/logo-brand.png" alt="Logo" width="180"/>
   </p>


DbNet is a Python/VueJS database client to access Oracle, Spark (Hive), Postgres, etc. It is still a work in progess, but should work fine for daily use. MS SQL Server is supported, although with some bugs here and there due to JDBC/JTDS bridge.

**Only Chrome and Firefox are supported at the moment.**

Install
=======

.. code-block:: bash

   pip install dbnet

Command ``dbnet`` should now be available in the PATH.

Running
=======

``dbnet --help``

.. code-block:: bash

   usage: dbnet [-h] [--serve] [--init_db] [--reset_db] [--force] [--port PORT]

   DbNet Application

   optional arguments:
     -h, --help   show this help message and exit
     --serve      Start the DbNet server
     --init_db    Initiatlize the backend SQLite database
     --reset_db   Reset the backend SQLite database
     --force      Kill any running instance.
     --port PORT  The web application port

``dbnet --serve``

.. code-block:: bash

   2019-02-27 10:08:11 -- DB Tables OK.
   2019-02-27 10:08:11 -- Main Loop PID is 39685
   2019-02-27 10:08:11 -- Monitor Loop PID is 39691
   2019-02-27 10:08:11 -- Web Server PID is 39692
   2019-02-27 10:08:11 -- URL -> http://macbook:5566/?token=CqPahSJIeg1Nl4Kj
   (39692) wsgi starting up on http://0.0.0.0:5566

Setting up Dababase Profile
---------------------------

Your database profile / credentials needs to be set up at ``~/profile.yaml`` or env var ``PROFILE_YAML``.
Run command ``xutil-create-profile`` to create from template.

Example Entry
^^^^^^^^^^^^^

.. code-block:: yaml

   PG_XENIAL:
     name: PG_XENIAL
     host: xenial-server
     database: db1
     port: 5432
     user: user
     password: password
     type: postgresql
     url: "jdbc:postgresql://xenial-server:5432/db1?&ssl=false"

Screenshots
===========


.. image:: dbnet.screenshot.2.png
   :target: dbnet.screenshot.2.png
   :alt: Screenshot 2



.. image:: dbnet.screenshot.1.png
   :target: dbnet.screenshot.1.png
   :alt: Screenshot 1


:raw-html-m2r:`<img src="dbnet.screenshot.schema.png" alt="Screenshot schema" width="300"/>`

Development
===========

Install Vue & Dependencies
--------------------------

.. code-block:: bash

   npm install -g @vue/cli @vue/cli-service @vue/cli-plugin-babel @vue/cli-plugin-eslint
   git clone https://github.com/flarco/dbnet.git
   cd dbnet/frontend
   npm install

Building
--------

.. code-block:: bash

   git clone https://github.com/flarco/dbnet.git
   cd dbnet
   bash build.sh

Release
-------


* Update version in `setup.py <./setup.py>`_.
* Draft new release on Github: https://github.com/flarco/dbnet/releases/new

.. code-block::

   git clone https://github.com/flarco/dbnet.git
   cd dbnet
   m2r --overwrite README.md
   python setup.py sdist && twine upload --skip-existing dist/*
