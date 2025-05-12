import pymysql
import json
import logging

# RDS Configuration
rds_host = "yarb-mndf3sh-aktar-mn-keda.cp8kcmwa2o3e.us-east-1.rds.amazonaws.com"
username = "admin"  # Replace with your RDS username
password = "Admin123"  # Replace with your RDS password
db_name = "main_db"

# Set up basic logging
logging.basicConfig(level=logging.INFO)

def lambda_handler(event, context):
    logging.info("Connecting to the database...")
    connection = None  # <-- Define connection as None here

    try:
        # Connect to the database
        connection = pymysql.connect(
            host=rds_host,
            user=username,
            password=password,
            database=db_name
        )
        logging.info("Connected to the database.")
        
        # Parse the body of the event to extract username and password
        body = json.loads(event['body'])  # Parse the JSON string in event.body
        input_username = body.get('username')
        input_password = body.get('password')
        
        if not input_username or not input_password:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Username and password are required'})
            }
        
        # SQL Query to check for matching credentials
        logging.info("Executing SQL query...")
        with connection.cursor() as cursor:
            sql = "SELECT username, user_id, password_hash FROM Users WHERE username=%s"
            cursor.execute(sql, (input_username,))
            logging.info("SQL query executed.")
            result = cursor.fetchone()
            
            if result:
                stored_user_id = str(result[1])
                stored_password_hash = result[2]
                
                # Assuming you are comparing plain text passwords
                # In production, use hashed password comparison (e.g., bcrypt)
                if stored_password_hash == input_password:
                    return {
                        'statusCode': 200,
                        'body': json.dumps({'user_id': stored_user_id})
                    }
                else:
                    return {
                        'statusCode': 401,
                        'body': json.dumps({'message': 'Invalid credentials'})
                    }
            else:
                return {
                    'statusCode': 401,
                    'body': json.dumps({'message': 'Invalid credentials'})
                }
    
    except pymysql.MySQLError as e:
        logging.error(f"Error connecting to MySQL: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Database connection failed', 'details': str(e)})
        }
    except Exception as e:
        logging.error(f"Unhandled exception: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
    finally:
        # Always close the connection to avoid leaks
        if connection is not None:  # <-- Only close if connection is assigned
            connection.close()
            logging.info("Connection closed.")
