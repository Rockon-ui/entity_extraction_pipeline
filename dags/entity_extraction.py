from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime
import logging
import pandas as pd
import json
from utils.match_entities import match_entities
from utils.schema_output import write_output_data
from docker.types import Mount


# Global paths inside Airflow container
DOCUMENTS_CSV = "/opt/airflow/data/documents.csv"
ALIASES_CSV = "/opt/airflow/data/entity_aliases.csv"
EXTRACTED_ENTITIES_JSON = "/opt/airflow/output/entities_extracted.json"
MATCHED_ENTITIES_JSON = "/opt/airflow/output/entities_matched.json"
FINAL_OUTPUT_CSV = "/opt/airflow/output/final_output.csv"

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Default arguments
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'retries': 1
}

# Load documents
def load_documents(**kwargs):
    try:
        logger.info("Loading documents...")
        df = pd.read_csv(DOCUMENTS_CSV)
        json_data = df.to_json(orient="records")
        kwargs['ti'].xcom_push(key="documents", value=json_data)
    except Exception as e:
        logger.error(f"Error loading documents: {e}")

# Match extracted entities
def match_entities_task(**kwargs):
    try:
        with open(EXTRACTED_ENTITIES_JSON, 'r') as f:
            extracted = json.load(f)
        df_aliases = pd.read_csv(ALIASES_CSV)
        matched = match_entities(extracted, df_aliases)
        with open(MATCHED_ENTITIES_JSON, 'w') as f:
            json.dump(matched, f)
        kwargs['ti'].xcom_push(key="matched_entities", value=json.dumps(matched))
    except Exception as e:
        logger.error(f"Error matching entities: {e}")

# Save final output
def store_output(**kwargs):
    try:
        write_output_data(DOCUMENTS_CSV, MATCHED_ENTITIES_JSON, FINAL_OUTPUT_CSV)
        logger.info("Final output stored successfully.")
    except Exception as e:
        logger.error(f"Error storing final output: {e}")

with DAG('entity_extraction_pipeline',
         default_args=default_args,
         schedule=None,
         catchup=False) as dag:

    load_documents_task = PythonOperator(
        task_id='load_documents',
        python_callable=load_documents
    )

    extract_entities_task = DockerOperator(
        task_id='extract_entities',
        image='gliner-extractor',
        api_version='auto',
        auto_remove=True,
        command='python extractor.py',
        docker_url='tcp://localhost:2375',  # or unix:///var/run/docker.sock on Linux
        network_mode='bridge',
        mount_tmp_dir=False,
        mounts=[
            Mount(source='/opt/airflow/data', target='/app/data', type='bind'),
            Mount(source='/opt/airflow/output', target='/app/output', type='bind'),
            Mount(source='/opt/airflow/extractor.py', target='/app/extractor.py', type='bind')
        ]
    )

    match_entities_op = PythonOperator(
        task_id='match_entities',
        python_callable=match_entities_task
    )

    store_output_task = PythonOperator(
        task_id='store_output',
        python_callable=store_output
    )

    load_documents_task >> extract_entities_task >> match_entities_op >> store_output_task
