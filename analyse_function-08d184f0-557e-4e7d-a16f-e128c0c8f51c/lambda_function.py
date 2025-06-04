import random
import json
import boto3
import time


def calculate_profit_loss(entry_price, exit_price):
    return exit_price - entry_price

def upload_to_s3(bucket_name, key, data):
    s3 = boto3.client('s3')
    s3.put_object(Bucket=bucket_name, Key=key, Body=data)
    
def download_from_s3(bucket_name, key):
    s3 = boto3.client('s3')
    try:
        response = s3.get_object(Bucket=bucket_name, Key=key)
        data = response['Body'].read().decode('utf-8')
        if not data:
            raise ValueError("Empty S3 object")
        return json.loads(data)
    except s3.exceptions.NoSuchKey:
        return None
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in S3 object: {str(e)}")

def lambda_handler(event, context):
    try:
        start_time = time.time()
        event = json.loads(event.get('body'))
        
        # Extract data from the event
        minhistory = event['minhistory']
        shots = event['shots']
        t = event['signal_type']
        days = event['days']
        stock_data = event['stock_data']  # Extract stock data
        
        # Retrieve values of 's' and 'r' from S3
        s3_bucket_name = 'warmup97'  
        s3_key = 'warmup_state.json'  
        warmup_data = download_from_s3(s3_bucket_name, s3_key)
        
        if not warmup_data:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Warmup state not found or it is empty in S3'})
            }
        
        s = warmup_data['service']
        r = warmup_data['resource_count']
        
        buy_dates = []  # Initialize with a default value
        sell_dates = []  # Initialize with a default value

        for i in range(2, len(stock_data)):
            body = 0.01

            # Three Soldiers
            if (stock_data[i]['Close'] - stock_data[i]['Open']) >= body \
                    and stock_data[i]['Close'] > stock_data[i - 1]['Close'] \
                    and (stock_data[i - 1]['Close'] - stock_data[i - 1]['Open']) >= body \
                    and stock_data[i - 1]['Close'] > stock_data[i - 2]['Close'] \
                    and (stock_data[i - 2]['Close'] - stock_data[i - 2]['Open']) >= body:
                stock_data[i]['Buy'] = 1

            # Three Crows
            if (stock_data[i]['Open'] - stock_data[i]['Close']) >= body \
                    and stock_data[i]['Close'] < stock_data[i - 1]['Close'] \
                    and (stock_data[i - 1]['Open'] - stock_data[i - 1]['Close']) >= body \
                    and stock_data[i - 1]['Close'] < stock_data[i - 2]['Close'] \
                    and (stock_data[i - 2]['Open'] - stock_data[i - 2]['Close']) >= body:
                stock_data[i]['Sell'] = 1
            
        var95_list = []
        var99_list = []
        profit_loss_list = []

        for i in range(minhistory, len(stock_data)):
            if stock_data[i]['Buy'] == 1:
                # Calculate VaR values for Buy signal
                close_prices_buy = [stock_data[j]['Close'] for j in range(i - minhistory, i)]
                pct_changes_buy = [(close_prices_buy[j] - close_prices_buy[j-1]) / close_prices_buy[j-1] for j in range(1, len(close_prices_buy))]
                buy_mean = sum(pct_changes_buy) / len(pct_changes_buy)
                buy_std = (sum((x - buy_mean) ** 2 for x in pct_changes_buy) / len(pct_changes_buy)) ** 0.5

                simulated_buy = [random.gauss(buy_mean, buy_std) for _ in range(shots)]
                simulated_buy.sort(reverse=True)
                var95_buy = simulated_buy[int(len(simulated_buy) * 0.95)] * 0.95
                var99_buy = simulated_buy[int(len(simulated_buy) * 0.99)] * 0.99
                

                var95_list.append(var95_buy)
                var99_list.append(var99_buy)

                
                buy_date = stock_data[i - days]['Date']
                sell_date = stock_data[i]['Date']
                buy_dates.append(buy_date)
                sell_dates.append(sell_date)
                buy_price = stock_data[i - days]['Close']
                sell_price = stock_data[days]['Close']
                profit_loss = calculate_profit_loss(buy_price, sell_price)
                profit_loss_list.append(profit_loss)

            if stock_data[i]['Sell'] == 1:
                # Calculate VaR values for Sell signal
                close_prices = [stock_data[j]['Close'] for j in range(i - minhistory, i)]
                pct_changes = [(close_prices[j] - close_prices[j-1]) / close_prices[j-1] for j in range(1, len(close_prices))]
                sell_mean = sum(pct_changes) / len(pct_changes)
                sell_std = (sum((x - sell_mean) ** 2 for x in pct_changes) / len(pct_changes)) ** 0.5
                
                simulated = [random.gauss(sell_mean, sell_std) for _ in range(shots)]
                simulated.sort(reverse=True)
                var95_sell = simulated[int(len(simulated) * 0.95)] * 0.95
                var99_sell = simulated[int(len(simulated) * 0.99)] * 0.99

                var95_list.append(var95_sell)
                var99_list.append(var99_sell)
                buy_date = stock_data[i - days]['Date']
                sell_date = stock_data[i]['Date']
                buy_dates.append(buy_date)
                sell_dates.append(sell_date)
                buy_price = stock_data[i - days]['Close']
                sell_price = stock_data[days]['Close']
                profit_loss = calculate_profit_loss(sell_price, buy_price)
                profit_loss_list.append(profit_loss)
        
        # Calculate the total profit/loss
        total_profit_loss = sum(profit_loss_list)
        profit_or_loss = 'Profit' if total_profit_loss > 0 else 'Loss'
        
        # Calculate the average of var95 and var99
        avg_var95 = sum(var95_list) / len(var95_list) if len(var95_list) > 0 else 0
        avg_var99 = sum(var99_list) / len(var99_list) if len(var99_list) > 0 else 0
        
        
        end_time = time.time()  # Record end time
        execution_time = (end_time - start_time)
        cost = execution_time * 0.0000166667 * 128/1024 * r
        analysis_results = {
            'var95': var95_list,
            'var99': var99_list,
            'avg_var95': avg_var95,
            'avg_var99': avg_var99,
            'profit_loss': profit_loss_list,
            'total_profit_loss': total_profit_loss,
            'time': execution_time,
            'cost': cost,
            'profit_or_loss': profit_or_loss,
            'buy_dates': buy_dates,
            'sell_dates': sell_dates,
            'h': minhistory,
            'd': shots,
            't': t,
            'p': days,
            's': s,
            'r': r
        }
        
        bucket_name = os.getenv('BUCKET_NAME', 'YOUR_BUCKET_NAME')
        key = 'analysis_results.json'  
        upload_to_s3(bucket_name, key, json.dumps(analysis_results))
        
        
        # Return a successful response with status code 200
        return {
            'statusCode': 200,
            'body': json.dumps({'analysis_results' : analysis_results})
        }

    except ValueError as ve:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(ve)})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }
