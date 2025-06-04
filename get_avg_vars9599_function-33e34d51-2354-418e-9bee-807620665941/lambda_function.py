import json

def lambda_handler(event, context):
    # Placeholder logic for returning average var95 and var99
    avg_var95 = 0.3345
    avg_var99 = 0.3345
    return {
        'statusCode': 200,
        'body': json.dumps({'var95': avg_var95, 'var99': avg_var99})
    }