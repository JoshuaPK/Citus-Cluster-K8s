#!/usr/bin/env bash

# make bash behave
set -euo pipefail
IFS=$'\n\t'

# Need to insert here: if this is the master, don't do this

if [[ $HOSTNAME =~ "worker" ]]
then
  flock /etc/citus/pg_worker_list.conf
  echo $HOSTNAME >> /etc/citus/pg_worker_list.conf
  flock -u /etc/citus/pg_worker_list.conf
fi

