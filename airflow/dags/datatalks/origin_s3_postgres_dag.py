import logging
import os
import re
import time
from datetime import datetime
from tempfile import NamedTemporaryFile

import requests
from datatalks.scripts.TlcTripScraper import TlcTripScraper
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

default_args = {
    "tags": ["talks"]
}


def save_trip_files_to_s3(ti):
    links: list = ti.xcom_pull(task_ids='scrape_links_tlc')
    logging.info(f"Scrapped {len(links)} links")
    print("links[0]", links[0])
    s3_hook = S3Hook(aws_conn_id="s3_minio_conn")
    bucket_name = "yellow-taxi-trips"  # TODO auto create this bucket
    for link in links:
        filename = link.split("/")[-1]
        with requests.get(link) as r:
            r.raise_for_status()
            if "Content-Disposition" in r.headers.keys():
                filename = re.findall("filename=(.+)", r.headers["Content-Disposition"])[0]
            with NamedTemporaryFile(mode="wb", delete=False) as temp_file:
                logging.info(f"{filename} Opened empty file")
                with temp_file as f:  # closes the file
                    for chunk in r.iter_content(chunk_size=512):
                        f.write(chunk)
                    f.flush()
                    logging.info(f"{filename} Written temporary file")
            s3_hook.load_file(filename=temp_file.name, key=filename,
                              bucket_name=bucket_name,
                              replace=True)
            logging.info(f"{filename} Uploaded to {bucket_name}")
            try:  # deleting temporary file
                os.remove(temp_file.name)
                logging.info(f"{filename} Removed temporary file")
            except OSError:
                pass
            time.sleep(1)  # slow down


with DAG(dag_id="yellow_taxi_data_ingestion_v07", default_args=default_args,
         start_date=datetime.now(), schedule_interval="@once") as dag:
    task_scrape_links = PythonOperator(task_id="scrape_links_tlc", python_callable=TlcTripScraper.run)
    task_save_trip_files_to_s3 = PythonOperator(task_id="save_trip_files_to_s3", python_callable=save_trip_files_to_s3)

    task_scrape_links >> task_save_trip_files_to_s3
