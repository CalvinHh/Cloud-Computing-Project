import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_hourly_rate(service):
    # Define the hourly rates for Lambda and EC2
    hourly_rates = {'lambda': 0.001, 'ec2': 0.005}
    return hourly_rates.get(service, 0)

def calculate_warmup_cost(service, warmup_time, resource_count):
    hourly_rate = get_hourly_rate(service)
    billable_time = warmup_time   # Assuming warmup_time is in hours
    cost = hourly_rate * billable_time * resource_count
    return {'billable_time': billable_time, 'cost': cost}

def lambda_handler(event, context):
    try:
        # Retrieve warm-up data from S3
        s3 = boto3.client('s3')
        import os
	bucket_name = os.getenv('BUCKET_NAME', 'YOUR_BUCKET_NAME')
        object_key = 'warmup_state.json'
        
        logger.info(f'Retrieving warm-up data from S3 bucket {bucket_name} with key {object_key}')
        
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        warmup_data = json.loads(response['Body'].read().decode('utf-8'))
        
        logger.info(f'Warm-up data retrieved: {warmup_data}')

        # Extract data from warm-up info
        service = warmup_data.get('service')
        warmup_time = warmup_data.get('warmup_time')
        resource_count = warmup_data.get('resource_count')

        logger.info(f'Service: {service}, Warmup Time: {warmup_time}, Resource Count: {resource_count}')

        if not service or not resource_count:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid input parameters'})
            }

        if service == 'lambda':
            warmup_cost = calculate_warmup_cost('lambda', warmup_time, resource_count)
        elif service == 'ec2':
            warmup_cost = calculate_warmup_cost('ec2', warmup_time, resource_count)
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Unsupported service: ' + service})
            }

        return {
            'statusCode': 200,
            'body': json.dumps(warmup_cost)
        }

    except Exception as e:
        logger.error(f'Exception: {str(e)}')
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }
