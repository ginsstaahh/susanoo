from airflow import DAG
from airflow.providers.http.operators.http import HttpOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import json
import os
from transformations.weather_transformations import save_city_dimensions

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

with DAG('city_dimensions_dag',
        default_args=default_args,
        schedule_interval=None,
        catchup=False
) as dag:

    get_weather_data = HttpOperator(
        task_id='get_weather_data',
        http_conn_id='openweather_conn',
        endpoint=f'data/{openweather_version}/weather?q={city},{province},{country}&appid={openweather_api_key}',
        method='GET',
        response_filter=lambda response: json.loads(response.text),
    )

    save_city_dimensions = PythonOperator(
        task_id='save_city_dimensions_data',
        python_callable=save_city_dimensions,
    )

get_weather_data >> save_city_dimensions