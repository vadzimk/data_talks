from datetime import timedelta, datetime

from airflow import DAG
from airflow_clickhouse_plugin.operators.clickhouse_operator import ClickHouseOperator

clickhouse_connection = {
    "clickhouse_conn_id": "clickhouse_conn"
}

default_args = {
    "owner": "airflow",
    "retires": 5,
    "retry_delay": timedelta(minutes=5),
    "tags": ["demo", "clickhouse"]
}

with DAG(dag_id="w_clickhouse_operator_v05", default_args=default_args,
         start_date=datetime.now(), schedule_interval="@once", catchup=False) as dag:
    task1 = ClickHouseOperator(task_id="create_test_db",
                               **clickhouse_connection,
                               sql="""
                              CREATE DATABASE IF NOT EXISTS test;
                              """)
    task2 = ClickHouseOperator(task_id="create_table",
                               **clickhouse_connection,
                               database="test",
                               sql="""
                               CREATE TABLE IF NOT EXISTS Dag_runs (
                                    dt date,
                                    dag_id varchar,
                                    PRIMARY KEY (dt, dag_id)
                             ) ENGINE = MergeTree;
                               """)

    task5 = ClickHouseOperator(task_id="insert_into_table",
                             **clickhouse_connection,
                               database="test",
                               sql="""
                             INSERT INTO Dag_runs (dt, dag_id) VALUES 
                             ('{{ ds }}', '{{ dag.dag_id }}')
                             """)

    task1 >> task2 >> task5