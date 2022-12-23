from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    "tags": ["demo"]
}

with DAG(dag_id="first_dag_v4", default_args=default_args, start_date=datetime.now(), schedule_interval="@once") as dag:
    task1 = BashOperator(task_id="first_task", bash_command="echo 'hello world'")
    task2 = BashOperator(task_id="second_task", bash_command="echo 'hello from 2nd task'")
    task3 = BashOperator(task_id="third_task", bash_command="echo 'hello from 3d task'")
    # task1.set_downstream([task3, task2])
    task1 >> [task3, task2]