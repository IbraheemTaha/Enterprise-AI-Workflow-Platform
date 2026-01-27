FROM python:3.12-slim


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


EXPOSE 5000

CMD ["mlflow", "server", "--host", "0.0.0.0", "--port", "5000"]
