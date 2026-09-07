# GeoPulse Airflow Pipeline

## Overview

The GeoPulse project uses **Apache Airflow** to automate and manage the data processing pipeline.

The pipeline contains five sequential stages. Each stage is represented as a separate Airflow task, allowing the execution order, status, logs, and failures to be monitored through the Airflow web interface.

## Pipeline Flow

```text
GPS Journey Generation
        ↓
Metadata Enrichment
        ↓
Footfall / Store Visit Detection
        ↓
Catchment / Spatial Analysis
        ↓
Data Validation
```

## Airflow DAG

**DAG Name:** `geopulse_pipeline`

The DAG is currently configured for manual triggering. This allows the complete pipeline to be executed when required.

## Pipeline Tasks

### 1. GPS Journey Generation

**Script:** `generate_gps_data.py`

Generates the synthetic GPS journey data used by the GeoPulse project.

### 2. Metadata Enrichment

**Script:** `generate_gps_metadata.py`

Adds metadata and supporting information to the generated GPS data.

### 3. Footfall / Store Visit Detection

**Script:** `generate_footfall_data.py`

Processes GPS movement data to identify store visits and generate footfall-related data.

### 4. Catchment / Spatial Analysis

**Script:** `generate_catchment_data.py`

Performs catchment and spatial analysis using the generated mobility and store data.

### 5. Data Validation

**Script:** `validate_data.py`

Checks the processed data and validates the output of the pipeline.

## Task Dependencies

The tasks are executed in the following order:

```text
gps_journey_generation
          ↓
metadata_enrichment
          ↓
footfall_detection
          ↓
catchment_spatial_analysis
          ↓
data_validation
```

A downstream task starts only after the previous task has completed successfully.

## Retry Configuration

Airflow is configured to automatically retry failed tasks.

```text
Maximum retries: 2
Retry delay: 1 minute
```

This improves pipeline reliability by allowing temporary failures to be retried automatically.

## Docker Setup

Airflow runs inside a Docker container.

The GeoPulse project directory is mounted into the container as:

```text
Windows Project Folder
        ↓
/opt/airflow/project
```

The Airflow DAG directory is mounted as:

```text
airflow/dags
        ↓
/opt/airflow/dags
```

## Starting Airflow

Open PowerShell in the GeoPulse project directory:

```powershell
cd "C:\Users\anees\OneDrive\Documents\Geopulse-Hyper-Local-Retail-Mobility-Analytics"
```

Start the Airflow container:

```powershell
docker compose up -d
```

Check the running container:

```powershell
docker ps
```

The container should appear as:

```text
geopulse_airflow
```

## Accessing Airflow

Open the following address in a web browser:

```text
http://localhost:8080
```

Login using the Airflow administrator account configured for the local project.

## Running the Pipeline

1. Open the Airflow web interface.
2. Find the `geopulse_pipeline` DAG.
3. Open the DAG.
4. Trigger the DAG manually.
5. Open the Graph view to monitor the task execution.
6. Check the task logs if a task fails.

## Monitoring

Airflow provides monitoring for every pipeline task.

The Graph view can be used to see:

- Task execution order
- Running tasks
- Successful tasks
- Failed tasks
- Task dependencies

Task logs can be opened from the Airflow interface to troubleshoot failures.

## Project Dependencies

The GeoPulse pipeline uses the following Python libraries:

```text
pandas
numpy
```

These dependencies are listed in the project's root `requirements.txt` file.

## Expected Result

After successful execution, the five Airflow tasks should complete in sequence:

```text
GPS Journey Generation       SUCCESS
            ↓
Metadata Enrichment          SUCCESS
            ↓
Footfall Detection           SUCCESS
            ↓
Catchment Analysis           SUCCESS
            ↓
Data Validation              SUCCESS
```

## Benefits of Using Airflow

Apache Airflow provides the following benefits for the GeoPulse project:

- Automated pipeline execution
- Task dependency management
- Pipeline monitoring
- Task-level logging
- Failure detection
- Automatic task retries
- Clear visualization of the complete workflow

## Airflow Directory Structure

```text
airflow/
│
├── dags/
│   └── geopulse_pipeline.py
│
└── README.md
```

## Summary

The GeoPulse data processing pipeline has been integrated with Apache Airflow and Docker. The existing Python processing stages are represented as independent Airflow tasks and executed in the required order.

This provides a structured, monitored, and reliable workflow for processing GeoPulse mobility analytics data.