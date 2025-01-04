# scrap data
# open neighborhoods
# open crimes
# bairros metadata
# reload aplication

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

# Import tasks
from tasks.download_data import download_data
from tasks.open_neighborhoods import open_neighborhoods
from tasks.process_crimes import process_crimes
from tasks.process_neighborhoods import process_neighborhoods

# DAG
with DAG(
    dag_id='update_crimes',
    description='Monthly update on the crime statistics for Porto Alegre',
    start_date=datetime(2024, 12, 20, 22, 0),
    schedule_interval='@monthly'
) as dag:
    # Download the data from the oficial website
    task1 = PythonOperator(
        task_id = 'download_data',
        python_callable = download_data
    )
    # Open a list of all the neighborhoods in Porto Alegre
    task2 = PythonOperator(
        task_id = 'open_neighborhoods',
        python_callable = open_neighborhoods  
    )
    # Process the data and metadata from the downloaded data
    task3 = PythonOperator(
        task_id = 'process_crimes',
        python_callable = process_crimes
    )
    # Process the data and metadata from the neighborhoods geo data
    task4 = PythonOperator(
        task_id = 'process_neighborhoods',
        python_callable = process_neighborhoods  
    )

    task1 >> task3
    task2 >> task3
    task2 >> task4

