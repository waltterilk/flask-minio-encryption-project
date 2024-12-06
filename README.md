# Flask Minio Encryption Project

This project implements a Flask-based web service that handles JSON data sent to it, stores the data in Minio object storage with AES encryption, and provides an endpoint for querying stored data. The project includes the following services:

1. **Data Generation**: A Python script that sends JSON data to a Flask server at a rate of one message per second.
   - Even seconds (`/even` route)
   - Odd seconds (`/odd` route)

2. **Flask Server**: A server that:
   - Receives JSON data on `/even` and `/odd` routes and stores it in Minio.
   - Encrypts the data using AES with a randomly generated encryption key.
   - Stores metadata (object ID, encryption key, nonce, tag) in a PostgreSQL database.

3. **Object Retrieval**: A third route (`/obj/<object_id>`) is available for retrieving and decrypting stored objects using the object ID.

4. **Query Script**: A script (`query_data.py`) that allows querying the Flask server to retrieve and decrypt an object by its ID.

## Prerequisites

- Minio (running locally or in a container)
- Flask (Python web framework)
- PostgreSQL (for storing encryption metadata)
- Python 3.x
- Docker (optional for containerization)

## Installation

1. Clone this repository
2. Install dependencies:
- pip install -r requirements.txt
3. Set up the PostgreSQL database (key_storage) and table:
CREATE TABLE object_metadata (
   object_id TEXT PRIMARY KEY,
   encryption_key TEXT,
   nonce TEXT,
   tag TEXT,
   owner TEXT
);
4. Run Minio
5. Run the Flask server:
- python flask_app.py
6. Run the data generation script:
- python data_generation.py
7. Use the query script to retrieve messages:
- python query_data.py

## Routes
- POST /even: Receives JSON data and stores it in the 'even' Minio bucket.
- POST /odd: Receives JSON data and stores it in the 'odd' Minio bucket.
- GET /obj/<object_id>: Retrieves and decrypts the object from Minio using the given object ID.
