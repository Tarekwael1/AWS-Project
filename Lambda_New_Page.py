import json
import pymysql
import boto3
import uuid
import base64

# RDS Configuration (Replace with your actual values)
RDS_HOST = "yarb-mndf3sh-aktar-mn-keda.cp8kcmwa2o3e.us-east-1.rds.amazonaws.com"
DB_USERNAME = "admin"
DB_PASSWORD = "Admin123"
DB_NAME = "user_auth"

# S3 Configuration (Replace with your actual bucket name)
S3_BUCKET_NAME = "users-picture"

# Initialize S3 client and RDS connection
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    connection = None
    try:
        # Parse the incoming event body
        body = json.loads(event['body'])
        
        # Extract the unit data and image details from the body
        user_id = body['user_id']  # The user ID that ties the unit to the user
        unit_name = body['unit_name']
        description = body['description']
        user_image_data = body['user_image']  # Base64 encoded image data
        unit_image_data = body['unit_image']  # Base64 encoded image data
        
        # Generate unique filenames for the images
        user_image_key = f"{user_id}/user_image_{str(uuid.uuid4())}.jpg"
        unit_image_key = f"{user_id}/unit_image_{str(uuid.uuid4())}.jpg"
        
        # Upload images to S3
        user_image_url = upload_to_s3(user_image_key, user_image_data)
        unit_image_url = upload_to_s3(unit_image_key, unit_image_data)

        # Insert the unit data into the RDS database, specifically for this user
        connection = pymysql.connect(
            host=RDS_HOST,
            user=DB_USERNAME,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        
        with connection.cursor() as cursor:
            # SQL query to insert unit data based on the user_id
            query = """INSERT INTO units (user_id, unit_name, description, user_image_url, unit_image_url)
                       VALUES (%s, %s, %s, %s, %s)"""
            
            # Execute the query with the provided data
            cursor.execute(query, (user_id, unit_name, description, user_image_url, unit_image_url))
            connection.commit()
        
        # Return success response
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Unit added successfully',
                'unit_id': unit_name,  # You can return any relevant information here
                'user_image_url': user_image_url,
                'unit_image_url': unit_image_url
            })
        }

    except Exception as e:
        # Handle any errors that occur
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

    finally:
        # Always close the DB connection
        if connection:
            connection.close()

def upload_to_s3(image_key, image_data):
    """
    Upload the image data (base64 encoded) to S3.
    """
    try:
        # Add padding to base64 string if needed
        padding = len(image_data) % 4
        if padding != 0:
            image_data += '=' * (4 - padding)

        # Decode the base64 image data
        image_data_decoded = base64.b64decode(image_data)
        
        # Upload to S3 without public-read
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=image_key,
            Body=image_data_decoded,
            ContentType='image/jpeg'  # assuming the image is JPEG, adjust if necessary
        )
        
        # Generate the URL to the uploaded image (you can make it public or private as per your requirement)
        image_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{image_key}"
        return image_url

    except Exception as e:
        raise Exception(f"Error uploading image to S3: {str(e)}")
