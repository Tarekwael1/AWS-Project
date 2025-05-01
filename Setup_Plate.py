import json
import pymysql
import logging

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
        body = event.get("body")
        if not body:
            raise ValueError("Request body is missing.")

        try:
            body = json.loads(body)  # Parse the body as JSON
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in request body: {str(e)}")

        # Extract required fields
        plate_id = body.get("plate_id")
        plant_name = body.get("plant_name")
        plant_id = body.get("plant_id")
        age_in_weeks = body.get("age_in_weeks", 0)  # Default to 0 if not provided
        harvested = body.get("harvested", False)  # Default to False if not provided

        # Validate input
        if not plate_id or not plant_name or not plant_id:
            raise ValueError("'plate_id', 'plant_name', and 'plant_id' are required.")

        # Connect to the RDS database
        connection = pymysql.connect(
            host=rds_host,
            user=username,
            password=password,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        logger.info("Connected to the database.")

        with connection.cursor() as cursor:
            # Step 1: Check if the plant already exists in the Plants table
            cursor.execute(
                "SELECT * FROM Plants WHERE plant_id = %s;",
                (plant_id,)
            )
            plant = cursor.fetchone()

            if plant:
                # Step 2: Update the existing plant data
                cursor.execute(
                    """
                    UPDATE Plants
                    SET plant_name = %s, plate_id = %s, age_in_weeks = %s, harvested = %s
                    WHERE plant_id = %s;
                    """,
                    (plant_name, plate_id, age_in_weeks, harvested, plant_id)
                )
                connection.commit()
                logger.info("Updated plant_id %s with plant_name '%s' in plate %s.", plant_id, plant_name, plate_id)
            else:
                # Step 3: Insert the plant data if it doesn't exist
                cursor.execute(
                    """
                    INSERT INTO Plants (plant_id, plant_name, plate_id, age_in_weeks, harvested)
                    VALUES (%s, %s, %s, %s, %s);
                    """,
                    (plant_id, plant_name, plate_id, age_in_weeks, harvested)
                )
                connection.commit()  # Commit the insertion
                logger.info("Inserted plant_id %s with plant_name '%s' into plate %s.", plant_id, plant_name, plate_id)

        # Return success response
        return {
            "statusCode": 200,
            "body": json.dumps({"message": f"Plant '{plant_name}' with ID {plant_id} and age_in_weeks {age_in_weeks} updated/inserted in plate {plate_id} successfully."})
        }

    except pymysql.MySQLError as e:
        logger.error("Database error: %s", e)
        return {"statusCode": 500, "body": json.dumps({"error": "Database operation failed.", "details": str(e)})}
    except ValueError as e:
        logger.error("Validation error: %s", e)
        return {"statusCode": 400, "body": json.dumps({"error": str(e)})}
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        return {"statusCode": 500, "body": json.dumps({"error": "Internal server error.", "details": str(e)})}
    finally:
        # Close the database connection
        if 'connection' in locals() and connection.open:
            connection.close()
            logger.info("Database connection closed.")