The componets of the AWS project:

* IAM.
* NAT Gateway.
* Security Groups.
* Route Tables.
* API.
* Lambda.
* EC2.
* S3.
* Sagemaker.
* AWS Glue.
* SNS.
* Cloudwatch Events.
* RDS.

![Design](https://github.com/user-attachments/assets/90899ed7-17b8-4163-82cd-f7c4e64e5e33)

# IAM Roles:

* Give the Lambda functions permissions to connect with other services and complete their missions correctly.
  1. Lambda_login.py: This function needs the permission of connected with RDS to read the data only.
     * AmazonRDSReadOnlyAccess.
  2. Lambda_Registeration.py: This function needs the permission of connected with RDS to write the data only.
     * AmazonRDSWriteOnlyAccess.
  3. Dashboard_start.py: This function needs the permission of connected with RDS to read data only.
     * AmazonRDSReadOnlyAccess.
  4. Setup_plate.py: This function needs the permission of connected with RDS to write new data only.
     * AmazonRDSWriteOnlyAccess.
  5. Delete_plate.py: This function needs the permission of connected with RDS to write data only.
     * AmazonRDSWriteOnlyAccess.
  6. Start_Stop_EC2.py: This function needs the permissions of connected with RDS and EC2, and SNS permissions.
     * AmazonSNSFullAccess.
     * AmazonRDSWriteOnlyAccess.
     * AmazonSSMFullAccess.
  7. Disease_detection_Runner.py: This function needs the permissions of connected with RDS and EC2, and SNS permissions.
     * AmazonSNSFullAccess.
     * AmazonRDSWriteOnlyAccess.
     * AmazonSSMFullAccess.
  8. Get_disease_Images.py: This function needs the permissions of connected with RDS to read data.
     * AmazonRDSReadOnlyAccess.
  9. Delete_disease_Images.py: This function needs the permissions of connected with RDS to read and write, and permissions of S3.
     * AmazonS3FullAccess.
     * AmazonRDSFullAccess.
  10. RL_Data_Filter.py: This function needs the permissions of connected with RDS to read and write, and permissions of S3.
      * AmazonS3FullAccess.
      * AmazonRDSFullAccess.
  11. RPI_Data.py: This function needs the permissions of connected with RDS to write data.
      * AmazonRDSWriteOnlyAccess.

# RDS

This is the storage database for the whole system, and we connected with it to a local server, like Mysql server to make the work easier.

# Nat Gateway

This service make the connection with the Internet easy for private subnets, so we used it to give the private subnets the access to the internet.

*To notice: Any Nat Gateway requires Elastic IP.

# Security Groups

The gard of the VPC, which check the whole communications to and from the VPC via the IP.

1. RDS: Needs the connection with Lambda, EC2, and local server.

   * Inbound:
     * MYSQL/Aurora   TCP     3306    from the security group of the Lambda, EC2, or your local IP.
2. EC2:

   * Inbound:
     * <br/>SSH   TCP   22   from the security group of the Lambda and our local IP, if you need to connect with it from your local machine.
   * Outbound:
     * MYSQL/Aurora   TCP     3306     to your local IP, if you created with RDS locally.
3. Lambda:

   * Outbound:
     * SSH   TCP   22      to your EC2 security group.
     * MYSQL/Aurora   TCP    to your RDS security group.

# Route Table

The route table that automatically comes with your VPC. It controls the routing for all subnets that are not explicitly associated with any other route table.This service

It contains private subnet, and used Nat Gateway to have an access to the internet.

# API

This which sends and receives the commands from and to mobile APP, and triggers the Lambda funcions.

Each Lambda funtion has an API to make the communication more stable and faster without any interruptions.

# Lambda

* In Log in/ Register folder there are two scripts:
  1. Lambda_Login.py:
     * This function is triggered by API, and receives the input data from the mobile app. Moreover, it will connect with the RDS to check if the data is correct. However, if the input data is correct that will return the confirmation message successfully, if not, that will answer with error message.
  2. lambda Registeration.py:
     * This function is triggered by API, and recieves the input data from the mobile app, and save it into the RDS tables. However, it checks first if the data was inputted before or not.
* In Dashboard folder there are three scripts:
  1. Dashboard_start.py:
     * Once the page of dashborad in the mobile app is oped, this Lambda will be triggered via API, and this function return the data from RDS of the plates to displayed in the app.
  2. Setup_plate.py:
     * This function will be triggerd via API when the user click on the add plate buttom. Moreover, it will take the input data and save it into RDS tables wich Dashboard start display it.
  3. Delete_plate.py:
     * This function will be triggerd via API when the user click on the delete plate buttom.
* Display-Delete disease images folder include two files:
  1. Get_disease_images.py:
     * This function just gets links of the images and the diseases' names from the RDS.
  2. Delete_disease_Images.py:
     * This Lambda will receive image link to delete from RDS and S3.
* Data folder contains two scripts:
  1. RPI_Data.py:
     * This file receive the data from raspberry pi and save it into the RDS.
  2. RL_Data_Filter.py:
     * This function returns the filtered data, which is filtered using AWS Glue, and will be sent to the RL model.
       This script for the Lambda function, which chooses the required data for the RL model, such as(PH, Rh, Light, etc). This function filters data and then saves it as a file. CSV into an S3 bucket as a source file for the ETL. The ETL continues filtration, like if the RL needs the value, for example, the PH is equal to 20 and RH 3, the output will be another file. CSV, which will be saved in another folder in the S3 bucket.
* In EC2 models runners folder there are two files:
  1. Start_Stop_EC2.py:
     * This function will be triggered via API when the setup plate page is opened, and it will run the Ec2 if it stoped, after that will run the EC2_script_prediction.py, which is on EC2 scrips folder, and the script itself runs the model and saves the output data into the RDS, and the Lambda function returns the output from the RDS.
  2. Disease_Detection_Runner.py:
     * This Lambda is triggered by cloudwatch events service every day at 9 AM, and send notification with the output diseases' names. However, this function will run the EC2_Disease_Detection_Script.py, which is on EC2 scrips folder, and this script itself runs the model and save the output into the RDS, and the Lambd function returns it.

# EC2

This is the computing service which we used to run the light models, such as prediction and disease detection.

It contains the whole requirements, such as pandas...etc.

# S3

Our S3 has more than bucket, and each one for spicific mission.

1. Bucket for the camera images, which the model detects them.
2. Bucket for the detected disease, which is the output of the disease detection model.
3. Bucket for filtered data as file.csv.
4. Another bucket for the output of the sagemaker, which is the trained model.

# Sagemaker

We use it to train our models, and it requires many libraies, like sklearn...etc.

# AWS Glue

This service takes the data of RL model and analyses it, then save it into the S3.

# SNS

We use it to send notification to the users as an alert for quintessential things, like the outputs of the models. In addition, the nitifications are sent via Email or HTTPS to the mobile app.

# Cloudwatch Events

Is used to run the disease detection model every day morning, and send the output as a meesage.

# APIs

#rds-user-auth --->  https://zeucnmkeah.execute-api.us-east-1.amazonaws.com/RegisterLogin/rds-user-auth .
-Postman JSON--->{
"username": "NAME",
"password": "Password"
}

#RegisterUserFunction ---> https://zeucnmkeah.execute-api.us-east-1.amazonaws.com/RegisterLogin/RegisterUserFunction .
-Postman JSON--->{
"username": "Name"
"password": "Password"
"email": "E-mail"
}

#Dashboard_Start ---> https://jk50f5a0mi.execute-api.us-east-1.amazonaws.com/Dashboard/Dashboard_Start .
-Postman JSON--->{It requiers nothing}

#Setup_Plate ---> https://gisvleb85c.execute-api.us-east-1.amazonaws.com/Setup_Delete_plate/setup-plate .
-Postman JSON--->{
"user_id": "2",
"plate_id": 2,
"plant_name": "Lavender",
"plant_id": 1,
"age_in_weeks": 3,
"harvested": false
}

#Delete_Plate ---> https://gisvleb85c.execute-api.us-east-1.amazonaws.com/Setup_Delete_plate/delete-plate .
-Postman JSON--->{
"plate_name": "Plate 1",
"user_id": "1"
}

#RPI_Data ---> https://wdy1m5yd7i.execute-api.us-east-1.amazonaws.com/RPI/RPI_DATA .
-Postman JSON--->{
"plate_id": 1,
"plant_id": 2,
"user_id": 2,
"unit_id": 1,
"timestamp": "2025-04-30 14:30:00",
"temperature": 25.5,
"humidity": 60.2,
"light_intensity": 350.0,
"solution_level": 5.5,
"ph": 6.5,
"ec": 1.2,
"anomaly_detection": 0,
"red_light_intensity": 100.0,
"blue_light_intensity": 80.0,
"far_red_light_intensity": 60.0,
"air_flow_level": 2.0,
"CO2": 400.0
}

#RL_Filter --->***___This will be created soon_____***
-Postman JSON--->{
"user_id": "12345"
}

#Get-desease-image ---> https://a4b272sa24.execute-api.us-east-1.amazonaws.com/disease_images/Get-disease-image .
-Postman JSON--->{
"user_id": "1"
}

#Delete-desease-image ---> https://a4b272sa24.execute-api.us-east-1.amazonaws.com/disease_images/Delete-disease-image .
-Postman JSON--->{
"image_url": "https://prediction-resultss.s3.us-east-1.amazonaws.com/predictions/botrytis_predicted_1746284582.jpg",
"user_id": "1"
}

#start-stop-EC2 ---> https://jk50f5a0mi.execute-api.us-east-1.amazonaws.com/Dashboard/Get-prediction .
-Postman JSON--->{
"user_id": "1"
}

---

#(This is overall about the steps of the AWS setup process, the architecture of my project, and the common problems that I encountered during the development phase.
By following these steps, you can successfully set up your AWS environment and deploy your application while minimizing common pitfalls encountered during the process. In the next step, I will upload all the code and configuration files to the repository for further reference and explain the steps of testing and the job of each Lambda and API endpoint, and so on.)
