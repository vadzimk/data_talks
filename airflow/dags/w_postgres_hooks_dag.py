import csv
import logging
import os.path
from datetime import timedelta, datetime
from tempfile import NamedTemporaryFile
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
    conn_postgres = hook.get_conn()
    cursor = conn_postgres.cursor()
    cursor.execute("SELECT * FROM orders WHERE date > %s AND date <= %s", (ds_nodash, next_ds_nodash))

    with NamedTemporaryFile(mode="w", suffix=ds_nodash, delete=False) as temp_file:
        # temporary file is deleted by default on close
        # with open(file_path, "w") as f:
        with temp_file as f:  # closes the file at the end of block
            csv_writer = csv.writer(f)
            csv_writer.writerow([i[0]] for i in cursor.description)
            csv_writer.writerows(cursor)
            f.flush()
        cursor.close()
        conn_postgres.close()
        logging.info(f"Saved orders in temporary text file: {temp_file.name}")

        # upload file to s3
        s3_hook = S3Hook(aws_conn_id="s3_minio_conn")  # id from airflow_setup.py
        filename = f"get_orders_{ds_nodash}.txt"
        logging.info(f"{temp_file.name} {'' if os.path.isfile(temp_file.name) else 'not'} exist")
        s3_hook.load_file(filename=temp_file.name, key=filename, bucket_name="airflow", replace=True)
        try:
            os.remove(temp_file.name)
        except OSError:
            pass


with DAG(dag_id="dag_w_postgres_hooks_v13", default_args=default_args,
         start_date=datetime.now(), schedule_interval="@daily") as dag:
    task1 = PythonOperator(task_id="postgres_to_s3", python_callable=postgres_to_s3)
