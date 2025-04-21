import pymysql
import json
import logging

logging.basicConfig(level=logging.INFO)

# Replace with your RDS connection details
DB_HOST = "yarb-mndf3sh-aktar-mn-keda.cp8kcmwa2o3e.us-east-1.rds.amazonaws.com"
DB_USER = "admin"
DB_PASSWORD = "Admin123"
DB_NAME = "UserDatabase"

def lambda_handler(event, context): 
    try:
        # Parse input data
        logging.info("Parsing input data")
        body = json.loads(event['body'])

        # Extract fields with default values or validation
        username = body.get('username')
        email = body.get('email')  # Use 'email' instead of 'gmail'
        password = body.get('password')

        # Validate input (add more validations as needed)
        if not username or not email or not password:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'All fields (username, email, password) are required'})
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

        # Insert data into the Users table
        logging.info("Inserting data into the database")
        insert_query = """
            INSERT INTO Users (username, password, email)
            VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (username, password, email))
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
        # Handle duplicate username or email
        logging.error(f"Database error: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Username or Email already exists'})
        }

    except Exception as e:
        # General error handling
        logging.error(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }