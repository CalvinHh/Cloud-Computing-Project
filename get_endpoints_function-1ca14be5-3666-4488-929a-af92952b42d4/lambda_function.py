import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_lambda_endpoints(bucket_name):
    s3 = boto3.client('s3')
    try:
        response = s3.get_object(Bucket=bucket_name, Key='warmup_state.json')
        warmup_data = json.loads(response['Body'].read().decode('utf-8'))
        service = warmup_data.get('service')
        
        if service == 'lambda':
            lambda_endpoints = [
                'https://YOUR_API_GATEWAY_URL/default/analyse_function',
                'https://YOUR_API_GATEWAY_URL/default/analyse_function',
                'https://YOUR_API_GATEWAY_URL/default/analyse_function',
                'https://YOUR_API_GATEWAY_URL/default/analyse_function',
                'https://YOUR_API_GATEWAY_URL/default/analyse_function',
                'https://YOUR_API_GATEWAY_URL/default/analyse_function',
                'https://YOUR_API_GATEWAY_URL/default/analyse_function',
                'https://YOUR_API_GATEWAY_URL/default/analyse_function'
            ]
            return [{'endpoint': endpoint} for endpoint in lambda_endpoints]
    except Exception as e:
        logger.error(f"Exception in get_lambda_endpoints: {str(e)}")
        pass
    
    return []

def get_ec2_endpoints(bucket_name):
    s3 = boto3.client('s3')
    try:
        response = s3.get_object(Bucket=bucket_name, Key='instance_info.json')
        instance_data = json.loads(response['Body'].read().decode('utf-8'))
        instances = instance_data.get('instances', [])
        
        ec2_endpoints = [
            {'endpoint': f"https://{instance['public_dns_name']}"}
            for instance in instances
        ]
        return ec2_endpoints
    except Exception as e:
        logger.error(f"Exception in get_ec2_endpoints: {str(e)}")
        pass
    
    return []

def lambda_handler(event, context):
    try:
        endpoints = []
        import os
	bucket_name = os.getenv('BUCKET_NAME', 'YOUR_BUCKET_NAME')
        
        lambda_endpoints = get_lambda_endpoints(bucket_name)
        ec2_endpoints = get_ec2_endpoints(bucket_name)
        
        endpoints.extend(lambda_endpoints)
        endpoints.extend(ec2_endpoints)
        
        if not endpoints:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'No warmed up resources found'})
            }
        
        return {
            'statusCode': 200,
            'body': json.dumps(endpoints)
        }
    except Exception as e:
        logger.error(f"Exception in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }
