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

WORKER_LIST_FILE = '/etc/citus/cluster-nodes-data/pg_worker_list.conf'
MASTER_HOST_FILE = '/etc/citus/cluster-nodes-data/MASTER_HOSTNAME'

LOG_LOCATION = '/mnt/logs/'
log = None
LOG_LEVEL = logbook.DEBUG

MASTER_HOSTNAME = None
MQTT_HOST = None

DEBUG = True
MQTT_CONN = None

FNF_ERROR = getattr(__builtins__,'FileNotFoundError', IOError)

def setupLogging():

    global log, LOG_LOCATION, LOG_LEVEL

    log_path = LOG_LOCATION + os.environ['HOSTNAME'] + '/'

    if not os.path.exists(log_path):
        os.makedirs(log_path)

    log_filename = log_path + 'log.txt'

    log = logbook.Logger('Cluster Watcher')
    log.handlers.append(logbook.FileHandler(log_filename, bubble=False, mode='a'))
    #log.handlers.append(logbook.StreamHandler(sys.stdout))
    log.level = LOG_LEVEL

def getMasterHost():

    global MASTER_HOST_FILE, MASTER_HOSTNAME, MQTT_HOST, log

    warned = False

    while True:
        try:
            MASTER_HOSTNAME = open(MASTER_HOST_FILE, 'r').read()
            break
        except FNF_ERROR:
            log.warn('Master Hostname File Not Found, waiting for retry')
            time.sleep(1)
            warned = True
            continue

    if (warned == True):
        log.warn('Found hostname file')

    log.debug ('Set hostname to ' + MASTER_HOSTNAME)
    MQTT_HOST = MASTER_HOSTNAME

    pass

def addHostToList_Old(hostname):

    global WORKER_LIST_FILE, MASTER_HOSTNAME, log

    log.debug('Received request to add host ' + hostname)

    try:

        log.debug('Opening file ' + WORKER_LIST_FILE + ' to add host')
        f = open(WORKER_LIST_FILE, 'a+')
        fc = f.read()

        if (hostname not in fc):
            log.debug('Host ' + hostname + ' was not in the host file, adding it.')
            f.seek(0, 2)
            f.write(hostname + '\n')

    except Exception as E:
        log.error('Exception caught during add of host: ' + E.str())

    finally:
        f.close()

    log.debug('Calling the registration procedure on MASTER database node')

    try:
        dbc = psycopg2.connect("dbname='postgres' user='postgres' host='" + MASTER_HOSTNAME + "'")
        cur = dbc.cursor()
        cur.execute("SELECT master_initialize_node_metadata();")
        dbc.close()

    except Exception as E:
        log.error('Exception caught during execution of database query: ' + E.str())

    log.debug('Added worker host ' + hostname)

    pass


def addHostToList(hostname):

    log.debug('Calling the registration procedure on MASTER database node')

    try:
        dbc = psycopg2.connect("dbname='postgres' user='postgres' host='" + MASTER_HOSTNAME + "'")
        cur = dbc.cursor()
        cur.execute("SELECT master_add_node(%s, %s)", (hostname, 5432))
        #cur.execute("SELECT master_initialize_node_metadata();")
        dbc.commit()
        dbc.close()

    except Exception as E:
        log.error('Exception caught during execution of database query: ' + E.str())

    log.debug('Added worker host ' + hostname)

    pass

def registerHost(client, userdata, message):

    global log

    locHostname = message.payload
    log.debug('Registering Host: ' + locHostname)
    addHostToList(locHostname)
    

    pass

def removeHost(client, userdata, message):


    pass


def connectMQTT():

    global MQTT_CONN, LOCAL_HOSTNAME,  MASTER_HOSTNAME, log

    MQTT_HOST = MASTER_HOSTNAME

    log.info('Connecting to MQTT and registering callbacks')

    try:
        MQTT_CONN = mqtt.Client(MQTT_HOST)
        MQTT_CONN.connect(MQTT_HOST)
        MQTT_CONN.subscribe('hosts/workers/add',qos=2)
        MQTT_CONN.subscribe('hosts/workers/remove',qos=2)
        MQTT_CONN.message_callback_add('hosts/workers/add', registerHost)
        MQTT_CONN.message_callback_add('hosts/workers/remove', removeHost)

    except Exception as E:
        log.error('Caught exception connectiong to MQTT: ' + E.str())

    log.info('Calling MQTT loop_forever method')

    MQTT_CONN.loop_forever()

if __name__ == '__main__':

    setupLogging()
    log.info('Starting worker registration listener')
    getMasterHost()
    connectMQTT()

    log.debug('We should never get here: after the loop_forever() call')

