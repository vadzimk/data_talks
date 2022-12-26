#!/usr/bin/env python
# Creates connections to data storage

from airflow.models import Connection
from airflow.utils.session import provide_session
import os


def drop_all_connections(session):
    connections = session.query(Connection).all()
    for conn in connections:
        session.delete(conn)
    session.commit()


def create_connections(session):
    mongo_conn = Connection(
        conn_id=f"mongo_conn",
        conn_type="mongo",
        host=os.environ.get('MONGO_HOST'),
        port=os.environ.get('MONGO_PORT'), # srv cannot have port in url string InvalidURI("%s URIs must not include a port number" % (SRV_SCHEME,))
        login=os.environ.get('MONGO_INITDB_ROOT_USERNAME'),
        password=os.environ.get('MONGO_INITDB_ROOT_PASSWORD'),
        schema="admin",  # authentication database, without it will not authenticate
        # extra={"srv": True}
    )
    clickhouse_conn = Connection(
        conn_id=f"clickhouse_conn",
        conn_type="clickhouse",
        host=os.environ.get('CLICKHOUSE_HOST'),
        port=os.environ.get('CLICKHOUSE_PORT'),
        # schema=  # optional
        login=os.environ.get('CLICKHOUSE_USER'),
        password=os.environ.get('CLICKHOUSE_PASSWORD')
    )
    postgres_test_db_conn = Connection(
        conn_id=f'postgres_test_db_conn',
        conn_type='postgres',
        host='data-talks-postgres',  # container name of postgres
        port=5432,
        login=os.environ.get('POSTGRES_USER'),
        password=os.environ.get('POSTGRES_PASSWORD'),
        schema='test',  # Maps to Database in Postgres
    )

    s3_minio_conn = Connection(
        conn_id="s3_minio_conn",
        conn_type="aws",
        login=os.environ.get('MINIO_ROOT_USER'),  # Reference to AWS Access Key ID
        password=os.environ.get('MINIO_ROOT_PASSWORD'),  # Reference to AWS Secret Access Key
        extra={
            # Specify extra parameters here
            # "region_name": "eu-central-1",
            "endpoint_url": "http://data-talks-minio:9000",  # host:port
        },
    )

    # --------- Optional ----------
    # Generate Environment Variable Name and Connection URI
    env_key = f"AIRFLOW_CONN_{s3_minio_conn.conn_id.upper()}"
    conn_uri = s3_minio_conn.get_uri()
    print(f"{env_key}={conn_uri}")
    # AIRFLOW_CONN_SAMPLE_AWS_CONNECTION=aws://AKIAIOSFODNN7EXAMPLE:wJalrXUtnFEMI%2FK7MDENG%2FbPxRfiCYEXAMPLEKEY@/?region_name=eu-central-1

    # Test connection
    os.environ[env_key] = conn_uri
    print(s3_minio_conn.test_connection())
    # ---------- End Optional ------

    session.add_all([
        postgres_test_db_conn,
        s3_minio_conn,
        clickhouse_conn,
        mongo_conn
    ])
    session.commit()


@provide_session
def setup_airflow(session=None):
    drop_all_connections(session)
    print("-------- CREATING CONNECTIONS ---------")
    create_connections(session)


if __name__ == '__main__':
    setup_airflow()
