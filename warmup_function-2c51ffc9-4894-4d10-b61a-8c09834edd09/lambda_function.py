import boto3
import json

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        service = body.get('s')
        scale = body.get('r')
        
        if not service or not scale:
            raise ValueError("Invalid input: 's' and 'r' must be provided")

        if service == 'ec2':
            ec2 = boto3.client('ec2')
            instance_ids = ['i-xxxxxxxxxxxxxxxxx'] * scale
            response = ec2.start_instances(InstanceIds=instance_ids)
        
        return {
            'statusCode': 200,
            'body': json.dumps({'result': 'ok'})
        }
    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'errorMessage': str(e)})
        }
