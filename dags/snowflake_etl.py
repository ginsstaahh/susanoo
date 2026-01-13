from airflow import DAG
from airflow.decorators import task
from datetime import datetime
from helpers.session import engine
import os
import pandas as pd
import snowflake.connector as snow
from snowflake.connector.pandas_tools import write_pandas


default_args = {
    'owner': 'ginsstaahh',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 0,
}

with DAG(
    dag_id='postgres_to_snowflake_etl',
    default_args=default_args,
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False,
) as dag:

    @task
    def postgres_to_snowflake(**kwargs):
        tablename = kwargs['table']
        engine = kwargs['engine']
        data = pd.read_sql(tablename, engine)

        conn = snow.connect(
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            warehouse="SUSANOO",
            database="SUSANOO",
            schema="PUBLIC"
        )
        write_pandas(conn, data, tablename, auto_create_table=True)
        conn.close()

    postgres_to_snowflake(table='weather', engine=engine)
    postgres_to_snowflake(table='pollution', engine=engine)
    postgres_to_snowflake(table='cities', engine=engine)