#!/bin/bash

echo Starting Mosquitto:
/usr/sbin/mosquitto -c /etc/mosquitto/mosquitto.conf -d


echo Starting Watcher Service:
/bin/python /usr/local/bin/watcher.py

echo We should never get here- why did the watcher crash?

