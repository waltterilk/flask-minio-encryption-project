import random
import time
import json
import requests
from datetime import datetime
from minio import Minio
from minio.error import S3Error


minio_client = Minio(
    "127.0.0.1:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

def create_bucket(bucket_name):
    try:
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
            print(f"Bucket '{bucket_name}' created.")
        else:
            print(f"Bucket '{bucket_name}' already exists.")
    except S3Error as e:
        print(f"Error creating bucket '{bucket_name}': {e}")

def generate_data():
    return {
        "timestamp": int(datetime.now().timestamp()),
        "timeofmeasurement": {
            "day": random.randint(1, 30),
            "month": random.randint(1, 12)
        },
        "temperature": round(random.uniform(-40, 40), 2),
        "humidity": round(random.uniform(0, 100), 2)
    }

def send_data():
    while True:
        data = generate_data()
        current_second = datetime.now().second
        url = "http://localhost:5000/even" if current_second % 2 == 0 else "http://localhost:5000/odd"

        response = requests.post(url, json=data)
        print(f"Sent to {url}: {data} - Response: {response.status_code}")
        
        time.sleep(1)

if __name__ == "__main__":
    create_bucket('even')
    create_bucket('odd')

    send_data()