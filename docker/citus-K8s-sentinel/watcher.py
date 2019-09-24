#!/usr/bin/python

# This program runs on the member manager.  It:
#  1. Connects to local mqtt daemon to listen for incoming host registrations
#  2. Connects to Posgres instance on MASTER_HOST
#  3. On incoming subscritpion requests, it:
#     1. Writes the host to pg_worker_list.conf
#     2. Calls the Postgres function on master to re-read the reg list

import paho.mqtt.client as mqtt
import psycopg2
import os
import sys
import time
import logbook

MASTER_HOSTNAME = 'citus-master-service.citus-cluster.svc.cluster.local'

LOG_LOCATION = '/mnt/logs/'
log = None
LOG_LEVEL = logbook.DEBUG

FNF_ERROR = getattr(__builtins__,'FileNotFoundError', IOError)

def setupLogging(isStderr = True):

    global log, LOG_LOCATION, LOG_LEVEL

    log = logbook.Logger('Cluster Watcher')
    log.level = LOG_LEVEL

    if isStderr:
        log.handlers.append(logbook.StreamHandler(sys.stderr))

    else:
        log_path = LOG_LOCATION + os.environ['HOSTNAME'] + '/'
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        log_filename = log_path + 'log.txt'
        log.handlers.append(logbook.FileHandler(log_filename, bubble=False, mode='a'))


def addHostToList(hostname):

    log.debug('Calling the registration procedure on MASTER database node')

    try:
        dbc = psycopg2.connect("dbname='postgres' user='postgres' host='" + MASTER_HOSTNAME + "'")
        cur = dbc.cursor()
        cur.execute("SELECT master_add_node(%s, %s)", (hostname, 5432))
        dbc.commit()
        dbc.close()
    except Exception as E:
        log.error('Exception caught during execution of database query: ' + E.str())

    log.debug('Added worker host ' + hostname)


def registerHost(client, userdata, message):

    global log
    locHostname = message.payload
    log.debug('Registering Host: ' + locHostname)
    addHostToList(locHostname)


def connectMQTT():

    global MASTER_HOSTNAME, log

    MQTT_HOST = MASTER_HOSTNAME
    MQTT_CONN = mqtt.Client(MQTT_HOST)
    log.info('Connecting to MQTT and registering callbacks')

    for i in range(1, 33):
        try:
            MQTT_CONN.connect(MQTT_HOST)
            MQTT_CONN.subscribe('hosts/workers/add',qos=2)
            MQTT_CONN.message_callback_add('hosts/workers/add', registerHost)
            break;
        except Exception as E:
            log.error('Caught exception connectiong to MQTT: ' + str(E))
            time.sleep(3)

    log.info('Calling MQTT loop_forever method')

    MQTT_CONN.loop_forever()

if __name__ == '__main__':

    setupLogging()
    log.info('Starting worker registration listener')
    connectMQTT()

    log.debug('We should never get here: after the loop_forever() call')

