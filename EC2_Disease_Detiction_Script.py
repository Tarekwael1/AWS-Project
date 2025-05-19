import os
import time
import boto3
import logging
import pymysql  # Use pymysql for MySQL
from roboflow import Roboflow

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set logging level to DEBUG
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/tmp/model_processor.log"),  # Log to a writable file in /tmp
        logging.StreamHandler()  # Log to the console
    ]
)
 
# Initialize Roboflow API
rf = Roboflow(api_key="MHOwGJ6gNlwpudPBxOmc")
project = rf.workspace().project("lavender-disease")
model = project.version(1).model

# Initialize S3 client
s3 = boto3.client('s3')

# Database connection details (replace with your RDS credentials)
db_config = {
    'host': 'yarb-mndf3sh-aktar-mn-keda.cp8kcmwa2o3e.us-east-1.rds.amazonaws.com',
    'user': 'admin',
    'password': 'Admin123',
    'database': 'main_db',
    'cursorclass': pymysql.cursors.DictCursor  # Ensure the results are returned as a dictionary
}

def save_to_rds(disease_name, detection_id, s3_url):
    connection = None
    try:
        # Connect to the database
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()
        logging.info("Connected to the database successfully")
        
        # Insert data into the Disease_Detection_Results table
        query = """
        INSERT INTO Disease_Detection_Results (disease_name, detection_id, s3_url)
        VALUES (%s, %s, %s)
        """
        cursor.execute(query, (disease_name, detection_id, s3_url))
        logging.info(f"Executed query: {query} with values: {disease_name}, {detection_id}, {s3_url}")
        
        # Commit the transaction
        connection.commit()
        logging.info(f"Data saved to RDS: {disease_name}, {detection_id}, {s3_url}")
        
    except Exception as e:
        logging.error(f"Error saving to RDS: {e}")
    finally:
        # Close the database connection
        if connection:
            cursor.close()
            connection.close()
            logging.info("Database connection closed")

def clear_output_bucket(output_bucket):
    """Delete all objects in the output S3 bucket."""
    try:
        logging.info(f"Clearing output S3 bucket: {output_bucket}")
        response = s3.list_objects_v2(Bucket=output_bucket)
        if 'Contents' in response:
            for obj in response['Contents']:
                s3.delete_object(Bucket=output_bucket, Key=obj['Key'])
                logging.info(f"Deleted object: {obj['Key']}")
        logging.info(f"Output S3 bucket cleared: {output_bucket}")
    except Exception as e:
        logging.error(f"Error clearing output S3 bucket: {e}")

def clear_rds_table():
    """Delete all records from the Disease_Detection_Results table in RDS."""
    connection = None
    try:
        # Connect to the database
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()
        logging.info("Connected to the database successfully")
        
        # Delete all records from the Disease_Detection_Results table
        query = "DELETE FROM Disease_Detection_Results"
        cursor.execute(query)
        connection.commit()
        logging.info("All records deleted from RDS table: Disease_Detection_Results")
        
    except Exception as e:
        logging.error(f"Error clearing RDS table: {e}")
    finally:
        # Close the database connection
        if connection:
            cursor.close()
            connection.close()
            logging.info("Database connection closed")

def process_images():
    # Define input and output buckets
    input_bucket = "camera-imagess"  # Bucket where camera uploads images
    output_bucket = "prediction-resultss"  # Bucket to save disease-detected images

    # Clear the output bucket and RDS table before processing new images
    clear_output_bucket(output_bucket)
    clear_rds_table()

    while True:
        try:
            # List objects in the input bucket
            logging.info("Listing objects in input S3 bucket")
            response = s3.list_objects_v2(Bucket=input_bucket)
            
            # Check if the bucket is empty
            if 'Contents' not in response or len(response['Contents']) == 0:
                logging.info("Input S3 bucket is empty. Stopping the script.")
                break  # Exit the loop if the bucket is empty

            for obj in response['Contents']:
                object_key = obj['Key']
                logging.info(f"Processing image: {object_key}")
                
                # Download the image from the input bucket to /tmp
                local_image_path = f"/tmp/{os.path.basename(object_key)}"
                logging.info(f"Downloading image to: {local_image_path}")
                s3.download_file(input_bucket, object_key, local_image_path)
                logging.info(f"Image downloaded: {local_image_path}")
                
                # Perform prediction
                logging.info("Running model prediction")
                prediction = model.predict(local_image_path, confidence=40, overlap=30)
                logging.info("Prediction completed")
                
                # Extract the predicted disease name
                if prediction.json()['predictions']:
                    disease_name = prediction.json()['predictions'][0]['class']  # Get the predicted disease name
                    disease_name = disease_name.replace(" ", "_").lower()  # Format the disease name
                else:
                    disease_name = "unknown"  # Default if no prediction is found
                
                # Log the prediction result
                logging.info(f"Predicted disease: {disease_name}")
                
                # Skip saving to output bucket and RDS if the disease is unknown
                if disease_name == "unknown":
                    logging.info(f"Skipping saving for unknown prediction: {object_key}")
                else:
                    # Generate a unique ID (e.g., timestamp)
                    unique_id = int(time.time())
                    
                    # Generate the result image name
                    result_image_name = f"predictions/{disease_name}_predicted_{unique_id}.jpg"
                    
                    # Save the prediction image to /tmp
                    prediction_image_path = f"/tmp/{os.path.basename(result_image_name)}"
                    logging.info(f"Saving prediction image: {prediction_image_path}")
                    prediction.save(prediction_image_path)
                    logging.info(f"Prediction image saved: {prediction_image_path}")
                    
                    # Upload the prediction image to the output bucket
                    logging.info(f"Uploading prediction image to output S3 bucket: {result_image_name}")
                    s3.upload_file(prediction_image_path, output_bucket, result_image_name)
                    logging.info(f"Prediction image uploaded to output S3 bucket: {result_image_name}")
                    
                    # Generate the S3 URL for the result image
                    s3_url = f"https://{output_bucket}.s3.amazonaws.com/{result_image_name}"
                    
                    # Save the data to RDS
                    save_to_rds(disease_name, str(unique_id), s3_url)
                
                # Delete the processed image from the input bucket
                logging.info(f"Deleting processed image from input S3 bucket: {object_key}")
                s3.delete_object(Bucket=input_bucket, Key=object_key)
                logging.info(f"Image deleted from input S3 bucket: {object_key}")
                
                # Clean up temporary files
                logging.info(f"Deleting temporary files: {local_image_path}")
                if os.path.exists(local_image_path):
                    os.remove(local_image_path)
                    logging.info(f"Deleted temporary file: {local_image_path}")
                if 'prediction_image_path' in locals() and os.path.exists(prediction_image_path):
                    os.remove(prediction_image_path)
                    logging.info(f"Deleted temporary file: {prediction_image_path}")
            
            # Wait before checking for new images again
            time.sleep(10)
        except Exception as e:
            logging.error(f"Error in process_images: {e}")

if __name__ == "__main__":
    logging.info("Starting model processing script")
    process_images()