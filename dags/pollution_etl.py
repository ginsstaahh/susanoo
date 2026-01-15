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

    city_dag_name = city.replace(' ', '_').lower()
    with DAG(f'{city_dag_name}_pollution_etl_dag',
            default_args=default_args,
            schedule_interval=timedelta(minutes=15),
            catchup=False
    ) as dag:

        extract_data = HttpOperator(
            task_id='get_pollution_data',
            http_conn_id='openweather_conn',
            endpoint=f'data/{openweather_version}/air_pollution?lat={latitude}&lon={longitude}&appid={openweather_api_key}',
            method='GET',
            response_filter=lambda response: json.loads(response.text),
        )

        transform_data = PythonOperator(
            task_id='transform_pollution_data',
            python_callable=transform_pollution_data,
            op_kwargs = {'city': city, 'country': country}
        )

    extract_data >> transform_data


with DAG('upload_pollution_data_dag',
    default_args=default_args,
    schedule='@daily',
    start_date=pendulum.datetime(2025, 2, 9, tz='local'),
    catchup=True
) as dag:

    start_tasks = DummyOperator(task_id='start_tasks')

    @task
    def check_file_exists(**kwargs):
        """Checks if the pollution data file exists for the given execution date
        Keyword Args:
            ds (str) - The execution date in 'YYYY-MM-DD' format"""
        ds = kwargs['ds']
        filename = f'pollution-{ds}.json'

        if os.path.exists(f'pollution/{filename}'):
            print('The pollution file exists')
            return True
        else:
            return False

    @task.branch
    def skip_run(file_exists):
        """Branches the DAG.  If the file exists, the clean_data task is run.
        Otherwise the DAG skips to the end_tasks.
        Args:
            file_exists (bool) - Whether the weather data file exists
        """
        if file_exists:
            return ['clean_data']
        else:
            return ['end_tasks']

    # create a temporary file to work with before replacing the working file.  This needs to be done for a sort command.
    # This sorts the data alphabetically and removes duplicate rows
    clean_data = BashOperator(
        task_id='clean_data',
        bash_command='sort -u ~/Documents/susanoo/pollution/pollution-{{ ds }}.json > /tmp/pollution-{{ ds }}.json && \
            mv /tmp/pollution-{{ ds }}.json ~/Documents/susanoo/pollution/pollution-{{ ds }}.json'
    )

    @task
    def upload_data(**kwargs):
        """Uploads the pollution data file to the S3 bucket
        Keyword Args:
            ds (str) - The execution date in 'YYYY-MM-DD' format
        """
        ds = kwargs['ds']
        filename = f'pollution-{ds}.json'

        s3_client = boto3.client('s3')
        try:
            s3_client.upload_file(f'pollution/{filename}', 'susanoo-pollution', filename)
        except ClientError as e:
            print(e)
            return False
        return True

    end_tasks = DummyOperator(task_id='end_tasks')

file_exists = check_file_exists()

start_tasks >> file_exists >> skip_run(file_exists) >> [clean_data, end_tasks]
clean_data >> upload_data() >> end_tasks