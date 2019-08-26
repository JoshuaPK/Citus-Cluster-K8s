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

MQTT_HOST = 'kubemaster'
WORKER_LIST_FILE = '/etc/citus/cluster-nodes-data/pg_worker_list_conf'
MASTER_HOST_FILE = '/etc/citus/cluster-nodes-data/MASTER_HOST'
MEMBER_MANAGER_HOST_FILE = '/etc/citus/cluster-nodes-data/MEMBER_MANAGER_HOST'
LOCAL_HOSTNAME = os.environ['HOSTNAME']

MQTT_CONN = None


def registerHost():


    pass

def removeHost():


    pass


def onMessage(client, userdata, message):


    pass

def connectMQTT():
    MQTT_CONN = mqtt.Client(LOCAL_HOSTNAME)
    MQTT_CONN.connect(LOCAL_HOSTNAME)
    MQTT_CONN.on_message = onMessage

def eventLoop():



    pass
