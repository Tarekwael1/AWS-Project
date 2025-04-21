#In this repo, I will share everything about my AWS project, including the steps to complete creating it, with sources.
#Firstly, I will start by outlining the project objectives and the technologies used.The structure I will upload it to a google drive folder and share it with you.
Additionally, I will provide detailed documentation on the setup process, code snippets, and any challenges faced along the way.
#So, lets get started, here are the main objectives of the project:
#1-Learning new technologies.
#2-Do Practical application about the fields which are we study.

#These are the main features of the project:
#1-Mobile App.
#2-Backend using AWS.
#3- 4 to 5 models AI.
#4- RL machine learning.

#Looking specially at the backend of the mobile application which is handled by AWS:
#Generally speaking, I used AWS Lambda for serverless functions and API Gateway for managing API requests.RDS for relational database management, and S3 for storage of static files.  Additionally, I implemented IAM roles for secure access control and monitoring through CloudWatch to track performance and errors. EC2 to run the ai models. Furthermore, I will use AWS Glue for ETL (Extract, Transform, Load) processes, allowing for efficient data integration and preparation to RL model. Finally, I will utilize CloudFormation for infrastructure as code, ensuring that my deployment is reproducible and manageable.
#So, lets start with the setup process for the AWS environment.(All of these steps created after the project objectives were clearly defined and build the AWS solution arcetichet)
#Note:The VPC is default created by AWS when you create your account and you will need to specify the VPC settings, including the subnet and security group configurations, to ensure proper connectivity and security for your database. So, if there is no VPCs in your account create one because this is the environment when you will deploy your application and connect to the database.
#1- Sign in to your AWS account(If you do not have one create an account) and navigate to the AWS Management Console.
#---> From this Link https://aws.amazon.com/
#2-Create user with the necessary permissions for your project.
#---> Go to the upper left of the page and select "IAM" from the dropdown menu, or write IAM in the search console.
#--->select users from left bar and click the "Add user" button to create a new user.
#--->Name the user then choose the policies and permmisions that suit your project requirements, such as "AdministratorAccess" for full access or custom policies for specific permissions.And click on "Create user" to finalize the user creation process.
#--->You now have a user credentials that you can use to access AWS services.
#3-Build Lambda functions.
#3--->Select Lambda survice from search console and click on the "Create function" button to start building your first Lambda function.
#--->Select the performances of you function and create it.
#--->Go to the code and write your code in the inline editor, or upload a .zip file containing your function code and dependencies. You can also choose a runtime that suits your programming language, such as Python or Node.js.(In my project i used Python)
#--->Do these steps for all of you lambda functions.
#4-Now we need to set up API Gateway to create endpoints for your Lambda functions, enabling them to be triggered via HTTP requests.And active your mobile app.
#--->search API Gateway in the search console and select "Create API" to start configuring your API endpoints.
#--->Choose your API type and create it.
#--->From the left sidebar, select "Resources" to define your resources and methods for the API. You can then link each method to the corresponding Lambda function by selecting "Integration Type" as Lambda Function, and specifying the function you created earlier.
#--->Once you have defined your resources and methods, deploy your API by selecting "Deploy API" from the Actions dropdown menu. Choose a deployment stage and click "Deploy" to make your API accessible.
#5-After that the project will not work, so why??
#--->You create everything correctly but you have not configured the necessary permissions and CORS settings for your API Gateway endpoints and Lambda functions to be invoked properly from your mobile app.
#6-From Lambda function from configuration-> permissions-> add role if you do not added it when you was creating the function.
#7-We created the Lambda functions and APIs, now we need to create the database which will store the data for our application using Amazon RDS.(If your database is relational)
#--->Go to RDS in the AWS Management Console and select "Create database" to start the database creation process.
#--->Choose your database's storage and CPU, ...etc.(I use the free tier version)
#--->Prepare the permissions for your database by configuring the security groups and IAM roles to allow access from your Lambda functions and API Gateway. Ensure that the database is accessible only from the necessary sources to maintain security.
#--->Security Groups are like a gard to the firewall for your AWS resources, controlling inbound and outbound traffic to your database instance.(The most problems occur due to misconfigured security group settings, which I faced.)
#8-Create EC2 instance to run your AI models and configure it with the necessary software and dependencies, such as Python, TensorFlow, or PyTorch, depending on the specific AI models you intend to run.
#--->Go to EC2 in the AWS Management Console and select "Launch Instance" to start the instance creation process.
#--->Pick out your EC2 type and configure the instance size, security group settings, and key pair for SSH access.
#9-To create S3 bucket to store static files, go to S3 in the AWS Management Console.
#--->Select "Create bucket". Choose a unique name for your bucket, configure the settings such as region and permissions, and click "Create bucket" to finalize the process.
#--->If you need Lambda to access the S3 bucket, ensure that the appropriate permissions and policies are set for the Lambda function to interact with the bucket. And you should create access point for easier management of access and permissions.
#10- Finally, implement monitoring and logging for your AWS resources to track performance and troubleshoot any issues that arise. Use CloudWatch to set up alarms and dashboards for your Lambda functions, API Gateway, and RDS instances, ensuring that you can proactively manage your application.

#(This is overall about the steps and the AWS setup process and the architecture of my project and the common problems that I encountered during the development phase.
By following these steps, you can successfully set up your AWS environment and deploy your application while minimizing common pitfalls encountered during the process.The next step, I will upload all the code and configuration files to the repository for further reference and explain the steps of testing and the job of each Lambda and API endpoint and so on.)