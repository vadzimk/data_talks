from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    "tags": ["demo"]
}

with DAG(dag_id="dag_with_catchup_and_backfill_v03", default_args=default_args,
         start_date=datetime.now()-timedelta(hours=3), schedule_interval="@hourly",
         catchup=False  # by default is True and will execute missed times from the start_date till now
         ) as dag:
    task1 = BashOperator(task_id="task1", bash_command="echo this is a simple bash command")


# docker exec -it <scheduler> bash
# airflow dags backfill -s <start_date> -e <end_date> <dag_id>  # allows to execute missed times from the past