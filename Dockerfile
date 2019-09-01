FROM centos:7
ARG VERSION=8.3.0
LABEL maintainer="Joshua Kramer" \
      org.label-schema.name="Citus" \
      org.label-schema.description="Scalable PostgreSQL for multi-tenant and real-time workloads" \
      org.label-schema.url="https://www.citusdata.com" \
      org.label-schema.vcs-url="https://github.com/citusdata/citus" \
      org.label-schema.vendor="Citus Data, Inc." \
      org.label-schema.version=${VERSION} \
      org.label-schema.schema-version="1.0"

ENV CITUS_VERSION ${VERSION}.citus-1

# /etc/citus/cluster-nodes-data

RUN yum -y install https://download.postgresql.org/pub/repos/yum/reporpms/EL-7-x86_64/pgdg-redhat-repo-latest.noarch.rpm \
    && yum -y install postgresql11 \
    && yum -y install epel-release \
    && yum -y install mosquitto \
    && yum -y install python-paho-mqtt \
    && yum -y install python-psycopg2 \
    && yum -y install bind-utils \
    && yum -y install telnet \
    && yum -y install traceroute \
    && mkdir /etc/citus \
    && mkdir /etc/citus/cluster-nodes-data

COPY bootup.sh watcher.py /usr/local/bin/

ENTRYPOINT /usr/local/bin/bootup.sh

