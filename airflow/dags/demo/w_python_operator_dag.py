from datetime import timedelta, datetime

from airflow import DAG
from airflow.operators.python import PythonOperator


def greet_one(name):
    print(f"Hello from {name} python operator")


def greet_two(ti):
    """ :param ti: The task instance"""
    name = ti.xcom_pull(task_ids='get_name')  # task_ids parameter specifies from which task to pull the return value
    number = ti.xcom_pull(task_ids='get_address', key="number")
    street = ti.xcom_pull(task_ids='get_address', key="street")
    print(f"Hello from {name} python operator")
    print(f"My address is {number} {street}")


def get_name():
    return "Frog"  # by default every task return value will be pushed to XCom, max size of it is only 48 KBytes, so it is not suitable for dataframes


def get_address(ti):
    ti.xcom_push(key="number", value="1")
    ti.xcom_push(key="street", value="North Pole")


default_args = {
    'owner': 'airflow',
    'retries': 5,
    'retry_delay': timedelta(minutes=5),
    "tags": ["demo"]

}

with DAG(dag_id="dag_with_python_operator_v5",
         default_args=default_args, description="first dag with python operator",
         start_date=datetime.now(), schedule_interval="@once"):
    task0 = PythonOperator(task_id="greet_task", python_callable=greet_one, op_kwargs={'name': 'Gypsy'})
    task1 = PythonOperator(task_id="get_name", python_callable=get_name)
    task2 = PythonOperator(task_id="get_address", python_callable=get_address)
    task3 = PythonOperator(task_id="greet_task_using_return_value", python_callable=greet_two)

    [task1, task2] >> task3
