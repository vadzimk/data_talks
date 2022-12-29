ARG METABASE_VERSION="v0.45.1"
FROM metabase/metabase:${METABASE_VERSION}
# must be below from beause it creates a new build stage and previous is lost
ARG CLICKHOUSE_DRIVER_VERSION="0.9.1"
WORKDIR /
ADD "https://github.com/enqueue/metabase-clickhouse-driver/releases/download/${CLICKHOUSE_DRIVER_VERSION}/clickhouse.metabase-driver.jar" /plugins/
RUN chmod 744 /plugins/clickhouse.metabase-driver.jar