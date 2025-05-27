import json
import pymysql
import logging
from pymysql import Error as DBError

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/tmp/lambda_handler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

# Database config
db_config = {
    'host': 'yarb-mndf3sh-aktar-mn-keda.cp8kcmwa2o3e.us-east-1.rds.amazonaws.com',
    'user': 'admin',
    'password': 'Admin123',
    'database': 'main_db',
    'cursorclass': pymysql.cursors.DictCursor
}

def lambda_handler(event, context):
    try:
        logger.info(f"Received event: {event}")
        payload = json.loads(event.get("body", "{}"))

        # Extract required sensor fields
        required_fields = [
            "plate_id", "plant_id", "user_id", "unit_id", "timestamp",
            "temperature", "humidity", "light_intensity",
            "solution_level", "ph", "ec"
        ]
        
        # Optional fields with default None
        optional_fields = [
            "anomly_detection", "red_light_intensity", "blue_light_intensity",
            "far_red_light_intensity", "air_flow_level", "CO2"
        ]

        # Validate required fields
        for field in required_fields:
            if field not in payload:
                raise ValueError(f"Missing required field: {field}")

        # Prepare all fields
        all_fields = required_fields + optional_fields
        values = tuple(payload.get(field) for field in all_fields)

        query = f"""
            INSERT INTO Sensor_Readings (
                {', '.join(all_fields)}
            ) VALUES (
                {', '.join(['%s'] * len(all_fields))}
            )
        """

        # Connect and insert
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            cursor.execute(query, values)
            connection.commit()

        logger.info("Sensor data inserted into Sensor_Readings.")
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Sensor reading inserted successfully."})
        }

    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(ve)})
        }
    except DBError as db_err:
        logger.error(f"Database error: {db_err}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Database error", "details": str(db_err)})
        }
    except Exception as e:
        logger.error(f"Unhandled error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Unexpected error", "details": str(e)})
        }
    finally:
        if 'connection' in locals() and connection:
            connection.close()
            logger.info("Database connection closed.")
