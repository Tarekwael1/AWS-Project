import json
import pymysql
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# RDS Configuration (hardcoded credentials)
rds_host = "yarb-mndf3sh-aktar-mn-keda.cp8kcmwa2o3e.us-east-1.rds.amazonaws.com"
username = "admin"
password = "Admin123"
db_name = "main_db"

def lambda_handler(event, context):
    connection = None
    try:
        logger.info("Connecting to the database...")
        # Connect to the RDS database
        connection = pymysql.connect(
            host=rds_host,
            user=username, 
            password=password,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        logger.info("Database connection established.")

        # Query to fetch plates
        plates_query = """
        SELECT 
            plate_id,
            plate_name,
            unit_id,
            planting_method_id
        FROM 
            Plates
        ORDER BY 
            plate_id ASC;
        """

        with connection.cursor() as cursor:
            logger.info("Executing plates query: %s", plates_query)
            cursor.execute(plates_query)
            plates = cursor.fetchall()
            logger.info("Plates query result: %s", plates)

        # Dynamically build response for all plates
        plates_response = {}

        for plate in plates:
            plate_id = plate["plate_id"]

            # Query to fetch the plant name and harvested status for the current plate
            plant_query = """
            SELECT 
                plant_name,
                harvested
            FROM 
                Plants
            WHERE 
                plate_id = %s AND harvested = 0;
            """
            with connection.cursor() as cursor:
                logger.info("Executing plant query for plate_id %s", plate_id)
                cursor.execute(plant_query, (plate_id,))
                plant = cursor.fetchone()
                logger.info("Plant query result for plate_id %s: %s", plate_id, plant)

            # Prepare plant data
            plant_name = plant["plant_name"] if plant and plant.get("plant_name") else "empty"
            harvested = plant["harvested"] if plant and "harvested" in plant else "empty"

            # Dynamically name the key: e.g., "plate1", "plate2", etc.
            plates_response[f"plate{plate_id}"] = {
                "plate_id": plate_id,
                "plate_name": plate.get("plate_name", "empty"),
                "plant_name": plant_name,
                "harvested": harvested
            }

        # Return the response
        response = {
            "statusCode": 200,
            "body": json.dumps(plates_response, default=str)  # Serialize response
        }

    except pymysql.MySQLError as e:
        logger.error("MySQL error: %s", e)
        response = {
            "statusCode": 500,
            "body": json.dumps({"error": "Database connection failed", "details": str(e)})
        }
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        response = {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error", "details": str(e)})
        }
    finally:
        # Ensure the database connection is closed
        if connection:
            connection.close()
            logger.info("Database connection closed.")

    return response
