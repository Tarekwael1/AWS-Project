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
    try:
        # Parse the request body
        body = json.loads(event.get("body", "{}"))
        plate_name = body.get("plate_name")  # Example: "Plate 1" or "Plate 2"
        user_id = body.get("user_id")  # Example: "123" (string)

        if not plate_name or not user_id:
            raise ValueError("'plate_name' and 'user_id' are required.")

        logger.info("Received request to update harvest status for plate %s for user %s", plate_name, user_id)

        # Connect to the RDS database
        connection = pymysql.connect(
            host=rds_host,
            user=username,
            password=password,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        logger.info("Connected to the database.")

        # Step 1: Get the plate_id from the Plates table using plate_name
        plate_query = """
        SELECT plate_id
        FROM Plates
        WHERE plate_name = %s AND user_id = %s;
        """
        with connection.cursor() as cursor:
            cursor.execute(plate_query, (plate_name, user_id))
            plate = cursor.fetchone()
            if not plate:
                raise ValueError(f"Plate with name '{plate_name}' not found for user_id '{user_id}'.")
            plate_id = plate["plate_id"]
            logger.info("Found plate_id %s for plate_name %s and user_id %s.", plate_id, plate_name, user_id)

        # Step 2: Update the Plants table to mark plants on this plate as harvested
        update_query = """
        UPDATE Plants
        SET harvested = TRUE, harvest_timestamp = NOW()
        WHERE plate_id = %s;
        """
        with connection.cursor() as cursor:
            cursor.execute(update_query, (plate_id,))
            connection.commit()
            logger.info("Updated harvest status for plate_id %s.", plate_id)

        # Return a success response
        response = {
            "statusCode": 200,
            "body": json.dumps({"message": f"Harvest status updated for plate {plate_name} (plate_id: {plate_id}) successfully."})
        }

    except pymysql.MySQLError as e:
        logger.error("Database error: %s", e)
        response = {
            "statusCode": 500,
            "body": json.dumps({"error": "Database operation failed.", "details": str(e)})
        }
    except ValueError as e:
        logger.error("Validation error: %s", e)
        response = {
            "statusCode": 400,
            "body": json.dumps({"error": str(e)})
        }
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        response = {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error.", "details": str(e)})
        }
    finally:
        try:
            if connection:
                connection.close()
                logger.info("Database connection closed.")
        except NameError:
            pass

    return response
