import json
import pymysql
import boto3

# RDS Configuration (Replace with your actual values)
RDS_HOST = "yarb-mndf3sh-aktar-mn-keda.cp8kcmwa2o3e.us-east-1.rds.amazonaws.com"
DB_USERNAME = "admin"
DB_PASSWORD = "Admin123"
DB_NAME = "user_auth"

# S3 Configuration (Replace with your actual bucket name)
S3_BUCKET_NAME = "users-picture"

# Initialize S3 client
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    connection = None
    try:
        # Check if user_id is in the query string parameters
        if 'queryStringParameters' not in event or 'user_id' not in event['queryStringParameters']:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'User ID is required'})
            }

        # Get the user ID from the query parameters
        user_id = event['queryStringParameters']['user_id']

        # Connect to the RDS database
        connection = pymysql.connect(
            host=RDS_HOST,
            user=DB_USERNAME,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        
        # Query the database for unit data
        with connection.cursor() as cursor:
            query = "SELECT id, unit_name, description FROM units WHERE user_id = %s"
            cursor.execute(query, (user_id,))
            units = cursor.fetchall()

        # Check if any units were found for the provided user_id
        if not units:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'No units found for the provided user ID'})
            }

        # Prepare the response data
        response_data = []

        for unit in units:
            id, unit_name, description = unit
            # Assume the image is named based on the unit ID (you can change this logic)
            image_key = f"{user_id}/{id}.jpg"
            
            # Get the image URL from S3
            image_url = get_s3_image_url(image_key)

            # Add the unit data to the response
            response_data.append({
                'id': id,
                'unit_name': unit_name,
                'description': description,
                'unit_image_url': image_url
            })

        return {
            'statusCode': 200,
            'body': json.dumps({'units': response_data})
        }

    except Exception as e:
        # Handle any errors and return the error response
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

    finally:
        # Always close the DB connection
        if connection:
            connection.close()

def get_s3_image_url(image_key):
    """
    This function retrieves the S3 URL of the image for the unit.
    """
    try:
        # Get the S3 object URL (presigned URL or direct access if public)
        image_url = s3_client.generate_presigned_url('get_object',
                                                     Params={'Bucket': S3_BUCKET_NAME, 'Key': image_key},
                                                     ExpiresIn=3600)  # URL expires in 1 hour
        return image_url
    except Exception as e:
        # Handle error (e.g., if the image is not found)
        return None
