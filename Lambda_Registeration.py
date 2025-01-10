import pymysql
import json
import logging

logging.basicConfig(level=logging.INFO)

# Replace with your RDS connection details
DB_HOST = "yarb-mndf3sh-aktar-mn-keda.cp8kcmwa2o3e.us-east-1.rds.amazonaws.com"
DB_USER = "admin"
DB_PASSWORD = "Admin123"
DB_NAME = "user_auth"

def lambda_handler(event, context):
    try:
        # Parse input data
        logging.info("Parsing input data")
        body = json.loads(event['body'])
        username = body['username']
        gmail = body['gmail']
        password = body['password']
        unit_id = body['unit_id']

        # Validate input (add more validations as needed)
        if not username or not gmail or not password or not unit_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'All fields are required'})
            }

        # Connect to the RDS database
        logging.info("Connecting to the RDS database")
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        logging.info("Connected to the RDS database")
        cursor = conn.cursor()

        # Insert data into the Users table without hashing the password
        logging.info("Inserting data into the database")
        insert_query = """
            INSERT INTO users (username, gmail, password_hash, unit_id)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (username, gmail, password, unit_id))
        conn.commit()

        # Close the connection
        logging.info("Closing the database connection")
        cursor.close()
        conn.close()

        return {
            'statusCode': 201,
            'body': json.dumps({'message': 'User registered successfully'})
        }

    except pymysql.IntegrityError as e:
        # Handle duplicate username or Gmail
        logging.error(f"Database error: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Username or Gmail already exists'})
        }

    except Exception as e:
        # General error handling
        logging.error(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
