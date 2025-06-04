import json

def lambda_handler(event, context):
    # Placeholder logic for terminate
    return {
        'statusCode': 200,
        'body': json.dumps({'result': 'ok'})
    }