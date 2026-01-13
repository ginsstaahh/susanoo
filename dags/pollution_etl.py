from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.http.operators.http import HttpOperator
from datetime import datetime
import json
import os
from helpers.transformations import transform_pollution_data

openweather_api_key = os.environ.get('OPENWEATHER_API_KEY')
openweather_version = '2.5'
locations = [
    {"city": "Vancouver", "country": "CA", "longitude": -123.1193, "latitude": 49.2497},
    {"city": "Seattle", "country": "US", "longitude": -122.3321, "latitude": 47.6062},
    {"city": "Los Angeles", "country": "US", "longitude": -118.2437, "latitude": 34.0522},
    {"city": "San Francisco", "country": "US", "longitude": -122.4194, "latitude": 37.7749}
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
    longitude = location['longitude']
    latitude = location['latitude']

    city_codename = city.replace(' ', '_').lower() # DAG names cannot have spaces
    with DAG(f'{city_codename}_pollution_etl',
            default_args=default_args,
            schedule_interval='@hourly',
            catchup=False
    ) as dag:

        extract_data = HttpOperator(
            task_id=f'get_pollution_data',
            http_conn_id='openweather_conn',
            endpoint=f'data/{openweather_version}/air_pollution?lat={latitude}&lon={longitude}&appid={openweather_api_key}',
            method='GET',
            response_filter=lambda response: json.loads(response.text),
        )

        transform_and_load_data = PythonOperator(
            task_id=f'transform_pollution_data',
            python_callable=transform_pollution_data,
            op_kwargs = {'city': city, 'country': country}
        )

        extract_data >> transform_and_load_data