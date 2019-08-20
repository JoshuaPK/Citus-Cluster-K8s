#!/usr/bin/env bash

# make bash behave
set -euo pipefail
IFS=$'\n\t'

# Only do this if we are a worker

echo Registering Node $HOSTNAME

if [[ $HOSTNAME =~ "worker-blah" ]]
then
  if [ -f /etc/citus/cluster-nodes-data/pg_worker_list.conf ]
  then
    flock /etc/citus/cluster-nodes-data/pg_worker_list.conf
    echo $HOSTNAME >> /etc/citus/cluster-nodes-data/pg_worker_list.conf
    flock -u /etc/citus/cluster-nodes-data/pg_worker_list.conf
  else
    echo WARNING: pg_worker_list_conf file not found, exiting!
  fi
fi

