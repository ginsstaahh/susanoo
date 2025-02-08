from airflow import DAG
from airflow.providers.http.operators.http import HttpOperator
from airflow.providers.amazon.aws.transfers.local_to_s3 import LocalFilesystemToS3Operator
from airflow.operators.python_operator import PythonOperator
from datetime import date, datetime, timedelta
import json
import os
from helpers.transformations import transform_pollution_data

openweather_api_key = os.environ.get('OPENWEATHER_API_KEY')
openweather_version = '2.5'

vancouver_lat, vancouver_lon = 49.2497, -123.1193

default_args = {
    'owner': 'ginsstaahh',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 0,
    'retry_delay': timedelta(minutes=1),
    'iam_user': '',
}

with DAG('pollution_etl_dag',
        default_args=default_args,
        schedule_interval=timedelta(minutes=15),
        catchup=False
) as dag:

    get_pollution_data = HttpOperator(
        task_id='get_pollution_data',
        http_conn_id='openweather_conn',
        endpoint=f'data/{openweather_version}/air_pollution?lat={vancouver_lat}&lon={vancouver_lon}&appid={openweather_api_key}',
        method='GET',
        response_filter=lambda response: json.loads(response.text),
    )

    transform_pollution_data = PythonOperator(
        task_id='transform_pollution_data',
        python_callable=transform_pollution_data,
    )

get_pollution_data >> transform_pollution_data


with DAG('upload_pollution_data_dag',
        default_args=default_args,
        schedule='@daily',
        catchup=False
) as dag:

    current_date = (date.today()).strftime('%Y-%m-%d')
    upload_pollution_data = LocalFilesystemToS3Operator(
        task_id='upload_pollution_data',
        filename=f'pollution/vancouver-pollution-{current_date}.json',
        dest_key=f'vancouver-pollution-{current_date}.json',
        dest_bucket='susanoo-pollution',
        aws_conn_id='aws_default',
        replace=True,
    )

upload_pollution_data