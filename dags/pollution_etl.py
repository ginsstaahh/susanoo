from airflow import DAG
from airflow.decorators import task
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.providers.http.operators.http import HttpOperator
from datetime import datetime, timedelta
from helpers.google import drive_service, upload_image
from helpers.graphing import Plotly
from helpers.session import session, engine
import json
import os
import pandas as pd
from sqlalchemy import text
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

with DAG(f'pollution_etl',
        default_args=default_args,
        schedule_interval='@hourly',
        catchup=False
) as dag:
    
    for location in locations:
        city = location['city']
        country = location['country']
        longitude = location['longitude']
        latitude = location['latitude']

        city_codename = city.replace(' ', '_').lower()

        extract_data = HttpOperator(
            task_id=f'get_{city_codename}_pollution_data',
            http_conn_id='openweather_conn',
            endpoint=f'data/{openweather_version}/air_pollution?lat={latitude}&lon={longitude}&appid={openweather_api_key}',
            method='GET',
            response_filter=lambda response: json.loads(response.text),
        )

        transform_and_load_data = PythonOperator(
            task_id=f'transform_{city_codename}_pollution_data',
            python_callable=transform_pollution_data,
            op_kwargs = {'city': city, 'country': country}
        )

        extract_data >> transform_and_load_data


with DAG('upload_pollution_graphs',
    default_args=default_args,
    schedule='@daily',
    catchup=False
) as dag:

    start_tasks = DummyOperator(task_id='start_tasks')

    @task
    def graph_daily_pollution(**kwargs):
        ds = kwargs['ds']

        select_day = f'SELECT * FROM pollution WHERE DATE(time) BETWEEN {ds} AND {ds}'

        query = text(select_day)
        df = pd.read_sql(query, engine)

        for location in locations:
            city = location['city']
            Plotly.graph_aqi(df, ds, city)

    drive_directory_ids = {
        'aqi' : '1eLb-Ie1np2Rhqht5dCRGMuqXhso_NZ-M'
    }

    @task
    def upload_daily_images(**kwargs):
        ds = kwargs['ds']
        for location in locations:
            city = location['city']

            print(f'File ID: {file_id}')
            file_id = upload_image(drive_directory_ids['aqi'],
                                   filepath=f'graphs/{city}-aqi-{ds}.png',
                                   filename=f'{city}-aqi-{ds}.png')
            print(f'File ID: {file_id}')

start_tasks