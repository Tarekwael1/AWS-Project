import pymysql
import json
import logging

# RDS Configuration
rds_host = "yarb-mndf3sh-aktar-mn-keda.cp8kcmwa2o3e.us-east-1.rds.amazonaws.com"
username = "admin"  # Replace with your RDS username
password = "Admin123"  # Replace with your RDS password
db_name = "user_auth"

# Set up basic logging
logging.basicConfig(level=logging.INFO)

def lambda_handler(event, context):
    logging.info("Connecting to the database...")
    
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
            sql = "SELECT user_id, password_hash FROM users WHERE username=%s"
            cursor.execute(sql, (input_username,))
            logging.info("SQL query executed.")
            result = cursor.fetchone()
            
            if result:
                stored_user_id = result[0]
                stored_password_hash = result[1]
                
                # Assuming you are comparing plain text passwords
                # Use a hashing comparison in a real-world scenario
                if stored_password_hash == input_password:  # Adjust this to hashed password logic
                    return {
                        'statusCode': 200,
                        'body': json.dumps({'user_id': str(stored_user_id)})
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
        if connection:
            connection.close()
            logging.info("Connection closed.")