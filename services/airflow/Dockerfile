FROM apache/airflow:3.1.6-python3.12

USER airflow

ARG CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-3.1.6/constraints-3.12.txt"

COPY requirements.txt .
RUN pip install --no-cache-dir \
    -r requirements.txt \
    --constraint "${CONSTRAINT_URL}"
