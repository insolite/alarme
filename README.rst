======
AlarMe
======

Universal alarm system

Overview
========

Alarm system based on *states* (e. g. "stay", "guard", "alarm")
which can be controlled by *sensors* (e. g. "movement sensor")
and execute *actions* (e. g. "GSM call", "Email", "Siren")
using *schedules* (e. g. "after 5 seconds every minute 10 times").

Features
========

Essentials:
 * React for sensors
 * Change states
 * Follow schedule
 * Execute actions

Real stuff:
 * Make GSM calls
 * Send GSM SMS
 * Interact with 433MHz receiver/transmitter
 * Send E-mail
 * Control states using web page
 * Play sound

Usage
=====

.. code-block:: bash

    alarme -c my-config.yaml

Simplest config example
=======================

Coming soon

Install
=======

Install package:

.. code-block:: bash

    python3 setup.py install

Run tests (optionally):

.. code-block:: bash

    python3 -m unittest discover tests
