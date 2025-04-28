import boto3
import csv
import io
from datetime import datetime

def lambda_handler(event, context):
    # 1. Create sample sensor data (or you will receive this from Raspberry Pi)
    data = [
        {"timestamp": str(datetime.now()), "temperature": 24.5, "light_period": 16, "pH": 6.2, "RH": 60, "EC": 2.5, "water_duration": 20},
        {"timestamp": str(datetime.now()), "temperature": 25.0, "light_period": 16, "pH": 6.1, "RH": 62, "EC": 2.6, "water_duration": 21},
    ]
    
    # 2. Build a CSV file in memory
    csv_buffer = io.StringIO()
    csv_writer = csv.DictWriter(csv_buffer, fieldnames=data[0].keys())
    csv_writer.writeheader()
    csv_writer.writerows(data)
    
    # 3. Upload the CSV to S3
    s3_client = boto3.client('s3')
    bucket_name = 'guetest'  # << Replace with your bucket name
    s3_key = 'guetest/Landing-zone/RL_Data/sensor_data.csv'  # << Where to save inside S3
    
    s3_client.put_object(
        Bucket=bucket_name,
        Key=s3_key,
        Body=csv_buffer.getvalue()
    )
    
    return {
        'statusCode': 200,
        'body': f'CSV file saved to S3://{bucket_name}/{s3_key}'
    }
