from airflow import DAG
from airflow.decorators import task
from airflow.providers.http.operators.http import HttpOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import json
import os
from helpers.transformations import transform_city_data
from helpers.google import sheets_service

openweather_api_key = os.environ.get('OPENWEATHER_API_KEY')
openweather_version = '2.5'
city, province, country = 'San Francisco', 'CA', 'US'

default_args = {
    'owner': 'ginsstaahh',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 0,
    'retry_delay': timedelta(minutes=1),
}

with DAG('city_etl',
        default_args=default_args,
        schedule_interval=None,
        catchup=False
) as dag:

    get_city_data = HttpOperator(
        task_id='get_city_data',
        http_conn_id='openweather_conn',
        endpoint=f'data/{openweather_version}/weather?q={city},{province},{country}&appid={openweather_api_key}',
        method='GET',
        response_filter=lambda response: json.loads(response.text),
    )

    transform_data = PythonOperator(
        task_id='transform_city_data',
        python_callable=transform_city_data,
    )

    @task
    def load_to_snowflake(**kwargs):
        pass

get_city_data >> transform_data >> load_to_snowflake()