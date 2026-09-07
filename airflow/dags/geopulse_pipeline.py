from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import subprocess
import sys
import os


# ============================================================
# GeoPulse project location inside the Docker container
# ============================================================
PROJECT_DIR = "/opt/airflow/project"


# ============================================================
# Default Airflow task settings
# ============================================================
default_args = {
    "owner": "geopulse",
    "retries": 2,
    "retry_delay": timedelta(minutes=1),
}


# ============================================================
# Function to run a GeoPulse Python script
# ============================================================
def run_script(script_name):
    script_path = os.path.join(PROJECT_DIR, script_name)

    result = subprocess.run(
        [sys.executable, script_path],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )

    # Display script output in Airflow task logs
    print(result.stdout)

    # If the script fails, show the error and mark task as failed
    if result.returncode != 0:
        print(result.stderr)
        raise Exception(f"{script_name} failed")

    print(f"{script_name} completed successfully")


# ============================================================
# GeoPulse Airflow DAG
# ============================================================
with DAG(
    dag_id="geopulse_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    description="GeoPulse automated data processing pipeline",
    default_args=default_args,
) as dag:

    # --------------------------------------------------------
    # Task 1: GPS Journey Generation
    # --------------------------------------------------------
    gps_generation = PythonOperator(
        task_id="gps_journey_generation",
        python_callable=run_script,
        op_args=["generate_gps_data.py"],
    )

    # --------------------------------------------------------
    # Task 2: Metadata Enrichment
    # --------------------------------------------------------
    metadata_enrichment = PythonOperator(
        task_id="metadata_enrichment",
        python_callable=run_script,
        op_args=["generate_gps_metadata.py"],
    )

    # --------------------------------------------------------
    # Task 3: Footfall / Store Visit Detection
    # --------------------------------------------------------
    footfall_detection = PythonOperator(
        task_id="footfall_detection",
        python_callable=run_script,
        op_args=["generate_footfall_data.py"],
    )

    # --------------------------------------------------------
    # Task 4: Catchment / Spatial Analysis
    # --------------------------------------------------------
    catchment_analysis = PythonOperator(
        task_id="catchment_spatial_analysis",
        python_callable=run_script,
        op_args=["generate_catchment_data.py"],
    )

    # --------------------------------------------------------
    # Task 5: Data Validation
    # --------------------------------------------------------
    data_validation = PythonOperator(
        task_id="data_validation",
        python_callable=run_script,
        op_args=["validate_data.py"],
    )

    # ========================================================
    # Task execution order
    # ========================================================
    gps_generation >> metadata_enrichment >> footfall_detection >> catchment_analysis >> data_validation