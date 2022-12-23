import csv
import logging
from datetime import timedelta, datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.postgres.hooks.postgres import PostgresHook

default_args = {
    "owner": "airflow",
    "retries": 5,
    "retry_delay": timedelta(minutes=5),
}


def postgres_to_s3(ds_nodash, next_ds_nodash):
    """
    1. query postgres and save result into text file
    2. upload text file to s3
    :param ds_nodash: datestamp macros https://airflow.apache.org/docs/apache-airflow/stable/templates-ref.html#macros
    :param next_ds_nodash: next execution datestamp
    :return: None
    """
    hook = PostgresHook(postgres_conn_id="postgres_test_db_conn")
    conn = hook.get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE date > %s AND date <= %s", (ds_nodash, next_ds_nodash))
    filename = f"get_orders_{ds_nodash}.txt"
    file_path = f"tmp/{filename}"
    with open(file_path, "w") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow([i[0]] for i in cursor.description)
        csv_writer.writerows(cursor)
    cursor.close()
    conn.close()
    logging.info(f"Saved orders in text file: {filename}")

    # upload file to s3
    s3_hook = S3Hook(aws_conn_id="s3_minio_conn")  # id from airflow_setup.py
    s3_hook.load_file(filename=file_path, key=filename, bucket_name="airflow", replace=True)


with DAG(dag_id="dag_w_postgres_hooks_v07", default_args=default_args,
         start_date=datetime.now(), schedule_interval="@daily") as dag:
    task1 = PythonOperator(task_id="postgres_to_s3", python_callable=postgres_to_s3)
