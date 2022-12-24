[Ariflow tutorial](https://youtu.be/K9AnJ9_ZAXE)  
**Airflow web UI:** `localhost:8080 `  
username: `admin`  
password: `admin`  

Local environment dependencies installation:  
`pip install apache-airflow
apache-airflow-providers-postgres 
apache-airflow-providers-amazon 
selectolax pyarrow
airflow-clickhouse-plugin`


**Minio web UI:**  `localhost:9090`
username, password — 
see environment variables:
`MINIO_ROOT_USER`  
`MINIO_ROOT_PASSWORD`
create a bucket `airflow`

### Notes
- connections are declared in `airflow/scripts/airflow_setup.py`,
you can use look up connection ids from that file to use them in DAGs
- [psycopg](https://www.psycopg.org/docs/) documentation for Python PostgreSQL database adapter
- [clickhouse](https://github.com/bryzgaloff/airflow-clickhouse-plugin) documentation for airflow plugin


