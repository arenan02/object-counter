# NIQ Innovation Enablement - Challenge 1 (Object Counting)

The goal of this repo is demonstrate how to apply Hexagonal Architecture in a ML based system.

This application consists in a Flask API that receives an image and a threshold and returns the number of objects detected in the image.

The application is composed by 3 layers:

- **entrypoints**: This layer is responsible for exposing the API and receiving the requests. It is also responsible for validating the requests and returning the responses.

- **adapters**: This layer is responsible for the communication with the external services. It is responsible for translating the domain objects to the external services objects and vice-versa.

- **domain**: This layer is responsible for the business logic. It is responsible for orchestrating the calls to the external services and for applying the business rules.

The model used in this example has been taken from 
[IntelAI](https://github.com/IntelAI/models/blob/master/docs/object_detection/tensorflow_serving/Tutorial.md)

## Table of Contents
1. [Key Features](#key-features)
2. [Instructions to Configure This Project](#instructions-to-configure-this-project)
    - [Download the RFCN Model](#download-the-rfcn-model)
    - [Install Dependencies with Poetry](#install-dependencies-with-poetry)
    - [Setup and Run TensorFlow Serving](#setup-and-run-tensorflow-serving)
    - [Run Mongo](#run-mongo)
    - [Run PostgreSQL](#run-postgresql)
    - [Automate Setup with Makefile](#automate-setup-with-makefile)
3. [Run the Application](#run-the-application)
4. [API Documentation](#api-documentation)
    - [/object-count Endpoint](#object-count-endpoint)
    - [/predict Endpoint](#predict-endpoint)
5. [Testing](#testing)
6. [Database Integration](#database-integration)

## Key Features
* **New Service Endpoint**: Added a /predict endpoint to provide predictions directly.
* **PostgreSQL Integration**: Implemented CountSQLDBRepo adapter to store and retrieve object counts using PostgreSQL.
* **Makefile**: Automates common tasks such as setup, testing, and running the application.
* **Dependency Management with Poetry**: Migrated to Poetry for modern and efficient dependency management.

## Instructions to configure this project
### Download the rfcn model 
```
wget https://storage.googleapis.com/intel-optimized-tensorflow/models/v1_8/rfcn_resnet101_fp32_coco_pretrained_model.tar.gz
tar -xzvf rfcn_resnet101_fp32_coco_pretrained_model.tar.gz -C tmp
rm rfcn_resnet101_fp32_coco_pretrained_model.tar.gz
chmod -R 777 tmp/rfcn_resnet101_coco_2018_01_28
mkdir -p tmp/model/rfcn/1
mv tmp/rfcn_resnet101_coco_2018_01_28/saved_model/saved_model.pb tmp/model/rfcn/1
rm -rf tmp/rfcn_resnet101_coco_2018_01_28
```
### Install dependencies with Poetry
This project uses **Poetry** to manage dependencies and environments
#### Install Poetry
```bash
curl -sSL https://install.python-poetry.org | python3 -
```
#### Install dependencies
```bash 
poetry install
```
OR
```bash
poetry add $(cat requirements.txt)
```
#### Activate the virtual environment
```bash
poetry shell
```

## Setup and run Tensorflow Serving

### If you have access to Intel Optimized Cores
```
# For unix systems
cores_per_socket=`lscpu | grep "Core(s) per socket" | cut -d':' -f2 | xargs`
num_sockets=`lscpu | grep "Socket(s)" | cut -d':' -f2 | xargs`
num_physical_cores=$((cores_per_socket * num_sockets))

docker rm -f tfserving
docker run \
    --name=tfserving \
    -p 8500:8500 \
    -p 8501:8501 \
    -v "$(pwd)/tmp/model:/models" \
    -e OMP_NUM_THREADS=$num_physical_cores \
    -e TENSORFLOW_INTER_OP_PARALLELISM=2 \
    -e TENSORFLOW_INTRA_OP_PARALLELISM=$num_physical_cores \
    intel/intel-optimized-tensorflow-serving:2.8.0 \
    --model_config_file=/models/model_config.config

# For Windows (Powershell)
$num_physical_cores=(Get-WmiObject Win32_Processor | Select-Object NumberOfCores).NumberOfCores
echo $num_physical_cores

docker rm -f tfserving
docker run `
    --name=tfserving `
    -p 8500:8500 `
    -p 8501:8501 `
    -v "$pwd\tmp\model:/models" `
    -e OMP_NUM_THREADS=$num_physical_cores `
    -e TENSORFLOW_INTER_OP_PARALLELISM=2 `
    -e TENSORFLOW_INTRA_OP_PARALLELISM=$num_physical_cores `
    intel/intel-optimized-tensorflow-serving:2.8.0 `
    --model_config_file=/models/model_config.config
```
`Note`

* TensorFlow Serving (or Intel-optimized TensorFlow) is compiled to take advantage of specific CPU instructions like AVX, AVX2, or AVX-512, which are supported only on modern CPUs.
* If your CPU does not support these instructions, running the binary will fail with this error.

### On normal cores
```
# For unix systems
cores_per_socket=`lscpu | grep "Core(s) per socket" | cut -d':' -f2 | xargs`
num_sockets=`lscpu | grep "Socket(s)" | cut -d':' -f2 | xargs`
num_physical_cores=$((cores_per_socket * num_sockets))

docker rm -f tfserving
docker run \
    --name=tfserving \
    -p 8500:8500 \
    -p 8501:8501 \
    -v "$(pwd)/tmp/model:/models" \
    tensorflow/serving:latest \
    --model_config_file=/models/model_config.config

# For Windows (Powershell)
$num_physical_cores=(Get-WmiObject Win32_Processor | Select-Object NumberOfCores).NumberOfCores
echo $num_physical_cores

docker rm -f tfserving
docker run `
    --name=tfserving `
    -p 8500:8500 `
    -p 8501:8501 `
    -v "$pwd\tmp\model:/models" `
    tensorflow/serving:latest `
    --model_config_file=/models/model_config.config
```


## Run mongo 

```bash
docker rm -f test-mongo
docker run --name test-mongo --rm -p 27017:27017 -d mongo:latest
```

## Run PostgreSQL
### Using Docker
```bash
docker rm -f test-postgres
docker run --name test-postgres -e POSTGRES_PASSWORD=postgres -d -p 5400:5432 postgres
```
### Create the Database Schema
Access the PostgreSQL container:
```bash
docker exec -it test-postgres psql -U postgres
```
Run the following SQL commands:
```sql
CREATE DATABASE test_object_db;
\c test_object_db
CREATE TABLE object_counts (
    object_class VARCHAR(255) PRIMARY KEY,
    count INT NOT NULL
);
```

## Automate setup with Makefile
Use the included `Makefile` to streamline common tasks.
### Set up the environment
```bash
make setup
```
### Run the application
```bash
make run
```
### Run tests
```bash
make test
```
### Format and link code
```bash
make format
make lint
```

## Run the application
### Using fakes
```
python -m counter.entrypoints.webapp
```

### Using real services in docker containers

```
# Unix
ENV=prod python -m counter.entrypoints.webapp

# Powershell
$env:ENV = "prod"
python -m counter.entrypoints.webapp
```

## Call the service

### `/object-count` **Endpoint**
* **Method**: `POST`
* **Description**: Detect objects and return their counts for a given image and confidence threshold.

**Request Parameters**:

* `file` (form-data): The image file to process.
* `threshold` (form-data): The confidence threshold (default: 0.5).


**Example Request**:

```shell script
 curl -F "threshold=0.9" -F "file=@resources/images/boy.jpg" http://0.0.0.0:5000/object-count
```
### `/predict` **Endpoint**
* **Method**: `POST`
* **Description**: Return predictions for objects detected in the image.

**Request Parameters**:
* `file` (form-data): The image file to process.
* `threshold` (form-data): The confidence threshold (default: 0.5).

**Example Request**:
```bash
curl -F "threshold=0.9" -F "file=@resources/images/cat.jpg" http://localhost:5000/predict
```
## Testing
### Run all tests
```bash
poetry run pytest
```
### Integration tests for PostgreSQL
```bash
poetry run pytest -v tests/adapters/test_count_sql_db_repo.py
```
## Project Structure
```plaintext
├── counter
│   ├── adapters         # Adapters for database and external service integration
│   ├── domain           # Business logic and domain models
│   ├── entrypoints      # Flask application and API definitions
│   └── tests            # Unit and integration tests
├── tmp                  # Model files for TensorFlow Serving
├── Makefile             # Automates setup, running, and testing
├── pyproject.toml       # Poetry configuration file
├── README.md            # Project documentation
└── requirements.txt     # (Optional) Legacy dependency file
```
## Database Integration
The `CountSQLDBRepo` adapter allows persisting and retrieving object detection results using PostgreSQL.

### Methods
* `update_values(new_values: List[ObjectCount])`: Insert or update object counts.
* `read_values(object_classes: List[str] = None) -> List[ObjectCount]`: Retrieve object counts filtered by class.