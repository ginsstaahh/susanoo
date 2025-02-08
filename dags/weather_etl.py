from airflow import DAG
from airflow.providers.http.operators.http import HttpOperator
from airflow.providers.amazon.aws.transfers.local_to_s3 import LocalFilesystemToS3Operator
from airflow.operators.python_operator import PythonOperator
from datetime import date, datetime, timedelta
import json
import os
from helpers.transformations import transform_weather_data

openweather_api_key = os.environ.get('OPENWEATHER_API_KEY')
openweather_version = '2.5'
city, province, country = 'Vancouver', 'BC', 'CA'

default_args = {
    'owner': 'ginsstaahh',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 0,
    'retry_delay': timedelta(minutes=1),
    'iam_user': '',
}

with DAG('weather_etl_dag',
        default_args=default_args,
        schedule_interval=timedelta(minutes=15),
        catchup=False
) as dag:

    get_weather_data = HttpOperator(
        task_id='get_weather_data',
        http_conn_id='openweather_conn',
        endpoint=f'data/{openweather_version}/weather?q={city},{province},{country}&appid={openweather_api_key}',
        method='GET',
        response_filter=lambda response: json.loads(response.text),
    )

    transform_weather_data = PythonOperator(
        task_id='transform_weather_data',
        python_callable=transform_weather_data,
    )

get_weather_data >> transform_weather_data


with DAG('upload_weather_data_dag',
        default_args=default_args,
        schedule='@daily',
        catchup=False
) as dag:

    current_date = (date.today()).strftime('%Y-%m-%d')
    upload_weather_data = LocalFilesystemToS3Operator(
        task_id='upload_weather_data',
        filename=f'weather/vancouver-weather-{current_date}.json',
        dest_key=f'vancouver-weather-{current_date}.json',
        dest_bucket='susanoo-weather',
        aws_conn_id='aws_default',
        replace=True,
    )

upload_weather_data