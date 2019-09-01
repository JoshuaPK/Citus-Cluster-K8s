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

WORKER_LIST_FILE = '/etc/citus/cluster-nodes-data/pg_worker_list_conf'
MASTER_HOST_FILE = '/etc/citus/cluster-nodes-data/MASTER_HOSTNAME'
MEMBER_MANAGER_HOST_FILE = '/etc/citus/cluster-nodes-data/MEMBER_MANAGER_HOSTNAME'

LOCAL_HOSTNAME = os.environ['HOSTNAME']
MQTT_HOST = LOCAL_HOSTNAME
MASTER_HOSTNAME = open(MASTER_HOST_FILE, 'r').read()

DEBUG = True
MQTT_CONN = None


def debugPrint(stringToPrint):

    global DEBUG

    if (DEBUG == True):
        print(stringToPrint)

debugPrint("Loading Worker Registration Listener")

def registerMemberManager():

    global LOCAL_HOSTNAME, MEMBER_MANAGER_HOST_FILE
    open(MEMBER_MANAGER_HOST_FILE, 'w').write(LOCAL_HOSTNAME)
    debugPrint('Registered Member Manager Host ' + LOCAL_HOSTNAME)

    pass

def addHostToList(hostname):

    global WORKER_LIST_FILE, MASTER_HOSTNAME

    f = open(WORKER_LIST_FILE, 'r+')
    fc = f.read()

    if (hostname not in fc):
        f.seek(0, 2)
        f.write(hostname + '\n')

    dbc = psycopg2.connect("dbname='postgres' user='postgres' host='" + MASTER_HOSTNAME + "'")
    cur = dbc.cursor()
    cur.execute("SELECT master_initialize_node_metadata();")
    dbc.close()

    debugPrint('Added worker host ' + hostname)

    pass

def registerHost(client, userdata, message):

    locHostname = message
    debugPrint('Registering Host: ' + locHostname)
    addHostToList(locHostname)
    

    pass

def removeHost(client, userdata, message):


    pass


def connectMQTT():

    global MQTT_CONN, LOCAL_HOSTNAME

    MQTT_CONN = mqtt.Client(LOCAL_HOSTNAME)
    MQTT_CONN.connect(LOCAL_HOSTNAME)
    MQTT_CONN.loop_start()
    MQTT_CONN.subscribe('hosts/workers/add',qos=2)
    MQTT_CONN.subscribe('hosts/workers/remove',qos=2)
    MQTT_CONN.message_callback_add('hosts/workers/add', registerHost)
    MQTT_CONN.message_callback_add('hosts/workers/remove', removeHost)
    MQTT_CONN.loop_forever()

if __name__ == '__main__':

    debugPrint('Starting worker registration listener')
    registerMemberManager()
    connectMQTT()

