# test_s3.py
import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# Obtiene las credenciales y el nombre del bucket del archivo .env
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region_name = os.getenv('AWS_S3_REGION_NAME')
aws_bucket_name = os.getenv('AWS_STORAGE_BUCKET_NAME')

# Configura el cliente de S3 usando las variables de entorno
s3_client = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region_name
)

try:
    s3_client.upload_file(
        'C:/Users/Cesar/Downloads/REDOX.png',
        aws_bucket_name,
        'logos_empresas/test.png'
    )
    print("Subida exitosa")
except ClientError as e:
    print(f"Error: {e}")