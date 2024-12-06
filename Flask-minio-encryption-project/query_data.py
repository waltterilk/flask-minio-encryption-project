import requests
from minio import Minio
from minio.error import S3Error

minio_client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

def list_objects(bucket_name):
    """List all objects in the specified bucket."""
    try:
        objects = minio_client.list_objects(bucket_name)
        print(f"Objects in bucket '{bucket_name}':")
        for obj in objects:
            print(obj.object_name)
    except S3Error as e:
        print(f"Error accessing bucket '{bucket_name}': {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def get_message(object_id):
    url = f"http://localhost:5000/obj/{object_id}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Retrieved message:", response.json()['data'])
        else:
            print("Error:", response.json().get('error', 'Unknown error occurred'))
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    for bucket_name in ['even', 'odd']:
        list_objects(bucket_name)
    object_id = input("Enter the object ID: ")
    get_message(object_id)


#Example usage (tested after data generation script had been ran):
#Enter the object ID: data_c9861fd8-a3e0-4e22-8ce7-0bce7b8e25b2.bin
#Retrieved message: {'humidity': 78.7, 'temperature': -23.28, 'timeofmeasurement': {'day': 23, 'month': 3}, 'timestamp': 1729241923}
