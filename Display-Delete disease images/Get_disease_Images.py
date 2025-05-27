import json
import pymysql
import logging

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

def lambda_handler(event, context):
    try:
        # Log the entire event for debugging
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Check if the body is a string and parse it
        if isinstance(event.get('body'), str):
            event['body'] = json.loads(event['body'])
        
        # Extract user_id from the parsed body
        user_id = event['body'].get('user_id')
        
        if not user_id:
            logger.error("user_id is required")
            return {
                'statusCode': 400,
                'body': json.dumps({"error": "user_id is required"})
            }

        logger.info(f"Received user_id: {user_id}")

        # Connect to the database
        logger.info("Connecting to the database...")
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()
        logger.info("Connected to the database successfully")

        # Query to get disease name, plate count, and individual S3 URLs
        query = """
        SELECT disease_name, disease_uri
        FROM Disease_Detection_Results
        WHERE user_id = %s
        ORDER BY disease_name
        """
        logger.info(f"Executing query: {query}")
        cursor.execute(query, (user_id,))
        results = cursor.fetchall()
        logger.info(f"Query executed successfully. Found {len(results)} records.")

        # Format the results
        response = []
        for row in results:
            disease_name, disease_uri = row
            response.append({
                "disease_name": disease_name,
                "disease_uri": disease_uri
            })

        # Close the database connection
        cursor.close()
        connection.close()
        logger.info("Database connection closed")

        # Return the response
        return {
            'statusCode': 200,
            'body': json.dumps(response, indent=2)
        }

    except Exception as e:
        logger.error(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)})
        }
