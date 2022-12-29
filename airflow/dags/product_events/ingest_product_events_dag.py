from datetime import timedelta, datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow_clickhouse_plugin.hooks.clickhouse_hook import ClickHouseHook
from airflow_clickhouse_plugin.operators.clickhouse_operator import ClickHouseOperator
from lib.s3_to_clickhouse import csv_to_sql  # relative to the dags directory

clickhouse_connection = {
    "clickhouse_conn_id": "clickhouse_conn"
}

default_args = {
    "owner": "airflow",
    "retires": 5,
    "retry_delay": timedelta(minutes=5),
    "tags": ["project", "clickhouse"]
}

database_name = "product_events"
table_name = "Events"
bucket_name = "product-events"
filenames = ["2019-Nov.csv", "2019-Oct.csv"]

s3_hook = S3Hook(aws_conn_id="s3_minio_conn")
ch_hook = ClickHouseHook(**clickhouse_connection)

stmt_create_table = f"""
CREATE TABLE IF NOT EXISTS {database_name}."{table_name}" (
"event_time" DateTime('GMT'),
"event_type" TEXT,
"product_id" UInt32, 
"category_id" UInt32,
"category_code" TEXT,
"brand" TEXT,
"price" REAL,
"user_id" UInt64,
"user_session" TEXT
) 
ENGINE = MergeTree 
ORDER BY "event_time"
PARTITION BY "category_id";
"""

def conversion_function(df):
    df['event_time'] = df['event_time'].apply(lambda d: d[:-4])  # removes " UTC"
    return df

def ingest_product_events():
    csv_to_sql(filenames=filenames,
               s3_hook=s3_hook,
               bucket_name=bucket_name,
               stmt_create_table=stmt_create_table,
               ch_hook=ch_hook,
               database_name=database_name,
               table_name=table_name,
               conversion_function=conversion_function)


with DAG(dag_id="product_events_to_clickhouse_v06", default_args=default_args,
         start_date=datetime.now(), schedule_interval="@once", catchup=False) as dag:
    sense_s3_file_add = S3KeySensor(task_id="sensor_minio_s3",
                                    aws_conn_id="s3_minio_conn",
                                    bucket_name=bucket_name,
                                    bucket_key=filenames,
                                    poke_interval=5,  # secs
                                    timeout=10 * 60)

    create_ch_database = ClickHouseOperator(task_id="create_companies_db",
                                            **clickhouse_connection,
                                            sql=f"""
                              CREATE DATABASE IF NOT EXISTS {database_name};
                              """)

    mv_csv_to_ch_table = PythonOperator(task_id="ingest_product_events", python_callable=ingest_product_events)

    sense_s3_file_add >> create_ch_database >> mv_csv_to_ch_table
