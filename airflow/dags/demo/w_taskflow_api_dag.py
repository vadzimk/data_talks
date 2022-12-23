from datetime import timedelta, datetime
from airflow.decorators import dag, task

default_args = {
    'owner': 'airflow',
    'retries': 5,
    'retry_delay': timedelta(minutes=5),
    "tags": ["demo"]
}


@dag(dag_id="dag_with_taskflow_api_v4", default_args=default_args, start_date=datetime.now(), schedule_interval="@once")
def hello_etl():
    @task
    def get_name():
        return "Gypsy"

    @task(multiple_outputs=True)  # need multiple_outputs=True to pass the dict attributes separately to the
    # consuming task
    def get_address():
        return {"number": 1, "street": "North Pole"}

    @task
    def greet(name, number, street):
        print(f"Hello, I am {name}, address: {number} {street}")

    address_dict = get_address()
    greet(name=get_name(), number=address_dict['number'], street=address_dict['street'])


greet_dag = hello_etl()
