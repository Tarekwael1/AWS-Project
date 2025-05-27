#In this repo, I will share everything about my AWS project, including the steps to complete creating it, with sources.
#Firstly, I will start by outlining the project objectives and the technologies used. The structure I will upload it to a Google Drive folder and share it with you.
Additionally, I will provide detailed documentation on the setup process, code snippets, and any challenges faced along the way.
#So, let's get started. Here are the main objectives of the project:
#1-Learning new technologies.
#2- Do a Practical application about the fields that we study.

#These are the main features of the project:
#1- Mobile App.
#2- Backend using AWS. 
#3- 3 models AI.
#4- RL machine learning.





![Design](https://github.com/user-attachments/assets/90899ed7-17b8-4163-82cd-f7c4e64e5e33)




----------------------------------------------------------------------------------------------------------------------------------
# Looking especially at the backend of the mobile application, which AWS handles:
#Generally speaking, I used AWS Lambda for serverless functions and API Gateway for managing API requests.RDS is used for relational database management, and S3 is used for the storage of static files.  Additionally, I implemented IAM roles for secure access control and monitoring through CloudWatch to track performance and errors. EC2 to run the AI models. Furthermore, I will use AWS Glue for ETL (Extract, Transform, Load) processes, allowing for efficient data integration and preparation for the RL model. Finally, I will utilize CloudFormation for infrastructure as code, ensuring that my deployment is reproducible and manageable.
#So, let us start with the setup process for the AWS environment. (All of these steps were created after the project objectives were clearly defined and the AWS solution architect)
#Note: The VPC is default created by AWS when you create your account, and you will need to specify the VPC settings, including the subnet and security group configurations, to ensure proper connectivity and security for your database. So, if there are no VPCs in your account, create one because this is the environment where you will deploy your application and connect to the database.
#1- Sign in to your AWS account(If you do not have one, create an account) and navigate to the AWS Management Console.
 #---> From this Link https://aws.amazon.com/

# 2-Create a user with the necessary permissions for your project.
 #--->  Go to the upper left of the page and select "IAM" from the dropdown menu, or write IAM in the search console.
 #--->  Select users from the left bar and click the "Add user" button to create a new user.
 #---> Name the user, then choose the policies and permissions that suit your project requirements, such as "AdministratorAccess" for full access or custom policies for specific permissions. Click on "Create user" to finalize the user creation process.
 #--->You now have a user's credentials that you can use to access AWS services.

#3-Build Lambda functions.
 #--->Select Lambda service from the search console and click on the "Create function" button to start building your first Lambda function.
 #--->Select the performances of your function and create it.
 #--->Go to the code and write your code in the inline editor, or upload a .zip file containing your function code and dependencies. You can also choose a runtime that suits your programming language, such as Python or Node.js.(In my project, I used Python)
 #--->Do these steps for all of your lambda functions.

#4- Now we need to set up API Gateway to create endpoints for your Lambda functions, enabling them to be triggered via HTTP requests. And activate your mobile app.
 #---> Search API Gateway in the search console and select "Create API" to start configuring your API endpoints.
 #--->Choose your API type and create it.
 #--->From the left sidebar, select "Resources" to define your resources and methods for the API. You can then link each method to the corresponding Lambda function by selecting "Integration Type" as the Lambda Function and specifying the function you created earlier.
 #--->Once you have defined your resources and methods, deploy your API by selecting "Deploy API" from the Actions dropdown menu. Choose a deployment stage and click "Deploy" to make your API accessible.

#5-After that, the project will not work, so why??
 #--->You create everything correctly, but you have not configured the necessary permissions and CORS settings for your API Gateway endpoints and Lambda functions to be invoked properly from your mobile app.

#6-From Lambda function, from configuration-> permissions-> add role if you did not add it when you were creating the function.

#7-We created the Lambda functions and APIs, now we need to create the database that will store the data for our application using Amazon RDS. (If your database is relational)
 #--->Go to RDS in the AWS Management Console and select "Create database" to start the database creation process.
 #--->Choose your database's storage and CPU, ...etc.(I use the free tier version)
 #--->Prepare the permissions for your database by configuring the security groups and IAM roles to allow access from your Lambda functions and API Gateway. Ensure that the database is accessible only from the necessary sources to maintain security.
 #--->Security Groups are like a guard to the firewall for your AWS resources, controlling inbound and outbound traffic to your database instance. (Most problems occur due to misconfigured security group settings, which I faced.)

#8-Create an EC2 instance to run your AI models and configure it with the necessary software and dependencies, such as Python, TensorFlow, or PyTorch, depending on the specific AI models you intend to run.
 #--->Go to EC2 in the AWS Management Console and select "Launch Instance" to start the instance creation process.
 #--->Pick out your EC2 type and configure the instance size, security group settings, and key pair for SSH access.

#9-To create S3 bucket to store static files, go to S3 in the AWS Management Console.
 #--->Select "Create bucket". Choose a unique name for your bucket, configure the settings such as region and permissions, and click "Create bucket" to finalize the process.
 #--->If you need Lambda to access the S3 bucket, ensure that the appropriate permissions and policies are set for the Lambda function to interact with the bucket. And you should create an access point for easier management of access and permissions.

#10- Finally, implement monitoring and logging for your AWS resources to track performance and troubleshoot any issues that arise. Use CloudWatch to set up alarms and dashboards for your Lambda functions, API Gateway, and RDS instances, ensuring that you can proactively manage your application.
----------------------------------------------------------------------------------------------------------------------------------

#I created a small test for the AWS Glue with filtered data received from the Raspberry Pi.
 #--->RL_Data_Filter.py is the script for the Lambda function, which chooses the required data for the RL model, such as(PH, Rh, Light, etc). This function filters data and then saves it as a file. CSV into an S3 bucket as a source file for the ETL. The ETL continues filtration, like if the RL needs the value, for example, the PH is equal to 20 and RH 3, the output will be another file. CSV, which will be saved in another folder in the S3 bucket.
#Steps:
1-Create the S3 bucket and create a folder.

2-Create a Lambda function with its requirements.
 #--->IAM:
 ===>AWSLambdaBasicExecutionRole
 ===>S3FullAccess
 #Liberaies:
 ===>Pymysql

3- Go to AWS Glue.
 #--->Create a new crawler.
 ===>Choose your source file, which is the output of the lambda function in the S3, and make the format CSV.
 ===>Choose the database of Glue database. If you do not have one, create a new one.
 ===>Name the crawler and save.
 ===>Run the crawler. (This will create a table. If you need to check if the table was created successfully, go to the table on the left and check.
 #--->Go to ETL Jobs.
 ===>If you need to create it as code or as a visual. (I created it using a visual ETL.)
 ===>From (+) choose source --> S3 bucket, double click on it, and select the path to your CSV file from the S3 bucket.
 ===>From (+) choose transform -->Custom transform.
 ===> From (+), choose the target and select the output path to S3. (It should be another folder.)
 #--->Name the Job, save, and run it.

In the future, I will make CloudWatch run this operation according to the project's requirements.

----------------------------------------------------------------------------------------------------------------------------------
#(Here I will explain all the scripts and their goals).
#Lambda_Login.py
    --->This Lambda is for Login and its name in the AWS is rds-user-auth, it is used to authenticate the user and then to get the user's data from the database.

#Lambda_Registeration.py
    --->This Lambda is for registering a new user and saving their data into the database.

#Dashboard_start.py
    --->This Lambda is for returning all the plates' data from the database and sending it to the APP via API Gateway to display them.

#Setup_plate.py
     --->This Lambda is for setting up a new plate and saving it in the database, which receives the data from the app via API Gateway.

#Delete_Plate.py
    --->This Lambda is for deleting a plate from the database, and also receiving the data from the APP via API Gateway.

#ControlACT.py
    --->***----This will be created soon----***

#GetACTStatus.py
    --->***____This will be created soon____***

#Get_disease_image.py
    --->This Lambda is for getting the disease image from the database and S3 and sending it to the APP via API Gateway.

#Delete_disease_image.py
    --->This Lambda is for deleting the diseases' images for S3 and RDS, which receives the data from the APP via API Gateway.

#RL_Data_Filter.py
    --->This Lambda gets the data from the database and saves the required data into the S3 bucket to be the source for the ETL job.

#RPI_Data,py
    --->This Lambda is for receiving the data from the RPI's sensors

#start_stop_EC2.py
    --->This Lambda is for starting and stopping the EC2 instance, which runs the models.

***There is no Lambda for Disease detection model(This will be created soon)***

#EC2_Disease_Detiction.py
    --->This is the script, which runs the disease detection model on the EC2 instance, and saves the result in the database.

#EC2_Prediction.py
    --->This is the script, which runs the prediction model on the EC2 instance, and saves the result in the database.

#Disease_Detection_Runner.py
    --->This is the script, which runs the disease detection model on the EC2 instance, and saves the images in the S3 bucket and RDS. Additionally, this model will be run every day at 6 am and will send a message to the user.
----------------------------------------------------------------------------------------------------------------------------------
#APIs
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


#GetACTStatus ---> ***_____This will be created soon______***
    -Postman JSON--->***___This will be created soon___***

#ControlACT ---> ***_____This will be created soon______***
    -Postman JSON--->***___This will be created soon___***

#start-stop-EC2 ---> https://jk50f5a0mi.execute-api.us-east-1.amazonaws.com/Dashboard/Get-prediction .
    -Postman JSON--->{
                        "user_id": "1"
                    }


----------------------------------------------------------------------------------------------------------------------------------
#(This is overall about the steps of the AWS setup process, the architecture of my project, and the common problems that I encountered during the development phase.
By following these steps, you can successfully set up your AWS environment and deploy your application while minimizing common pitfalls encountered during the process. In the next step, I will upload all the code and configuration files to the repository for further reference and explain the steps of testing and the job of each Lambda and API endpoint, and so on.)
