from airflow import DAG
from airflow.providers.http.operators.http import HttpOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import json
import os

openweather_api_key = os.environ.get('OPENWEATHER_API_KEY')
openweather_version = '2.5'
city, province, country = 'Seattle', 'WA', 'US'

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

    get_city_data = HttpOperator(
        task_id='get_city_data',
        http_conn_id='openweather_conn',
        endpoint=f'data/{openweather_version}/weather?q={city},{province},{country}&appid={openweather_api_key}',
        method='GET',
        response_filter=lambda response: json.loads(response.text),
    )

    def save_city_dimensions(task_instance):
        """save_city_dimensions uses the HTTP response from Openweather to store
        dimension data of the city being queried in a json file"""
        weather_data = task_instance.xcom_pull(task_ids='get_city_data')
        transformed_data = {
            'city': weather_data['name'],
            'country': weather_data['sys']['country'],
            'longitude': weather_data['coord']['lon'],
            'latitude': weather_data['coord']['lat'],
            'timezone': weather_data['timezone'],
        }

        with open('city_dimensions.json', 'a') as file:
            json.dump(transformed_data, file)
            file.write('\n')

    save_city_dimension_data = PythonOperator(
        task_id='save_city_dimension_data',
        python_callable=save_city_dimensions,
    )

get_city_data >> save_city_dimension_data