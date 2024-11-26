import boto3
import os
import json
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from datetime import datetime, timedelta

def get_parameter_value(ssm_client, parameter_name):
    """
    Fetch the value of a parameter from AWS Systems Manager Parameter Store.
    """
    try:
        response = ssm_client.get_parameter(Name=parameter_name, WithDecryption=True)
        return response['Parameter']['Value']
    except Exception as e:
        raise ValueError(f"Error retrieving parameter {parameter_name}: {str(e)}")

def lambda_handler(event, context):
    """
    Lambda function to generate a presigned URL for an S3 object with structured output.
    """
    # Fetch bucket name and object key from environment variables
    bucket_name = os.getenv('BUCKET_NAME')
    object_key = os.getenv('OBJECT_KEY')  # Default object key

    # Allow overriding the object key via the event payload
    object_key = event.get('object_key', object_key)

    # Default expiration time for the presigned URL (7 days in seconds)
    expiration = int(os.getenv('PRESIGNED_URL_EXPIRATION', 604800))  # Default to 7 days

    # Validate required environment variables
    if not bucket_name or not object_key:
        return {
            "statusCode": 400,
            "body": {
                "error": "Environment variables 'BUCKET_NAME' or 'OBJECT_KEY' are missing.",
                "presigned_url": None,
                "expiration_time": None
            }
        }

    # Get Parameter Store paths for access key and secret key
    access_key_param = os.getenv('AWS_ACCESS_KEY_PARAM')
    secret_key_param = os.getenv('AWS_SECRET_KEY_PARAM')

    if not access_key_param or not secret_key_param:
        return {
            "statusCode": 500,
            "body": {
                "error": "Parameter store paths for access key and secret key are not set.",
                "presigned_url": None,
                "expiration_time": None
            }
        }

    try:
        # Initialize SSM client
        ssm_client = boto3.client('ssm')

        # Fetch credentials from Parameter Store
        access_key = get_parameter_value(ssm_client, access_key_param)
        secret_key = get_parameter_value(ssm_client, secret_key_param)

        # Initialize S3 client with the retrieved credentials
        s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )

        # Generate the presigned URL
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': object_key},
            ExpiresIn=expiration
        )

        # Calculate expiration time
        expiration_time = datetime.utcnow() + timedelta(seconds=expiration)

        # Return the presigned URL and expiration time with specified structure
        return {
            "statusCode": 200,
            "body": {
                "presigned_url": presigned_url,
                "expiration_time": expiration_time.strftime("%Y-%m-%d %H:%M:%S UTC")
            }
        }

    except ValueError as ve:
        return {
            "statusCode": 404,
            "body": {
                "error": str(ve),
                "presigned_url": None,
                "expiration_time": None
            }
        }
    except ssm_client.exceptions.ParameterNotFound as e:
        return {
            "statusCode": 404,
            "body": {
                "error": f"Parameter not found: {e}",
                "presigned_url": None,
                "expiration_time": None
            }
        }
    except (NoCredentialsError, PartialCredentialsError) as e:
        return {
            "statusCode": 500,
            "body": {
                "error": f"Credential error: {e}",
                "presigned_url": None,
                "expiration_time": None
            }
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": {
                "error": f"An unexpected error occurred: {str(e)}",
                "presigned_url": None,
                "expiration_time": None
            }
        }
