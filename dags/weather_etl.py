from airflow import DAG
from airflow.decorators import task
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.providers.http.operators.http import HttpOperator
import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
import json
import os
import pendulum
from helpers.transformations import transform_weather_data

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
    
    city_dag_name = city.replace(' ', '_').lower()
    with DAG(f'{city_dag_name}_weather_etl_dag',
            default_args=default_args,
            schedule_interval=timedelta(minutes=15),
            catchup=False
    ) as dag:
        
        extract_data = HttpOperator(
            task_id='get_weather_data',
            http_conn_id='openweather_conn',
            endpoint=f'data/{openweather_version}/weather?q={city},{country}&appid={openweather_api_key}',
            method='GET',
            response_filter=lambda response: json.loads(response.text),
        )

        transform_data = PythonOperator(
            task_id='transform_weather_data',
            python_callable=transform_weather_data,
        )

    extract_data >> transform_data


with DAG('upload_weather_data_dag',
    default_args=default_args,
    schedule='@daily',
    start_date=pendulum.datetime(2025, 2, 9, tz='local'),
    catchup=True
) as dag:

    start_tasks = DummyOperator(task_id='start_tasks')

    @task
    def check_file_exists(**kwargs):
        ds = kwargs['ds']
        filename = f'weather-{ds}.json'

        if os.path.exists(f'weather/{filename}'):
            print('The weather file exists')
            return True
        else:
            return False

    @task.branch
    def skip_run(file_exists):
        if file_exists:
            return ['clean_data']
        else:
            return ['end_tasks']

    # create a temporary file to work with before replacing the working file.  This needs to be done for a sort command
    clean_data = BashOperator(
        task_id='clean_data',
        bash_command='sort -u ~/Documents/susanoo/weather/weather-{{ ds }}.json > /tmp/weather-{{ ds }}.json && \
            mv /tmp/weather-{{ ds }}.json ~/Documents/susanoo/weather/weather-{{ ds }}.json'
    )

    @task
    def upload_data(**kwargs):
        ds = kwargs['ds']
        filename = f'weather-{ds}.json'

        s3_client = boto3.client('s3')
        try:
            s3_client.upload_file(f'weather/{filename}', 'susanoo-weather', filename)
        except ClientError as e:
            print(e)
            return False
        return True
    
    end_tasks = DummyOperator(task_id='end_tasks')

file_exists = check_file_exists()

start_tasks >> file_exists >> skip_run(file_exists) >> [clean_data, end_tasks]
clean_data >> upload_data() >> end_tasks