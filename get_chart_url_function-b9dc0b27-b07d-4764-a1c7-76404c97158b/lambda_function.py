import boto3
import json
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def generate_chart_url(bucket_name, key):
    s3 = boto3.client('s3')
    try:
        response = s3.get_object(Bucket=bucket_name, Key=key)
    except s3.exceptions.NoSuchKey:
        logger.error(f"The specified key does not exist: {key}")
        raise
    except s3.exceptions.NoSuchBucket:
        logger.error(f"The specified bucket does not exist: {bucket_name}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise

    analysis_results = json.loads(response['Body'].read().decode())

    buy_dates = analysis_results['buy_dates']
    var95_list = analysis_results['var95']
    var99_list = analysis_results['var99']
    avg_var95 = analysis_results['avg_var95']
    avg_var99 = analysis_results['avg_var99']

    display_buy_dates = buy_dates[-20:]

    x_axis_labels = '|'.join(display_buy_dates)

    # Create an array of average values of the same length as buy_dates
    avg_var95_line = [avg_var95] * len(buy_dates)
    avg_var99_line = [avg_var99] * len(buy_dates)

    colors = 'ADD8E6,FFA500,800080,90EE90'

    # Construct the chart URL using Image-Charts
    chart_url = (f"https://image-charts.com/chart?chs=800x400&cht=lc&chds=a&chxt=x,y&chd=t:"
                 f"{','.join(map(str, var95_list))}|{','.join(map(str, var99_list))}|"
                 f"{','.join(map(str, avg_var95_line))}|{','.join(map(str, avg_var99_line))}"
                 f"&chxl=0:|{x_axis_labels}&chdl=95%25+VaR|99%25+VaR|Avg+95%25+VaR|Avg+99%25+VaR"
                 f"&chdlp=b&chco={colors}")

    return {
        'chart_url': chart_url
    }

def lambda_handler(event, context):
    bucket_name = 'bucket97'  
    key = 'analysis_results.json'  

    logger.info(f"Fetching object from bucket: {bucket_name}, key: {key}")

    try:
        chart_url = generate_chart_url(bucket_name, key)
        response = {
            'statusCode': 200,
            'body': json.dumps(chart_url)
        }
    except Exception as e:
        response = {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

    return response


