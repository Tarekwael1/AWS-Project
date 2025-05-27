import json
import boto3
import pymysql
import logging
from pymysql import Error as DBError
from botocore.exceptions import BotoCoreError, ClientError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Database connection details (replace with your RDS credentials)
db_config = {
    'host': 'yarb-mndf3sh-aktar-mn-keda.cp8kcmwa2o3e.us-east-1.rds.amazonaws.com',
    'user': 'admin',
    'password': 'Admin123',
    'db': 'main_db',
}

# S3 bucket details
s3_bucket = "prediction-resultss"  # Replace with your S3 bucket name

def delete_image_data(image_url, user_id):
    connection = None
    cursor = None
    try:
        # Initialize S3 client
        s3 = boto3.client('s3')
        logger.info("S3 client initialized")

        # Step 1: Extract the S3 object key from the URL
        # Handle different S3 URL formats:
        # Format 1: https://s3.amazonaws.com/bucket-name/path/to/object
        # Format 2: https://bucket-name.s3.amazonaws.com/path/to/object
        import re

        match = re.search(rf"{s3_bucket}\.s3[\.-][a-z0-9-]+\.amazonaws\.com/(.+)", image_url)
        if match:
            object_key = match.group(1)
        else:
            logger.error(f"Unsupported S3 URL format: {image_url}")
            return {
                'status': 'error',
                'message': f"Unsupported S3 URL format: {image_url}"
            }


        logger.info(f"Deleting S3 object with key: {object_key}")

        try:
            # Delete the object from S3
            s3.delete_object(Bucket=s3_bucket, Key=object_key)
            logger.info(f"Deleted S3 object: {object_key}")
        except (BotoCoreError, ClientError) as e:
            logger.error(f"Error deleting object from S3: {e}")
            raise

        # Step 2: Delete the record from RDS (and ensure it matches the user_id)
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()
        logger.info("Connected to the database")

        delete_query = "DELETE FROM Disease_Detection_Results WHERE disease_uri = %s AND user_id = %s"
        logger.info(f"Executing query: {delete_query} with disease_uri: {image_url} and user_id: {user_id}")
        cursor.execute(delete_query, (image_url, user_id))
        connection.commit()
        logger.info(f"Deleted {cursor.rowcount} record(s) from RDS")

        return {
            'status': 'success',
            'message': f"Deleted image {image_url} from S3 and RDS for user {user_id}"
        }

    except DBError as e:
        logger.error(f"Database error: {e}")
        return {
            'status': 'error',
            'message': f"Database error: {str(e)}"
        }
    except (BotoCoreError, ClientError) as e:
        logger.error(f"S3 error: {e}")
        return {
            'status': 'error',
            'message': f"S3 error: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            'status': 'error',
            'message': f"Unexpected error: {str(e)}"
        }
    finally:
        # Close the database connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()
        logger.info("Database connection closed")

def lambda_handler(event, context):
    try:
        # Parse the image URL and user_id from the API event
        body = json.loads(event['body'])
        image_url = body.get('image_url')
        user_id = body.get('user_id')
        
        # Validate input
        if not image_url:
            logger.error("image_url is missing or empty")
            return {
                'statusCode': 400,
                'body': json.dumps({"error": "image_url is required"})
            }
        
        if not user_id:
            logger.error("user_id is missing or empty")
            return {
                'statusCode': 400,
                'body': json.dumps({"error": "user_id is required"})
            }

        logger.info(f"Received request to delete image: {image_url} for user: {user_id}")

        # Call the function to delete the image
        result = delete_image_data(image_url, user_id)

        # Return the response
        return {
            'statusCode': 200 if result['status'] == 'success' else 500,
            'body': json.dumps(result, indent=2)
        }

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in event body: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps({"error": "Invalid JSON in event body"})
        }
    except Exception as e:
        logger.error(f"Error in lambda_handler: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)})
        }
