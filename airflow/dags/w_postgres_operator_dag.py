from datetime import timedelta, datetime

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator

default_args = {
    "owner": "airflow",
    "retires": 5,
    "retry_delay": timedelta(minutes=5)
}

with DAG(
        dag_id="dag_w_postgres_operator_v4", start_date=datetime.now(), schedule_interval="@once", catchup=False
) as dag:
    task1 = PostgresOperator(task_id="create_postgres_table",
                             postgres_conn_id="postgres_localhost",
                             # declared in airflow ui -> admin -> connections. schema is database name
                             sql="""
                             CREATE TABLE IF NOT EXISTS Dag_runs (
                                dt date,
                                dag_id varchar,
                                PRIMARY KEY (dt, dag_id)
                             );
                             """)
