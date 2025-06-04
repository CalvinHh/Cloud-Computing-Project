import boto3
import json

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    import os
    bucket_name = os.getenv('BUCKET_NAME', 'YOUR_BUCKET_NAME')
    key = 'warmup_state.json'

    try:
        response = s3.get_object(Bucket=bucket_name, Key=key)
        warmup_data = json.loads(response['Body'].read().decode('utf-8'))

        if warmup_data.get('state') == 'warming':
            return {
                'statusCode': 200,
                'body': json.dumps({'warm': True})
            }
        else:
            return {
                'statusCode': 200,
                'body': json.dumps({'warm': False})
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
