import boto3
import json
import time
import logging

# AWS Region and EC2 instance details
region = 'us-east-1'
instances = ['i-0c0516d7f319e2d78']  # Replace with your EC2 instance ID

# AWS clients
ec2 = boto3.client('ec2', region_name=region)
ssm_client = boto3.client('ssm', region_name=region)

def lambda_handler(event, context):
    try:
        logging.info("Starting disease detection Lambda execution...")

        # Start EC2 instance if not running
        instance_status = ec2.describe_instance_status(InstanceIds=instances)
        if not instance_status['InstanceStatuses'] or instance_status['InstanceStatuses'][0]['InstanceState']['Name'] != 'running':
            logging.info("EC2 instance is not running. Starting instance...")
            ec2.start_instances(InstanceIds=instances)
            logging.info(f"Started EC2 instance(s): {instances}")
            logging.info("Waiting for EC2 instance to be fully running (about 60 seconds)...")
            time.sleep(60)  # Wait for instance to start fully
        else:
            logging.info("EC2 instance is already running.")

        # Command to run disease detection script on EC2 (adjust path if needed)
        command = "sudo -u ubuntu /usr/bin/python3 /home/ubuntu/disease_detection_model.py"
        logging.info(f"Sending command to EC2: {command}")

        # Send command to EC2 instance via SSM
        response = ssm_client.send_command(
            InstanceIds=instances,
            DocumentName='AWS-RunShellScript',
            Parameters={'commands': [command]},
        )
        command_id = response['Command']['CommandId']
        logging.info(f"Command sent. Command ID: {command_id}")

        # Wait for command to complete, checking status every 10 seconds (max 10 attempts)
        for attempt in range(10):
            time.sleep(10)
            output = ssm_client.get_command_invocation(
                CommandId=command_id,
                InstanceId=instances[0],
            )
            status = output['Status']
            logging.info(f"Attempt {attempt + 1}: Command status = {status}")
            if status in ['Success', 'Failed', 'Cancelled', 'TimedOut']:
                break

        # Log outputs
        stdout = output.get('StandardOutputContent', '')
        stderr = output.get('StandardErrorContent', '')
        logging.info(f"Command output: {stdout}")
        if stderr:
            logging.error(f"Command error output: {stderr}")

        if status != 'Success':
            return {
                'statusCode': 500,
                'body': json.dumps({'error': f"Command execution failed with status: {status}", 'stderr': stderr})
            }

        # Optionally, you can fetch results from RDS here if needed
        # (Add your RDS query logic if you want to return detection results)

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Disease detection model run successfully', 'output': stdout})
        }

    except Exception as e:
        logging.error(f"Error in Lambda execution: {e}")
        return {
            'statusCode': 500, 
            'body': json.dumps({'error': str(e)})
        }
