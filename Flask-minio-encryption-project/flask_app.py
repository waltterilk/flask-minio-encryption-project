from flask import Flask, request, jsonify
from minio import Minio
from minio.error import S3Error
from Crypto.Cipher import AES
from io import BytesIO
from Crypto.Random import get_random_bytes
import psycopg2
import uuid
import json

app = Flask(__name__)

minio_client = Minio(
    "localhost:9000",
    access_key="", # access key here
    secret_key="", # secret key here
    secure=False
)


def get_db_connection():
    return psycopg2.connect(
        dbname="key_storage",
        user="", # database user
        password="", # database password
        host="localhost",
        port="5432"
    )

def encrypt_data(data):
    data_bytes = json.dumps(data).encode('utf-8')
    key = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(data_bytes)
    nonce = cipher.nonce
    return key, ciphertext, tag, nonce

@app.route('/even', methods=['POST'])
def even():
    return handle_data(request.json, 'even')

@app.route('/odd', methods=['POST'])
def odd():
    return handle_data(request.json, 'odd')



def handle_data(data, bucket_name):
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    key, encrypted_data, tag, nonce = encrypt_data(data)

    object_id = str(uuid.uuid4())
    object_name = f"data_{object_id}.bin"

    try:
        encrypted_data_io = BytesIO(encrypted_data)

        minio_client.put_object(bucket_name, object_name, encrypted_data_io, len(encrypted_data), content_type="application/octet-stream")

        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO object_metadata (object_id, encryption_key, nonce, tag, owner)
                    VALUES (%s, %s, %s, %s, %s)
                """, (object_name, key.hex(), nonce.hex(), tag.hex(), 'Waltteri'))

        return jsonify({"message": "Data stored successfully", "object_id": object_name}), 200

    except S3Error as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    

@app.route('/obj/<object_id>', methods=['GET'])
def get_object(object_id):
    for bucket_name in ['even', 'odd']:
        try:
            response = minio_client.get_object(bucket_name, object_id)
            encrypted_data = response.read()

            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT encryption_key, nonce, tag FROM object_metadata WHERE object_id = %s
                    """, (object_id,))
                    result = cursor.fetchone()

            if result:
                key_hex, nonce_hex, tag_hex = result
                key = bytes.fromhex(key_hex)
                nonce = bytes.fromhex(nonce_hex)
                tag = bytes.fromhex(tag_hex)

                decrypted_message = decrypt_data(encrypted_data, key, nonce, tag)

                return jsonify({'data': json.loads(decrypted_message)}), 200
            else:
                return jsonify({'error': 'Metadata not found for object'}), 404

        except S3Error as e:
            if e.code != 'NoSuchKey':
                return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Object not found in either bucket'}), 404


def decrypt_data(encrypted_data, key, nonce, tag):
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    decrypted_data = cipher.decrypt_and_verify(encrypted_data, tag)
    return decrypted_data

if __name__ == "__main__":
    app.run(debug=True)
