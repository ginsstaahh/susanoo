from airflow import DAG
from airflow.providers.http.operators.http import HttpOperator
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.transfers.local_to_s3 import LocalFilesystemToS3Operator
from datetime import datetime, timedelta
import json
import os
from transformations.weather_transformations import transform_data

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

with DAG('openweather_current_dag',
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
        python_callable=transform_data,
    )

    load_weather_data_to_s3 = LocalFilesystemToS3Operator(
        task_id='load_weather_data_to_s3',
        filename="{{ task_instance.xcom_pull(task_ids='transform_weather_data') }}",
        dest_key="{{ task_instance.xcom_pull(task_ids='transform_weather_data') }}",
        dest_bucket='susanoo',
        aws_conn_id='aws_default',
        replace=True,
    )

get_weather_data >> transform_weather_data >> load_weather_data_to_s3