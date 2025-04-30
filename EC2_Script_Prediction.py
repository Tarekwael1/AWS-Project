import pandas as pd
import pickle
import mysql.connector
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# RDS Configuration
rds_host = "yarb-mndf3sh-aktar-mn-keda.cp8kcmwa2o3e.us-east-1.rds.amazonaws.com"
rds_user = "admin"
rds_password = "Admin123"
rds_database = "USER1_db"

# Load the saved model
with open('/home/ubuntu/knn_model.pkl', 'rb') as model_file:
    loaded_model = pickle.load(model_file)
logger.info("Model loaded successfully.")

# Try loading the encoder
try:
    with open('encoder.pkl', 'rb') as encoder_file:
        encoder = pickle.load(encoder_file)  # Load the encoder if saved separately
    logger.info("Encoder loaded successfully.")
except FileNotFoundError as e:
    logger.warning("Encoder file not found. Skipping encoding.")
    encoder = None  # Set encoder to None if it's not available

def fetch_input_data():
    """Fetch the last 10 sensor readings from the Sensor_Readings table and calculate averages/max values."""
    try:
        # Connect to the RDS database
        connection = mysql.connector.connect(
            host=rds_host,
            user=rds_user,
            password=rds_password,
            database=rds_database
        )
        logger.info("Connected to the database.")

        with connection.cursor(dictionary=True) as cursor:
            # Fetch the last 10 sensor readings
            cursor.execute("""
                SELECT 
                    temperature, humidity, light_intensity, 
                    red_light_intensity, blue_light_intensity, 
                    far_red_light_intensity, air_flow_level, 
                    CO2, solution_level, ph, ec
                FROM Sensor_Readings
                ORDER BY timestamp DESC
                LIMIT 10;
            """)
            sensor_data = cursor.fetchall()

            if not sensor_data:
                logger.error("No sensor data found in the Sensor_Readings table.")
                return None

            # Convert the sensor data to a DataFrame
            sensor_df = pd.DataFrame(sensor_data)

            # Calculate average and max values for relevant features
            input_data = {
                "avg_temperature": sensor_df["temperature"].mean(),
                "max_temperature": sensor_df["temperature"].max(),
                "avg_humidity": sensor_df["humidity"].mean(),
                "max_humidity": sensor_df["humidity"].max(),
                "avg_light_intensity": sensor_df["light_intensity"].mean(),
                "max_light_intensity": sensor_df["light_intensity"].max(),
                "avg_red_light": sensor_df["red_light_intensity"].mean(),
                "max_red_light": sensor_df["red_light_intensity"].max(),
                "avg_blue_light": sensor_df["blue_light_intensity"].mean(),
                "max_blue_light": sensor_df["blue_light_intensity"].max(),
                "avg_far_red": sensor_df["far_red_light_intensity"].mean(),
                "max_far_red": sensor_df["far_red_light_intensity"].max(),
                "avg_air_flow": sensor_df["air_flow_level"].mean(),
                "max_air_flow": sensor_df["air_flow_level"].max(),
                "avg_CO2": sensor_df["CO2"].mean(),
                "max_CO2": sensor_df["CO2"].max(),
                "avg_solution_level": sensor_df["solution_level"].mean(),
                "max_solution_level": sensor_df["solution_level"].max(),
                "avg_ph": sensor_df["ph"].mean(),
                "max_ph": sensor_df["ph"].max(),
                "avg_ec": sensor_df["ec"].mean(),
                "max_ec": sensor_df["ec"].max(),
            }

            # Add default values for missing data
            default_values = {
                "plant_size": "medium",  # Default plant size
                "air_flow": "moderate",  # Default air flow
            }
            input_data.update(default_values)

            return input_data

    except Exception as e:
        logger.error(f"Error fetching input data: {e}")
        return None
    finally:
        # Close the database connection
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            logger.info("Database connection closed.")

def fetch_plant_id(plant_name):
    """Fetch the plant_id for a given plant name from the Plants table."""
    try:
        # Connect to RDS MySQL database
        connection = mysql.connector.connect(
            host=rds_host,
            user=rds_user,
            password=rds_password,
            database=rds_database
        )
        logger.info("Connected to the database.")

        with connection.cursor(dictionary=True) as cursor:
            # SQL query to fetch plant_id based on plant_name
            query = "SELECT plant_id FROM Plants WHERE plant_name = %s;"
            cursor.execute(query, (plant_name,))
            result = cursor.fetchone()

            if not result:
                logger.warning(f"No plant_id found for plant_name: {plant_name}")
                return None

            return result["plant_id"]

    except Exception as e:
        logger.error(f"Error fetching plant_id: {e}")
        return None
    finally:
        # Close the database connection
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            logger.info("Database connection closed.")

def save_recommendation(result_name):
    try:
        connection = mysql.connector.connect(
            host=rds_host,
            user=rds_user,
            password=rds_password,
            database=rds_database
        )
        cursor = connection.cursor()

        update_query = """
            UPDATE predictions 
            SET predicted_plant = %s 
            WHERE recommendation_id = 1
        """
        logger.info(f"Executing query: {update_query} with value: {result_name}")
        cursor.execute(update_query, (result_name,))
        connection.commit()
        logger.info(f"Rows updated: {cursor.rowcount}")

    except mysql.connector.Error as err:
        logger.error(f"Error while updating recommendation: {err}")
    finally:
        if connection.is_connected():
            connection.close()


    """Update or insert the recommendation in the predictions table."""
    try:
        # Connect to RDS MySQL database
        connection = mysql.connector.connect(
            host=rds_host,
            user=rds_user,
            password=rds_password,
            database=rds_database
        )
        logger.info("Connected to the database.")

        with connection.cursor(dictionary=True) as cursor:
            # Step 1: Check if there is an existing recommendation
            cursor.execute("SELECT recommendation_id FROM predictions ORDER BY recommendation_id DESC LIMIT 1;")
            existing_row = cursor.fetchone()

            if existing_row:
                # If there is an existing recommendation (we update the most recent one)
                update_query = """
                UPDATE predictions 
                SET predicted_plant = %s, plant_id = %s
                WHERE recommendation_id = %s;
                """
                cursor.execute(update_query, (result_name, plant_id, existing_row['recommendation_id']))
                logger.info(f"Updated prediction: ID={existing_row['recommendation_id']}, Plant={result_name}, Plant ID={plant_id}")
            else:
                # If no rows exist, insert a new recommendation
                insert_query = """
                INSERT INTO predictions (predicted_plant, plant_id)
                VALUES (%s, %s);
                """
                cursor.execute(insert_query, (result_name, plant_id))
                logger.info(f"Inserted new prediction: Plant={result_name}, Plant ID={plant_id}")
            
            connection.commit()

    except Exception as e:
        logger.error(f"Error saving recommendation: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            logger.info("Database connection closed.")

    """Update or insert the recommendation in the Recommendation_Plants table."""
    try:
        # Connect to RDS MySQL database
        connection = mysql.connector.connect(
            host=rds_host,
            user=rds_user,
            password=rds_password,
            database=rds_database
        )
        logger.info("Connected to the database.")

        with connection.cursor() as cursor:
            # Step 1: Check if there is an existing recommendation (based on your logic, maybe the most recent row)
            cursor.execute("SELECT recommendation_id FROM predictions ORDER BY recommendation_id DESC LIMIT 1;")
            existing_row = cursor.fetchone()

            if existing_row:
                # If there is an existing recommendation (we update the most recent one)
                update_query = """
                UPDATE predictions 
                SET predicted_Plant = %s
                WHERE recommendation_id = 1;
                """
                cursor.execute(update_query, (result_name, plant_id, existing_row['recommendation_id']))
                logger.info(f"Recommendation updated: {result_name} (Plant ID: {plant_id})")
            else:
                # If no rows exist, insert a new recommendation
                insert_query = """
                INSERT INTO predictions (predicted_plant, plant_id)
                VALUES (%s, %s);
                """
                cursor.execute(insert_query, (result_name, plant_id))
                logger.info(f"New recommendation inserted: {result_name} (Plant ID: {plant_id})")
            
            connection.commit()

    except Exception as e:
        logger.error(f"Error updating recommendation: {e}")
    finally:
        # Close the database connection
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            logger.info("Database connection closed.")


def predict_plant(input_data):
    """Predict the plant name based on input features and update the recommendation."""
    # Create a DataFrame with the input features
    input_df = pd.DataFrame([input_data])

    # Preprocess the data
    categorical_features = ['plant_size', 'air_flow']
    numerical_features = input_df.columns.difference(categorical_features)

    numerical_imputer = SimpleImputer(strategy='mean')
    input_df[numerical_features] = numerical_imputer.fit_transform(input_df[numerical_features])

    categorical_imputer = SimpleImputer(strategy='most_frequent')
    input_df[categorical_features] = categorical_imputer.fit_transform(input_df[categorical_features])

    # Apply one-hot encoding if encoder is available
    if encoder:
        try:
            encoded_features = encoder.transform(input_df[categorical_features])
            encoded_feature_names = encoder.get_feature_names_out(categorical_features)

            input_df = input_df.drop(categorical_features, axis=1)
            input_df = pd.concat([input_df, pd.DataFrame(encoded_features, columns=encoded_feature_names, index=input_df.index)], axis=1)
        except Exception as e:
            logger.error(f"Error during encoding: {e}")
            return None
    else:
        logger.warning("Skipping encoding as encoder is not available.")

    # Reorder features to match training data order
    input_df = input_df.reindex(columns=loaded_model.feature_names_in_)

    # Handle NaN values if any
    if input_df.isnull().values.any():
        logger.warning("Warning: There are still NaN values in the input data.")
        input_df = input_df.fillna(0)

    # Make the prediction
    prediction = loaded_model.predict(input_df)[0]

    # Fetch the plant_id for the predicted plant
    plant_id = fetch_plant_id(prediction)

    save_recommendation(prediction)


    return prediction

def main():
    # Fetch input data from RDS
    input_data = fetch_input_data()
    if not input_data:
        return

    # Make predictions for each input
    prediction = predict_plant(input_data)
    if prediction:
        logger.info(f"Predicted plant: {prediction}")
    else:
        logger.error("Failed to make prediction.")

if __name__ == "__main__":
    main()