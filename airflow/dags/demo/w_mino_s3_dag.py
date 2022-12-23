from datetime import datetime, timedelta
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor  # waits for a key to be present in the s3 bucket
from airflow import DAG

default_args = {
    "tags": ["demo"]
}

with DAG(dag_id="dag_w_s3_minio_v03", default_args=default_args,
         start_date=datetime.now(), schedule_interval="@daily", catchup=False) as dag:

    task1 = S3KeySensor(task_id="sensor_minio_s3",
                        aws_conn_id="s3_minio_conn",
                        bucket_name="airflow", bucket_key="data.csv",
                        poke_interval=5, # secs
                        timeout=30)
