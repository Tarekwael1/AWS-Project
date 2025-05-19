import boto3
import time
import pymysql
import logging

ssm = boto3.client('ssm')
sns = boto3.client('sns')

rds_host = "yarb-mndf3sh-aktar-mn-keda.cp8kcmwa2o3e.us-east-1.rds.amazonaws.com"
username = "admin"
password = "Admin123"
db_name = "main_db"
topic_arn = 'arn:aws:sns:us-east-1:116981773526:Notifications'  

def lambda_handler(event, context):
    instance_id = 'i-0c0516d7f319e2d78'
    
    try:
        # 1. Run command on EC2 to start model
        response = ssm.send_command(
            InstanceIds=[instance_id],
            DocumentName='AWS-RunShellScript',
            Parameters={'commands': ['sudo -u ubuntu /usr/bin/python3 /home/ubuntu/disease_detection_model.py']}
        )
        command_id = response['Command']['CommandId']

        # 2. Poll command status
        max_tries = 20
        for i in range(max_tries):
            time.sleep(3)
            invocation = ssm.get_command_invocation(
                CommandId=command_id,
                InstanceId=instance_id
            )
            status = invocation['Status']
            if status in ('Success', 'Failed', 'Cancelled', 'TimedOut'):
                break

        if status != 'Success':
            sns.publish(
                TopicArn=topic_arn,
                Subject='EC2 Command Failed',
                Message=f'EC2 model command failed with status: {status}'
            )
            return {'statusCode': 500, 'body': 'EC2 command failed'}

        # 3. EC2 command succeeded - now fetch results from RDS
        connection = pymysql.connect(
            host=rds_host,
            user=username,
            password=password,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT DISTINCT disease_name FROM Disease_Detection_Results ORDER BY disease_name ASC")
                results = cursor.fetchall()

        if not results:
            sns.publish(
                TopicArn=topic_arn,
                Subject='No Prediction Result',
                Message='No prediction result found in RDS after model run.'
            )
            return {'statusCode': 404, 'body': 'No prediction result found'}

        # Compose message from distinct disease names
        disease_names = [row['disease_name'] for row in results]
        message = "Prediction results:\n" + "\n".join(disease_names)

        # 4. Send SNS notification with results
        sns.publish(
            TopicArn=topic_arn,
            Subject='New Disease Prediction Result',
            Message=message
        )

        return {'statusCode': 200, 'body': 'Success'}

    except Exception as e:
        logging.error(f"Error in Lambda: {e}")
        sns.publish(
            TopicArn=topic_arn,
            Subject='Disease Detection Lambda Error',
            Message=str(e)
        )
        return {'statusCode': 500, 'body': 'Error'}
