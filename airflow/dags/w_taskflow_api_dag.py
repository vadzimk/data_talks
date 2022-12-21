from datetime import timedelta, datetime
from airflow.decorators import dag, task

default_args = {
    'owner': 'airflow',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}


@dag(dag_id="dag_with_taskflow_api_v3", default_args=default_args, start_date=datetime.now(), schedule_interval="@once")
def hello_etl():
    @task
    def get_name():
        return "Gypsy"

    @task
    def get_address():
        return {"number": 1, "street": "North Pole"}

    @task
    def greet(name, address):
        print(f"Hello, I am {name}, address: {address['number']} {address['street']}")

    greet(name=get_name(), address=get_address())


greet_dag = hello_etl()
