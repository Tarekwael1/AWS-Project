#This script will start the EC2 incstance if it is stopped and run the script (prediction_code.py) on the EC2 instance using SSM.
#This model predicts the plant type based on the input image and stores the result in an RDS database.
# Lambda function to start EC2 instance, run a script, and fetch results from RDS.
import boto3
import json
import time
import mysql.connector
from mysql.connector import Error

# AWS Region and Instance Details
region = 'us-east-1'
instances = ['i-0c0516d7f319e2d78']  # Replace with your EC2 instance ID

# EC2 and SSM Clients
ec2 = boto3.client('ec2', region_name=region)
ssm_client = boto3.client('ssm', region_name=region)

# RDS Database Configuration
rds_host = 'yarb-mndf3sh-aktar-mn-keda.cp8kcmwa2o3e.us-east-1.rds.amazonaws.com'  # Replace with your RDS endpoint
rds_user = 'admin'  # Replace with your RDS username
rds_password = 'Admin123'  # Replace with your RDS password
rds_database = 'USER1_db'  # Replace with your RDS database name

def lambda_handler(event, context):
    try:
        print("Starting Lambda execution...")

        # Start EC2 Instance (if not already running)
        print("Checking EC2 instance status...")
        instance_status = ec2.describe_instance_status(InstanceIds=instances)
        if not instance_status['InstanceStatuses'] or instance_status['InstanceStatuses'][0]['InstanceState']['Name'] != 'running':
            print("EC2 instance is not running. Starting instance...")
            ec2.start_instances(InstanceIds=instances)
            print(f"Started EC2 instance(s): {instances}")
            # Wait for the instance to be fully running
            print("Waiting for EC2 instance to be fully running...")
            time.sleep(60)  # Adjust the delay as needed
        else:
            print("EC2 instance is already running.")

        # Command to run the script on EC2
        command = "sudo -u ubuntu /usr/bin/python3 /home/ubuntu/prediction_code.py"
        print("Command to execute on EC2:", command)

        # Send command to EC2 instance via SSM
        print("Sending command to EC2 instance via SSM...")
        response = ssm_client.send_command(
            InstanceIds=instances,
            DocumentName='AWS-RunShellScript',
            Parameters={'commands': [command]},  # Pass the command as a list
        )
        command_id = response['Command']['CommandId']
        print(f"Command sent to EC2. Command ID: {command_id}")

        # Wait for the command to complete
        print("Waiting for command to complete...")
        for _ in range(10):  # Retry for up to 100 seconds (10 * 10 seconds)
            time.sleep(10)
            print(f"Checking command status (Attempt {_ + 1})...")
            output = ssm_client.get_command_invocation(
                CommandId=command_id,
                InstanceId=instances[0],
            )
            if output['Status'] in ['Success', 'Failed']:
                print(f"Command status: {output['Status']}")
                break

        print(f"EC2 Script Output: {output.get('StandardOutputContent')}")
        print(f"EC2 Script Error: {output.get('StandardErrorContent')}")

        # Check if the output is empty
        if not output.get('StandardOutputContent'):
            print("Warning: EC2 script output is empty. Possible reasons:")
            print("1. The script did not produce any output.")
            print("2. The script failed to execute.")
            print("3. The SSM agent did not return the output correctly.")
            print("4. The command did not complete successfully.")

        # Fetch the result from RDS
        print("Fetching result from RDS...")
        try:
            # Connect to RDS
            connection = mysql.connector.connect(
                host=rds_host,
                user=rds_user,
                password=rds_password,
                database=rds_database
            )
            cursor = connection.cursor()

            # Query the latest result from the database
            query = "SELECT predicted_Plant FROM predictions WHERE 1"
            cursor.execute(query)
            result = cursor.fetchone()

            if result:
                prediction_result = result[0]
                print(f"Prediction result from RDS: {prediction_result}")
            else:
                prediction_result = "No result found in the database."
                print(prediction_result)

            # Close the database connection
            cursor.close()
            connection.close()

        except Error as e:
            print(f"Error fetching result from RDS: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': str(e)})
            }

        # Return the result to the API
        return {
            'statusCode': 200,
            'body': json.dumps({
                'prediction_result': prediction_result
            })
        }

    except Exception as e:
        print(f"Error in Lambda execution: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }