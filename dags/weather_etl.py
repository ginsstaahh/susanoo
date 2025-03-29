from airflow import DAG
from airflow.decorators import task
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.providers.http.operators.http import HttpOperator
from datetime import datetime, timedelta
from helpers.transformations import transform_weather_data
from helpers.google import drive_service, upload_image
from helpers.graphing import Plotly
from helpers.session import session, engine
import json
import os
import pandas as pd
from sqlalchemy import text

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


with DAG('weather_etl',
        default_args=default_args,
        schedule_interval=timedelta(minutes=15),
        catchup=False
) as dag:

    for location in locations:
        city = location['city']
        country = location['country']
        city_codename = city.replace(' ', '_').lower()

        extract_data = HttpOperator(
            task_id=f'get_{city_codename}_weather_data',
            http_conn_id='openweather_conn',
            endpoint=f'data/{openweather_version}/weather?q={city},{country}&appid={openweather_api_key}',
            method='GET',
            response_filter=lambda response: json.loads(response.text),
        )

        transform_data = PythonOperator(
            task_id=f'transform_{city_codename}_weather_data',
            python_callable=transform_weather_data,
        )

        extract_data >> transform_data


with DAG('upload_weather_graphs',
    default_args=default_args,
    schedule='@daily',
    catchup=False
) as dag:

    start_tasks = DummyOperator(task_id='start_tasks')

    @task
    def graph_daily_weather(**kwargs):
        ds = kwargs['ds']

        select_day = f'SELECT * FROM weather WHERE DATE(time) BETWEEN {ds} AND {ds}'
        select_all = "SELECT * FROM weather"

        query = text(select_all)
        df = pd.read_sql(query, engine)

        for location in locations:
            city = location['city']
            Plotly.graph_temperature(df, ds, city)
            Plotly.graph_humidity(df, ds, city)
    

    drive_directory_ids = {
        'temperature' : '1cCcWsGyDKelB2Ir6fALfthoudTLSBTDr',
        'humidity' : '1D5QTP7pWTsqHWXe-WFBkpwRknxeJY-r1',
    }

    @task
    def upload_daily_images(**kwargs):
        ds = kwargs['ds']
        for location in locations:
            city = location['city']

            print(f'Uploading daily images for {city} to Google Drive')
            file_id = upload_image(drive_directory_ids['temperature'],
                                   filepath=f'graphs/{city}-temperature-{ds}.png',
                                   filename=f'{city}-temperature-{ds}.png')
            print(f'File ID: {file_id}')
            file_id = upload_image(drive_directory_ids['humidity'],
                                   filepath=f'graphs/{city}-humidity-{ds}.png',
                                   filename=f'{city}-humidity-{ds}.png')
            print(f'File ID: {file_id}')

start_tasks