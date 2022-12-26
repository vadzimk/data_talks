import json
import logging
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.mongo.hooks.mongo import MongoHook

default_args = {
    "tags": ["demo", "mongo"]
}


def upload_to_mongo(ti):
    hook = MongoHook(conn_id='mongo_conn')
    client = hook.get_conn()
    db = client.firstDB
    first_collection = db.first_collection  # declares the collection
    logging.info(f"Connected to MongoDB - {client.server_info()}")
    # d = json.loads(context["result"]) # deserialize string into python object
    first_collection.insert_one({"test": "success"})


with DAG(dag_id="mongo_hook_v01",
         default_args=default_args,
         start_date=datetime.now(),
         schedule_interval="@once") as dag:
    task1 = PythonOperator(task_id="load_test_object", python_callable=upload_to_mongo)

