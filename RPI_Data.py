#This script is used to read data from a Raspberry Pi and send it to a RDS database.

import json
import pymysql
import logging
from pymysql import Error as DBError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/tmp/lambda_handler.log"),  # Log to a file in /tmp
        logging.StreamHandler()  # Log to the console
    ]
)
logger = logging.getLogger()

# Database connection details (replace with your RDS credentials)
db_config = {
    'host': 'yarb-mndf3sh-aktar-mn-keda.cp8kcmwa2o3e.us-east-1.rds.amazonaws.com',
    'user': 'admin',
    'password': 'Admin123',
    'database': 'user_auth',
    'cursorclass': pymysql.cursors.DictCursor
}

def save_sensor_data(connection, sensors):
    """Save sensor data to the RDS database."""
    try:
        with connection.cursor() as cursor:
            # Insert sensor data into the sensors table
            query = """
            INSERT INTO sensors_data (
                plate1_temp, plate1_humidity, plate2_temp, plate2_humidity,
                plate1_light_visible, plate2_light_visible, ec, ph,
                water_level, nutrient_level
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                sensors["plate1_temp"], sensors["plate1_humidity"],
                sensors["plate2_temp"], sensors["plate2_humidity"],
                sensors["plate1_light_visible"], sensors["plate2_light_visible"],
                sensors["ec"], sensors["ph"],
                sensors["water_level"], sensors["nutrient_level"]
            ))
            logger.info("Sensor data saved to RDS")
    except Exception as e:
        logger.error(f"Error saving sensor data: {e}")
        raise

def validate_sensors(sensors):
    """Validate sensors data types."""
    # Sensors should be floats
    for key, value in sensors.items():
        if not isinstance(value, float):
            raise ValueError(f"Invalid type for sensor '{key}': expected float, got {type(value).__name__}")
    logger.info("Sensors validation passed")

def lambda_handler(event, context):
    try:
        # Log the raw event
        logger.info(f"Incoming event: {event}")

        # Parse the incoming payload
        payload = json.loads(event["body"])
        sensors = payload.get("sensors")

        if not sensors:
            raise ValueError("Missing 'sensors' in payload")

        # Validate sensors data
        validate_sensors(sensors)

        # Connect to the RDS database
        connection = pymysql.connect(**db_config)
        logger.info("Connected to the database successfully")

        # Save sensor data
        save_sensor_data(connection, sensors)

        # Commit the transaction
        connection.commit()

        return {
            'statusCode': 200,
            'body': json.dumps({"message": "Sensor data saved successfully"})
        }

    except ValueError as ve:
        logger.error(f"Value error: {ve}")
        return {
            'statusCode': 400,
            'body': json.dumps({"error": str(ve)})
        }
    except Exception as e:
        logger.error(f"Error in lambda_handler: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)})
        }
    finally:
        if 'connection' in locals() and connection:
            connection.close()
            logger.info("Database connection closed")
