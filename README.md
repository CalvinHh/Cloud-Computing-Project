# Cloud-Computing-Project
This project(one of my individual coursework projects) is designed for a cloud-based system for analyzing trading signals in Yahoo financial time series data. Web hosting is implemented by Google App Engine. Lambda functions, EC2 and S3 from AWS services performs trading strategies calculation. Users can access the system by using RESTful API endpoints.
Features
Flask API for orchestrating analysis and cloud resource scaling

AWS Lambda function templates for analysis and utility tasks

Example S3 and EC2 integration

All sensitive data (bucket names, endpoints) uses placeholders or environment variables—no secrets in code

Repository Contents
index.py – Flask web server and API routes

lambda_function.py – Example Lambda handler(s)

analysis_results.json – Example analysis output

instance_info.json – Example instance info (redacted)

warmup_info.json – Example warmup config

warmup_state.json – Example resource state

Security Notice
This repo contains no real credentials or cloud endpoints.

All instance IDs, DNS names, and bucket names are redacted or placeholders.

Never commit your .env file or real credentials to public repositories.

Customization
Edit lambda_function.py for your own analysis or compute logic.

Deploy your own AWS Lambda/API Gateway as needed, and use those endpoints.
