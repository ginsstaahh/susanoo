from airflow import DAG
from airflow.providers.amazon.aws.transfers.local_to_s3 import LocalFilesystemToS3Operator
from airflow.operators.python_operator import PythonOperator
from datetime import date, datetime, timedelta
import os

default_args = {
    'owner': 'ginsstaahh',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=1),
    'iam_user': '',
}

with DAG('load_s3_dag',
        default_args=default_args,
        schedule='@daily',
        catchup=False
) as dag:

    yesterday_date = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    load_weather_data_to_s3 = LocalFilesystemToS3Operator(
        task_id='load_weather_data_to_s3',
        filename=f'vancouver-weather-{yesterday_date}.json',
        dest_key=f'vancouver-weather-{yesterday_date}.json',
        dest_bucket='susanoo',
        aws_conn_id='aws_default',
        replace=True,
    )

    def delete_file(date):
        try:
            os.remove(f'vancouver-weather-{date}.json')
        except Exception as e:
            print(e)

    delete_local_file = PythonOperator(
        task_id='delete_local_file',
        python_callable=delete_file,
        op_args=[yesterday_date]
    )

load_weather_data_to_s3 >> delete_local_file