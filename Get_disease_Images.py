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
    'db': 'user_auth',
}

def lambda_handler(event, context):
    try:
        # Connect to the database
        logger.info("Connecting to the database...")
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()
        logger.info("Connected to the database successfully")

        # Query to get disease name, plate count, and individual S3 URLs
        query = """
        SELECT disease_name, s3_url
        FROM disease_predicted
        ORDER BY disease_name
        """
        logger.info(f"Executing query: {query}")
        cursor.execute(query)
        results = cursor.fetchall()
        logger.info(f"Query executed successfully. Found {len(results)} records.")

        # Format the results
        response = []
        for row in results:
            disease_name, s3_url = row
            response.append({
                "disease_name": disease_name,
                "s3_url": s3_url
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