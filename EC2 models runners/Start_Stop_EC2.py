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
sns = boto3.client('sns', region_name=region)
sns_topic_arn = 'arn:aws:sns:us-east-1:116981773526:Notifications'  # Replace with your SNS Topic ARN

# RDS Database Configuration
rds_host = 'yarb-mndf3sh-aktar-mn-keda.cp8kcmwa2o3e.us-east-1.rds.amazonaws.com'
rds_user = 'admin'
rds_password = 'Admin123'
rds_database = 'main_db'

def lambda_handler(event, context):
    try:
        print("Starting Lambda execution...")

        body = json.loads(event.get('body', '{}'))
        user_id = str(body.get('user_id', None))
        if not user_id:
            raise ValueError("user_id not provided in the event body.")

        print(f"Received user_id: {user_id}")

        instance_status = ec2.describe_instance_status(InstanceIds=instances)
        if not instance_status['InstanceStatuses'] or instance_status['InstanceStatuses'][0]['InstanceState']['Name'] != 'running':
            print("Starting EC2 instance...")
            ec2.start_instances(InstanceIds=instances)
            time.sleep(60)
        else:
            print("EC2 instance is already running.")

        command = f"sudo -u ubuntu /usr/bin/python3 /home/ubuntu/prediction_code.py {user_id}"
        response = ssm_client.send_command(
            InstanceIds=instances,
            DocumentName='AWS-RunShellScript',
            Parameters={'commands': [command]},
        )
        command_id = response['Command']['CommandId']

        for _ in range(10):
            time.sleep(10)
            output = ssm_client.get_command_invocation(
                CommandId=command_id,
                InstanceId=instances[0],
            )
            if output['Status'] in ['Success', 'Failed']:
                break

        print(f"EC2 Output: {output.get('StandardOutputContent')}")
        print(f"EC2 Error: {output.get('StandardErrorContent')}")

        prediction_result = "No result found."
        try:
            connection = mysql.connector.connect(
                host=rds_host,
                user=rds_user,
                password=rds_password,
                database=rds_database
            )
            cursor = connection.cursor()
            query = "SELECT prediction_output FROM predicions WHERE user_id = %s LIMIT 1"
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()

            if result:
                prediction_result = result[0]
                print(f"Prediction result from RDS: {prediction_result}")

            cursor.close()
            connection.close()

        except Error as e:
            print(f"RDS Error: {e}")
            sns.publish(
                TopicArn=sns_topic_arn,
                Message=f"RDS Error for user_id {user_id}:\n{str(e)}",
                Subject='Prediction Error Notification'
            )
            return {
                'statusCode': 500,
                'body': json.dumps({'error': str(e)})
            }

        # Send success email
        message = f"Prediction completed for user_id {user_id}.\nResult: {prediction_result}"
        sns.publish(
            TopicArn=sns_topic_arn,
            Message=message,
            Subject='Prediction Result Notification'
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'prediction_result': prediction_result})
        }

    except Exception as e:
        print(f"Lambda error: {e}")
        sns.publish(
            TopicArn=sns_topic_arn,
            Message=f"Lambda execution error for user_id {user_id if 'user_id' in locals() else 'N/A'}:\n{str(e)}",
            Subject='Prediction Lambda Failure'
        )
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
