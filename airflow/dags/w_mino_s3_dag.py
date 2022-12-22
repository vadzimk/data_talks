from datetime import datetime, timedelta

from airflow.providers.amazon.aws.operators.s3 import S3CreateBucketOperator, S3CreateObjectOperator
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor  # waits for a key to be present in the s3 bucket
from airflow import DAG

default_args = {
    "owner": "airflow",
    "aws_conn_id": "s3_minio_conn",
}

with DAG(dag_id="dag_w_s3_minio_v02",
         start_date=datetime.now(), schedule_interval="@daily", catchup=False) as dag:

    task1 = S3KeySensor(task_id="sensor_minio_s3", default_args=default_args,
                        bucket_name="airflow", bucket_key="data.csv")
