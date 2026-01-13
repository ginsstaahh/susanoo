from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.http.operators.http import HttpOperator
from datetime import datetime, timedelta
from helpers.transformations import transform_weather_data
import json
import os

openweather_api_key = os.environ.get('OPENWEATHER_API_KEY')
openweather_version = '2.5'
locations = [
    {'city': 'Vancouver', 'country': 'CA'},
    {"city": "Seattle", "country": "US"},
    {"city": "Los Angeles", "country": "US"},
    {"city": "San Francisco", "country": "US"}
]

default_args = {
    'owner': 'ginsstaahh',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 0,
}

for location in locations:
    city = location['city']
    country = location['country']

    city_codename = city.replace(' ', '_').lower() # DAG names cannot have spaces
    with DAG(f'{city_codename}_weather_etl',
            default_args=default_args,
            schedule_interval=timedelta(minutes=15),
            catchup=False
    ) as dag:

        extract_data = HttpOperator(
            task_id=f'get_weather_data',
            http_conn_id='openweather_conn',
            endpoint=f'data/{openweather_version}/weather?q={city},{country}&appid={openweather_api_key}',
            method='GET',
            response_filter=lambda response: json.loads(response.text),
        )

        transform_data = PythonOperator(
            task_id=f'transform_weather_data',
            python_callable=transform_weather_data,
        )

        extract_data >> transform_data