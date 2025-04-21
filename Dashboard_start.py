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
db_name = "USER1_db"

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

        # Initialize response with default values
        plates_response = {
            "plate1": {
                "plate_id": "empty",
                "plate_name": "empty",
                "plant_name": "empty",
                "harvested": "empty"
            },
            "plate2": {
                "plate_id": "empty",
                "plate_name": "empty",
                "plant_name": "empty",
                "harvested": "empty"
            }
        }

        # Update response with data from the database
        for plate in plates:
            plate_id = plate["plate_id"]
            if plate_id in [1, 2]:  # Only process plates 1 and 2
                # Query to fetch the plant name and harvested status for the current plate
                plant_query = """
                SELECT 
                    plant_name,
                    harvested
                FROM 
                    Plants
                WHERE 
                    plate_id = %s and harvested = 0;
                """
                with connection.cursor() as cursor:
                    logger.info("Executing plant query for plate_id %s", plate_id)
                    cursor.execute(plant_query, (plate_id,))
                    plant = cursor.fetchone()  # Fetch only one plant
                    logger.info("Plant query result for plate_id %s: %s", plate_id, plant)

                # Extract the plant name and harvested status (or set to "empty" if no plant is found)
                plant_name = plant["plant_name"] if plant and plant["plant_name"] else "empty"
                harvested = plant["harvested"] if plant and "harvested" in plant else "empty"

                # Update the response for the plate
                plates_response[f"plate{plate_id}"] = {
                    "plate_id": plate_id if plate_id else "empty",
                    "plate_name": plate["plate_name"] if plate["plate_name"] else "empty",
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