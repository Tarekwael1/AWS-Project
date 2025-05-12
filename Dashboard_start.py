import json
import pymysql
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# RDS Configuration
rds_host = "yarb-mndf3sh-aktar-mn-keda.cp8kcmwa2o3e.us-east-1.rds.amazonaws.com"
username = "admin"
password = "Admin123"
db_name = "main_db"

def lambda_handler(event, context):
    connection = None
    try:
        logger.info("Received event: %s", json.dumps(event))

        # Parse user_id from the incoming request body
        if 'body' in event:
            body = json.loads(event['body'])
            user_id = body.get('user_id')
        else:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing request body."})
            }

        if not user_id:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing user_id in request."})
            }

        logger.info(f"Received user_id: {user_id}")

        # Connect to the database
        connection = pymysql.connect(
            host=rds_host,
            user=username,
            password=password,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        logger.info("Database connection established.")

        # Query to fetch plates associated with the user
        plates_query = """
        SELECT 
            plate_id,
            plate_name,
            unit_id,
            planting_method_id
        FROM 
            Plates
        WHERE 
            user_id = %s
        ORDER BY 
            plate_id ASC;
        """

        with connection.cursor() as cursor:
            logger.info("Executing plates query for user_id %s", user_id)
            cursor.execute(plates_query, (user_id,))
            plates = cursor.fetchall()
            logger.info("Plates query result: %s", plates)

        plates_response = {}
        plate_count = 0

        for plate in plates:
            plate_id = plate["plate_id"]
            plate_count += 1

            # Query to fetch the plant name and harvested status for the current plate
            plant_query = """
            SELECT 
                plant_name,
                harvested
            FROM 
                Plants
            WHERE 
                plate_id = %s AND harvested = 0 AND user_id = %s;
            """
            with connection.cursor() as cursor:
                logger.info("Executing plant query for plate_id %s", plate_id)
                cursor.execute(plant_query, (plate_id, user_id))
                plant = cursor.fetchone()
                logger.info("Plant query result: %s", plant)

            plant_name = plant["plant_name"] if plant and plant.get("plant_name") else "empty"
            harvested = plant["harvested"] if plant and "harvested" in plant else "empty"

            plates_response[f"plate{plate_id}"] = {
                "plate_id": plate_id,
                "plate_name": plate.get("plate_name", "empty"),
                "unit_id": plate.get("unit_id", "empty"),
                "planting_method_id": plate.get("planting_method_id", "empty"),
                "plant_name": plant_name,
                "harvested": harvested
            }

        result = {
            "user_id": user_id,
            "number_of_plates": plate_count,
            "plates": plates_response
        }

        return {
            "statusCode": 200,
            "body": json.dumps(result, default=str)
        }

    except pymysql.MySQLError as e:
        logger.error("MySQL error: %s", e)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Database connection failed", "details": str(e)})
        }
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error", "details": str(e)})
        }
    finally:
        if connection:
            connection.close()
            logger.info("Database connection closed.")
