import pymysql
import boto3
import csv
import io
import json

def lambda_handler(event, context):
    # 1. Retrieve user_id from the event
    body = json.loads(event.get("body", "{}"))
    user_id = body.get("user_id")
    
    if not user_id:
        return {'statusCode': 400, 'body': '❌ Missing user_id'}

    print(f"Received request for user_id: {user_id}")

    # 2. Database connection parameters
    host = 'yarb-mndf3sh-aktar-mn-keda.cp8kcmwa2o3e.us-east-1.rds.amazonaws.com'
    user = 'admin'
    password = 'Admin123'
    db_name = 'main_db'

    # 3. Connect to RDS MySQL
    try:
        conn = pymysql.connect(host=host, user=user, password=password, db=db_name)
        cursor = conn.cursor()
        print("✅ Connected to database.")
    except Exception as e:
        return {'statusCode': 500, 'body': f'❌ Database connection failed: {str(e)}'}

    # 4. Execute the query on Historical_Data filtered by user_id
    query = """
        SELECT plant_id,
               plate_id,
               user_id,
               unit_id,
               timestamp,
               temperature,
               humidity,
               light_intensity,
               nutrient_level,
               ph,
               ec,
               alerts,
               diseases_detected,
               harvested,
               biomass
        FROM Historical_Data
        WHERE user_id = %s
        ORDER BY timestamp DESC
        LIMIT 100
    """
    
    try:
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        print(f"✅ Retrieved {len(rows)} rows for user_id {user_id}.")
    except Exception as e:
        cursor.close()
        conn.close()
        return {'statusCode': 500, 'body': f'❌ Query execution failed: {str(e)}'}

    # 5. Define column headers
    columns = [
        'plant_id', 'plate_id', 'user_id', 'unit_id', 'timestamp', 'temperature',
        'humidity', 'light_intensity', 'nutrient_level', 'ph', 'ec',
        'alerts', 'diseases_detected', 'harvested', 'biomass'
    ]

    # 6. Create CSV in memory
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(columns)
    writer.writerows(rows)

    # 7. Upload to S3
    s3 = boto3.client('s3')
    bucket_name = 'guetest'
    s3_key = f'guetest/Landing-zone/RL_Data/historical_data_user_{user_id}.csv'

    try:
        # Delete previous version if exists
        try:
            s3.head_object(Bucket=bucket_name, Key=s3_key)
            s3.delete_object(Bucket=bucket_name, Key=s3_key)
            print("ℹ️ Previous file deleted.")
        except s3.exceptions.ClientError as e:
            if e.response['Error']['Code'] != '404':
                raise

        # Upload new file
        s3.put_object(Bucket=bucket_name, Key=s3_key, Body=csv_buffer.getvalue())
        print(f"✅ File uploaded to: s3://{bucket_name}/{s3_key}")
    except Exception as e:
        return {'statusCode': 500, 'body': f'❌ Failed to upload to S3: {str(e)}'}

    # 8. Cleanup
    cursor.close()
    conn.close()

    return {
        'statusCode': 200,
        'body': f'✅ Exported {len(rows)} rows to s3://{bucket_name}/{s3_key}'
    }
