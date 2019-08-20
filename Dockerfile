FROM postgres:11.4
ARG VERSION=8.3.0
LABEL maintainer="Citus Data https://citusdata.com" \
      org.label-schema.name="Citus" \
      org.label-schema.description="Scalable PostgreSQL for multi-tenant and real-time workloads" \
      org.label-schema.url="https://www.citusdata.com" \
      org.label-schema.vcs-url="https://github.com/citusdata/citus" \
      org.label-schema.vendor="Citus Data, Inc." \
      org.label-schema.version=${VERSION} \
      org.label-schema.schema-version="1.0"

ENV CITUS_VERSION ${VERSION}.citus-1

# install Citus
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ca-certificates \
       curl \
       lua5.3 \
       lua-filesystem \
       lua-posix \
    && curl -s https://install.citusdata.com/community/deb.sh | bash \
    && apt-get install -y postgresql-$PG_MAJOR-citus-8.3=$CITUS_VERSION \
                          postgresql-$PG_MAJOR-hll=2.12.citus-1 \
                          postgresql-$PG_MAJOR-topn=2.2.0 \
    && apt-get purge -y --auto-remove curl \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir /etc/citus \
    && mkdir /etc/citus/cluster-nodes-data \
    && touch /etc/citus/cluster-nodes-data/pg_worker_list.conf \
    && ln -s /etc/citus/cluster-nodes-data/pg_worker_list.conf /etc/citus/pg_worker_list.conf

# add citus to default PostgreSQL config
RUN echo "shared_preload_libraries='citus'" >> /usr/share/postgresql/postgresql.conf.sample

# add scripts to run after initdb
COPY 000-configure-stats.sh 001-create-citus-extension.sql 002-register-worker.sh /docker-entrypoint-initdb.d/
COPY test.lua /etc/

# add health check script
COPY pg_healthcheck /

# JPK TODO: REMEMBER TO ENABLE THIS AFTER UPGRADE OF DOCKER TO DOCKER-CE FROM DOCKER REPO
# HEALTHCHECK --interval=4s --start-period=6s CMD ./pg_healthcheck
