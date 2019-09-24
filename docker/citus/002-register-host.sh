#!/usr/bin/env bash

# make bash behave
set -euo pipefail
IFS=$'\n\t'

# Only do this if we are a worker

LONGHOST=`hostname -f`

echo Registering Node $LONGHOST

if [[ $LONGHOST =~ "citus-master" ]]
then
#  echo -n $LONGHOST > /etc/citus/cluster-nodes-data/MASTER_HOSTNAME
  echo Registered Master Node $LONGHOST
else
  if [[ $LONGHOST =~ "citus-worker" ]]
  then
    echo Registering Worker Node
    # Run script that connects to MQTT here
    #MQTT_HOST=`cat /etc/citus/cluster-nodes-data/MASTER_HOSTNAME`
    MQTT_HOST='citus-master-service.citus-cluster.svc.cluster.local'
    echo MQTT broker lives at $MQTT_HOST
    mosquitto_pub -h $MQTT_HOST -m $LONGHOST -t hosts/workers/add
    echo Host registration procedure complete
  fi
fi

