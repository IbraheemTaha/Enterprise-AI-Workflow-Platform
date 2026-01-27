from airflow import DAG
from airflow.decorators import task
from datetime import datetime

with DAG(
    'example_ml_pipeline',
    start_date=datetime(2024, 1, 1),
    schedule='@daily',
    catchup=False,
    tags=['example', 'ml']
) as dag:
    
    @task
    def extract_data():
        print("Extracting data...")
        return {"data": "sample"}
    
    @task
    def process_data(data):
        print(f"Processing: {data}")
        return {"processed": True}
    
    @task
    def train_model(processed_data):
        print(f"Training model with: {processed_data}")
        return "model_v1"
    
    data = extract_data()
    processed = process_data(data)
    model = train_model(processed)
