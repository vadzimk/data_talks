[Ariflow tutorial](https://youtu.be/K9AnJ9_ZAXE)  
**Airflow web UI:** `localhost:8080 `  
username: `admin`  
password: `admin`  

Local environment dependencies installation:  
`pip install apache-airflow
apache-airflow-providers-postgres 
apache-airflow-providers-amazon 
selectolax pyarrow
airflow-clickhouse-plugin
clickhouse-sqlalchemy
pymongo[srv]
apache-airflow-providers-mongo
sudo pip install python-dotenv
`

install dependencies in the running container:
<pre><code>
docker exec -it data-talks-webserver bash -c "pip install {package}";
</code></pre>

establish new connections in a running container:
<pre><code>
docker exec -it data-talks-webserver bash -c "python scripts/airflow_setup.py";
</code></pre>


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
- The following command removes multiple objects from the mydata bucket on the myminio MinIO deployment: `mc rm --recursive --force myminio/mydata`
- debug Error tokenizing data Expected 10 fields in line 2684, saw 11 ```sed -n 1p free_company_dataset.csv >> test.csv && sed -n 26384,26385p free_company_dataset.csv >> test.csv```





