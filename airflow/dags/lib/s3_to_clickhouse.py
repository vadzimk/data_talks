import logging
import os
from tempfile import TemporaryDirectory
from time import time
from typing import List

import pandas as pd
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from clickhouse_driver import Client


def insert_chunk(*, client, database_name, table_name, df):
    client.insert_dataframe(
        f"""INSERT INTO {database_name}."{table_name}" VALUES""",
        df,
        settings=dict(use_numpy=True),
    )


def csv_to_sql(*, filenames: List[str], s3_hook: S3Hook, bucket_name: str, stmt_create_table: str, ch_hook: Client,
               database_name: str, table_name: str,
               conversion_function: callable = lambda x: x):
    # download file into temporary directory
    with TemporaryDirectory() as temp_dir_name:
        for filename in filenames:
            s3_file_key = filename
            logging.info(f"{s3_file_key} Created temp dir")
            downloaded_filename = s3_hook.download_file(key=s3_file_key,
                                                        bucket_name=bucket_name,
                                                        local_path=temp_dir_name,
                                                        preserve_file_name=True,
                                                        use_autogenerated_subdir=False,
                                                        )
            logging.info(f"{s3_file_key} Written temp file {downloaded_filename}")
            file_path = os.path.join(temp_dir_name, downloaded_filename)
            CHUNK_SIZE = 100_000
            df_iter = pd.read_csv(file_path, iterator=True, chunksize=CHUNK_SIZE, dtype=str,
                                  escapechar="\\")  # chunksize is number of rows
            df = next(df_iter)
            df = conversion_function(df)
            client: Client = ch_hook.get_conn()
            client.execute("SET max_partitions_per_insert_block = 1000;")
            # https://stackoverflow.com/questions/31071952/generate-sql-statements-from-a-pandas-dataframe

            logging.info(f"Executing stmt_create_table: {stmt_create_table}")
            client.execute(stmt_create_table)
            logging.info(f"{s3_file_key} Created database table {table_name}")
            start_t = time()
            # https://stackoverflow.com/questions/58422110/pandas-how-to-insert-dataframe-into-clickhouse
            insert_chunk(client=client, database_name=database_name, table_name=table_name, df=df)
            end_t = time()
            logging.info(f"The first {CHUNK_SIZE} rows took {end_t - start_t}s to insert")
            chunk_count = 1
            while True:
                try:
                    df = next(df_iter)
                    df = conversion_function(df)
                    insert_chunk(client=client, database_name=database_name, table_name=table_name, df=df)
                    chunk_count += 1
                except StopIteration:
                    logging.info(f"{s3_file_key} completed insertion into {table_name}")
                    break
                except pd.errors.ParserError as e:
                    logging.error(
                        f"Chunk number {chunk_count}: between row {CHUNK_SIZE * chunk_count} and row {CHUNK_SIZE * (chunk_count + 1)}")
                    raise e
