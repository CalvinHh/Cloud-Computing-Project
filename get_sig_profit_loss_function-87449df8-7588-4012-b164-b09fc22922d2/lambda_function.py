import json

def lambda_handler(event, context):
    # Placeholder logic for returning profit/loss for all signals
    profit_loss = [27.2, -51, 8, 3, -12]
    return {
        'statusCode': 200,
        'body': json.dumps({'profit_loss': profit_loss})
    }
