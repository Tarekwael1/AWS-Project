import sys
import pandas as pd
import pickle
import logging
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sqlalchemy import create_engine
import mysql.connector

# -------------------- Configuration --------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

rds_host = "yarb-mndf3sh-aktar-mn-keda.cp8kcmwa2o3e.us-east-1.rds.amazonaws.com"
rds_user = "admin"
rds_password = "Admin123"
rds_database = "main_db"

# SQLAlchemy DB URI
db_uri = f"mysql+mysqlconnector://{rds_user}:{rds_password}@{rds_host}/{rds_database}"
engine = create_engine(db_uri)

# -------------------- Load Model --------------------
try:
    with open('/home/ubuntu/knn_model.pkl', 'rb') as model_file:
        model = pickle.load(model_file)
    logger.info("Model loaded.")
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    sys.exit(1)

encoder = None
try:
    with open('/home/ubuntu/encoder.pkl', 'rb') as f:
        encoder = pickle.load(f)
    logger.info("Encoder loaded.")
except FileNotFoundError:
    logger.warning("Encoder not found, skipping encoding.")

# -------------------- Helper Functions --------------------

def fetch_sensor_data(user_id):
    """Fetch and aggregate sensor data for the given user_id."""
    try:
        query = """
            SELECT temperature, humidity, light_intensity, 
                   red_light_intensity, blue_light_intensity, 
                   far_red_light_intensity, air_flow_level, 
                   CO2, solution_level, ph, ec
            FROM Sensor_Readings
            WHERE user_id = %s
            ORDER BY timestamp DESC
            LIMIT 10;
        """
        df = pd.read_sql(query, con=engine, params=(user_id,))
        if df.empty:
            logger.error("No sensor data for user.")
            return None

        # Aggregate features
        agg = {
            "avg_temperature": df["temperature"].mean(),
            "max_temperature": df["temperature"].max(),
            "avg_humidity": df["humidity"].mean(),
            "max_humidity": df["humidity"].max(),
            "avg_light_intensity": df["light_intensity"].mean(),
            "max_light_intensity": df["light_intensity"].max(),
            "avg_red_light": df["red_light_intensity"].mean(),
            "max_red_light": df["red_light_intensity"].max(),
            "avg_blue_light": df["blue_light_intensity"].mean(),
            "max_blue_light": df["blue_light_intensity"].max(),
            "avg_far_red": df["far_red_light_intensity"].mean(),
            "max_far_red": df["far_red_light_intensity"].max(),
            "avg_air_flow": df["air_flow_level"].mean(),
            "max_air_flow": df["air_flow_level"].max(),
            "avg_CO2": df["CO2"].mean(),
            "max_CO2": df["CO2"].max(),
            "avg_solution_level": df["solution_level"].mean(),
            "max_solution_level": df["solution_level"].max(),
            "avg_ph": df["ph"].mean(),
            "max_ph": df["ph"].max(),
            "avg_ec": df["ec"].mean(),
            "max_ec": df["ec"].max(),
            "plant_size": "medium",
            "air_flow": "moderate"
        }

        return agg

    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        return None

def predict_and_save(user_id, input_data):
    """Run prediction and save result."""
    input_df = pd.DataFrame([input_data])

    # Impute missing values
    num_features = input_df.columns.difference(['plant_size', 'air_flow'])
    input_df[num_features] = SimpleImputer(strategy='mean').fit_transform(input_df[num_features])
    input_df[['plant_size', 'air_flow']] = SimpleImputer(strategy='most_frequent').fit_transform(
        input_df[['plant_size', 'air_flow']]
    )

    # Encode
    if encoder:
        try:
            encoded = encoder.transform(input_df[['plant_size', 'air_flow']])
            encoded_df = pd.DataFrame(
                encoded,
                columns=encoder.get_feature_names_out(['plant_size', 'air_flow']),
                index=input_df.index
            )
            input_df.drop(['plant_size', 'air_flow'], axis=1, inplace=True)
            input_df = pd.concat([input_df, encoded_df], axis=1)
        except Exception as e:
            logger.error(f"Encoding failed: {e}")
            return
    else:
        logger.warning("Encoder is missing, skipping encoding.")
        input_df.drop(['plant_size', 'air_flow'], axis=1, errors='ignore', inplace=True)

    # Reorder columns to match model
    input_df = input_df.reindex(columns=model.feature_names_in_, fill_value=0)

    # Predict
    prediction = model.predict(input_df)[0]
    logger.info(f"Prediction: {prediction}")

    # Save to DB using mysql.connector
    try:
        conn = mysql.connector.connect(
            host=rds_host, user=rds_user, password=rds_password, database=rds_database
        )
        cursor = conn.cursor()
        insert_query = """
            INSERT INTO predicions (user_id, prediction_output)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE prediction_output = VALUES(prediction_output);
        """
        cursor.execute(insert_query, (user_id, prediction))
        conn.commit()
        logger.info("Prediction saved.")
    except Exception as e:
        logger.error(f"Error saving prediction: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()

# -------------------- Main --------------------
if __name__ == "__main__":
    if len(sys.argv) != 2:
        logger.error("Usage: python3 prediction_code.py <user_id>")
        sys.exit(1)

    user_id = sys.argv[1]
    logger.info(f"Received user_id: {user_id}")

    data = fetch_sensor_data(user_id)
    if data:
        predict_and_save(user_id, data)
    else:
        logger.error("No input data. Exiting.")
