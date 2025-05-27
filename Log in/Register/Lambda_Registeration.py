import pymysql
import json
import logging

# enable INFO-level logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# RDS Configuration
DB_HOST     = "yarb-mndf3sh-aktar-mn-keda.cp8kcmwa2o3e.us-east-1.rds.amazonaws.com"
DB_USER     = "admin"
DB_PASSWORD = "Admin123"
DB_NAME     = "main_db"

def lambda_handler(event, context):
    # 1. Parse and log incoming body
    body_str = event.get('body', '{}')
    logger.info(f"Raw event['body']: {body_str}")
    try:
        body = json.loads(body_str)
    except json.JSONDecodeError:
        logger.error("Failed to parse JSON body")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JSON in body'})
        }

    username = body.get('username')
    email    = body.get('email')
    password = body.get('password')

    # 2. Validate input
    if not username or not email or not password:
        logger.warning("Missing one of username/email/password")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'username, email and password are all required'})
        }

    conn = None
    cursor = None
    try:
        # 3. Connect to RDS
        logger.info("Connecting to RDS")
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()
        logger.info("Connected to RDS")

        # 4. Check for existing username or email
        check_sql = """
            SELECT user_id, username, email
              FROM Users
             WHERE username = %s OR email = %s
             LIMIT 1
        """
        logger.info(f"Running existence check: {check_sql} with [{username}, {email}]")
        cursor.execute(check_sql, (username, email))
        existing = cursor.fetchone()
        logger.info(f"Existence check result: {existing!r}")

        if existing:
            # If this log shows a row, then the check is indeed finding something.
            return {
                'statusCode': 409,
                'body': json.dumps({'error': 'Username or Email already exists', 'existing': existing})
            }

        # 5. Insert new user
        insert_sql = """
            INSERT INTO Users (username, email, password_hash)
            VALUES (%s, %s, %s)
        """
        logger.info(f"Inserting new user: {username}, {email}")
        cursor.execute(insert_sql, (username, email, password))
        conn.commit()
        logger.info("Insert committed")

        return {
            'statusCode': 201,
            'body': json.dumps({'message': 'User registered successfully', 'user_id': cursor.lastrowid})
        }

    except Exception as e:
        logger.exception("Unhandled exception")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
