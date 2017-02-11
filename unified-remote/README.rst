============================
AlarMe Unified Remote remote
============================

Simple state control remote for `Unified Remote <https://www.unifiedremote.com/>`_ software

Overview
========

This remote provides control adapted for following 6 states:

* Start
* Disabled
* Pass
* Stay
* Guard
* Alarm

More detailed info about these states can be found in config examples.
Of course you can change this remote's controls according to your AlarMe config.

Features
========

* Show current state
* Change state

Prerequisites
=============

This remote uses AlarMe API that is provided using `web` sensor.
So to use this remote you need AlarMe server running with `web` sensor enabled.

Install
=======

Copy this folder into your remotes folder for Unified Remote server.
More info at `Official Tutorial <https://www.unifiedremote.com/tutorials/how-to-install-a-custom-remote>`_.

Config
======

After install you need to set up access details to your AlarMe server in remote configuration page.
Settings fields are:

* `url` - AlarMe server url. Default: `http://127.0.0.1:8000`
* `login` - AlarMe web sensor login. Default: `admin`
* `password` - AlarMe web sensor password. Default: `admin`
