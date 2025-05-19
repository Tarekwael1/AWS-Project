{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": [
                    "datazone.amazonaws.com",
                    "sagemaker.amazonaws.com"
                ],
                "AWS": [
                    "arn:aws:iam::116981773526:role/service-role/AmazonSageMakerServiceCatalogProductsCloudformationRole",
                    "arn:aws:iam::116981773526:role/service-role/AmazonSageMakerServiceCatalogProductsLambdaRole",
                    "arn:aws:iam::116981773526:role/datazone_usr_role_3w9p6og0f22js7_4pw33uydexxh9j"
                ]
            },
            "Action": [
                "sts:AssumeRole",
                "sts:TagSession",
                "sts:SetContext"
            ],
            "Condition": {
                "StringEquals": {
                    "aws:SourceAccount": "116981773526"
                }
            }
        }
    ]
}







{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Effect": "Allow",
			"Principal": {
				"Service": "datazone.amazonaws.com"
			},
			"Action": [
				"sts:AssumeRole",
				"sts:TagSession",
				"sts:SetContext"
			],
			"Condition": {
				"StringEquals": {
					"aws:SourceAccount": "116981773526"
				},
				"ForAllValues:StringLike": {
					"aws:TagKeys": "datazone*"
				}
			}
		}
	]
}






















{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": [
                    "auth.datazone.amazonaws.com",
                    "datazone.amazonaws.com"
                ]
            },
            "Action": [
                "sts:AssumeRole",
                "sts:TagSession",
                "sts:SetContext",
                "sts:SetSourceIdentity"
            ],
            "Condition": {
                "StringEquals": {
                    "aws:SourceAccount": "116981773526"
                }
            }
        },
        {
            "Effect": "Allow",
            "Principal": {
                "Service": [
                    "glue.amazonaws.com",
                    "airflow-env.amazonaws.com",
                    "scheduler.amazonaws.com",
                    "sagemaker.amazonaws.com",
                    "emr-serverless.amazonaws.com",
                    "lakeformation.amazonaws.com",
                    "airflow.amazonaws.com",
                    "lambda.amazonaws.com"
                ]
            },
            "Action": [
                "sts:AssumeRole",
                "sts:TagSession",
                "sts:SetContext",
                "sts:SetSourceIdentity"
            ],
            "Condition": {
                "StringEquals": {
                    "aws:SourceAccount": "116981773526"
                }
            }
        },
        {
            "Effect": "Allow",
            "Principal": {
                "Service": [
                    "redshift-serverless.amazonaws.com",
                    "redshift.amazonaws.com"
                ]
            },
            "Action": "sts:AssumeRole",
            "Condition": {
                "StringLike": {
                    "sts:ExternalId": "arn:aws:redshift:*:116981773526:dbuser:*/*"
                }
            }
        },
        {
            "Effect": "Allow",
            "Principal": {
                "Service": [
                    "redshift-serverless.amazonaws.com",
                    "redshift.amazonaws.com"
                ]
            },
            "Action": [
                "sts:TagSession",
                "sts:SetContext",
                "sts:SetSourceIdentity"
            ]
        },
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::116981773526:role/service-role/AmazonSageMakerProvisioning-116981773526"
            },
            "Action": [
                "sts:AssumeRole",
                "sts:TagSession",
                "sts:SetContext",
                "sts:SetSourceIdentity"
            ]
        },
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "bedrock.amazonaws.com"
            },
            "Action": [
                "sts:AssumeRole",
                "sts:TagSession",
                "sts:SetContext",
                "sts:SetSourceIdentity"
            ],
            "Condition": {
                "StringEquals": {
                    "aws:SourceAccount": "116981773526"
                },
                "ArnLike": {
                    "aws:SourceArn": "arn:aws:bedrock:us-east-1:116981773526:*"
                }
            }
        }
    ]
}