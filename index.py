from flask import Flask, jsonify, request
import requests
from datetime import date, timedelta
from pandas_datareader import data as pdr
import yfinance as yf
import json
#import logging

# Initialize Flask app
app = Flask(__name__)
yf.pdr_override()

# Configure logging
#logging.basicConfig(level=logging.DEBUG)
#logger = logging.getLogger(__name__)

# Endpoints
warmup_endpoint = 'https://YOUR_API_GATEWAY_URL/default/analyse_function'
scaled_ready_endpoint = 'https://YOUR_API_GATEWAY_URL/default/analyse_function'
get_warmup_cost_endpoint = 'https://YOUR_API_GATEWAY_URL/default/analyse_function'
get_endpoints_endpoint = 'https://YOUR_API_GATEWAY_URL/default/analyse_function'
analyse_endpoint = 'https://YOUR_API_GATEWAY_URL/default/analyse_function'
get_sig_vars9599_endpoint = 'https://YOUR_API_GATEWAY_URL/default/analyse_function'
get_avg_vars9599_endpoint = 'https://YOUR_API_GATEWAY_URL/default/analyse_function'
get_sig_profit_loss_endpoint = 'https://YOUR_API_GATEWAY_URL/default/analyse_function'
get_total_profit_loss_endpoint = 'https://YOUR_API_GATEWAY_URL/default/analyse_function'
get_chart_url_endpoint = 'https://YOUR_API_GATEWAY_URL/default/analyse_function'
get_time_cost_endpoint = 'https://YOUR_API_GATEWAY_URL/default/analyse_function'
get_audit_endpoint = 'https://YOUR_API_GATEWAY_URL/default/analyse_function'
reset_endpoint = 'https://YOUR_API_GATEWAY_URL/default/analyse_function'
terminate_endpoint = 'https://YOUR_API_GATEWAY_URL/default/analyse_function'
scaled_terminated_endpoint = 'https://YOUR_API_GATEWAY_URL/default/analyse_function'

analysis_results = None

# Warmup endpoint to scale up resources
@app.route('/warmup', methods=['POST'])
def warmup():
    request_body = request.get_json()
    service = request_body.get('s')
    resource_count = request_body.get('r')
    
    response = requests.post(warmup_endpoint, json={'s': service, 'r': resource_count})

    if response.status_code == 200:
        return jsonify({'result': 'ok'})
    else:
        return jsonify({'result': 'ok'})

# Check if resources are ready for scaling
@app.route('/scaled_ready', methods=['GET'])
def scaled_ready():
    response = requests.get(scaled_ready_endpoint)
    response_data = response.json()
    
    # Check if 'body' key exists in response
    if 'body' in response_data:
        # Find JSON string inside the 'body' field
        body_data = json.loads(response_data['body'])
        if 'warm' in body_data:
            return jsonify({'warm': body_data['warm']})
        else:
            return jsonify({'result': 'error', 'message': 'No warm key in body data'})
    else:
        # Directly return the response if 'body' key doesn't exist
        return jsonify(response_data)

# Retrieve all relevant endpoints
@app.route('/get_endpoints', methods=['GET'])
def get_endpoints():
    try:
        response = requests.get(get_endpoints_endpoint)
        response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code
        
        endpoints_data = response.json()
        named_endpoints = [
            {'name': 'Warmup', 'endpoint': warmup_endpoint},
            {'name': 'Scaled Ready', 'endpoint': scaled_ready_endpoint},
            {'name': 'Get Warmup Cost', 'endpoint': get_warmup_cost_endpoint},
            {'name': 'Get Endpoints', 'endpoint': get_endpoints_endpoint},
            {'name': 'Analyse', 'endpoint': analyse_endpoint},
            {'name': 'Get Sig Vars 95/99', 'endpoint': get_sig_vars9599_endpoint},
            {'name': 'Get Avg Vars 95/99', 'endpoint': get_avg_vars9599_endpoint},
            {'name': 'Get Sig Profit/Loss', 'endpoint': get_sig_profit_loss_endpoint},
            {'name': 'Get Total Profit/Loss', 'endpoint': get_total_profit_loss_endpoint},
            {'name': 'Get Chart URL', 'endpoint': get_chart_url_endpoint},
            {'name': 'Get Time Cost', 'endpoint': get_time_cost_endpoint},
            {'name': 'Get Audit', 'endpoint': get_audit_endpoint},
            {'name': 'Reset', 'endpoint': reset_endpoint},
            {'name': 'Terminate', 'endpoint': terminate_endpoint},
            {'name': 'Scaled Terminated', 'endpoint': scaled_terminated_endpoint}
        ]
        return jsonify(named_endpoints)

    except Exception as e:
        return jsonify({'error': 'Internal server error'})
    
    # Wasn't able to show name of endpoints so logger was added
    # except requests.exceptions.HTTPError as errh:
    #     logger.error(f"Http Error: {errh}")
    #     return jsonify({'error': 'Http Error', 'message': str(errh)})

    # except requests.exceptions.ConnectionError as errc:
    #     logger.error(f"Error Connecting: {errc}")
    #     return jsonify({'error': 'Error Connecting', 'message': str(errc)})

    # except requests.exceptions.Timeout as errt:
    #     logger.error(f"Timeout Error: {errt}")
    #     return jsonify({'error': 'Timeout Error', 'message': str(errt)})

    # except requests.exceptions.RequestException as err:
    #     logger.error(f"OOps: Something Else: {err}")
    #     return jsonify({'error': 'Something Else', 'message': str(err)})

    # except Exception as e:
    #     logger.error(f"Internal server error: {e}")
    #     return jsonify({'error': 'Internal server error', 'message': str(e)})

# Get the warmup cost
@app.route('/get_warmup_cost', methods=['GET'])
def get_warmup_cost():
    try:
        response = requests.get(get_warmup_cost_endpoint)

        if response.status_code == 200:
            warmup_cost_data = response.json()
            billable_time = warmup_cost_data.get('billable_time')
            cost = warmup_cost_data.get('cost')
            
            return jsonify({'billable_time': billable_time, 'cost': cost})
        else:
            return jsonify({'error': 'Failed to retrieve warm-up cost'})

    except Exception as e:
        return jsonify({'error': 'Internal server error'})

# Perform analysis on stock data
@app.route('/analyse', methods=['POST'])
def analyse():
    global analysis_results
    try:
        # Get inputs
        request_body = request.get_json()
        h = int(request_body.get('h'))
        d = int(request_body.get('d'))
        t = request_body.get('t')
        p = int(request_body.get('p'))
        print("aa", h)

        # Yahoo finance data
        today = date.today()
        decade_ago = today - timedelta(days=1095)
        # Personal second letter is 'H'
        data_df = yf.download('NVDA', start=decade_ago, end=today)
        print ("ww", data_df) 

        stock_data = []
        for row in data_df.itertuples():
            stock_data.append({
                'Date': row.Index.to_pydatetime().strftime('%Y-%m-%d'),
                'Open': row.Open,
                'High': row.High,
                'Low': row.Low,
                'Close': row.Close,
                'Adj Close': row._5,
                'Volume': row.Volume,
                'Buy': 0,
                'Sell': 0,
            })
        
        # Payload for lambda function
        print("Aa", stock_data)
        payload = {
            'stock_data': stock_data,
            'minhistory': h,
            'shots': d,
            'days': p,
            'signal_type': t,
        }

        response = requests.post(analyse_endpoint, json=payload)

        if response.status_code == 200:
            abc = response.json()
            analysis_results = abc.get('analysis_results', [])
            return jsonify(analysis_results)
        else:
            return jsonify({'error': 'Error in Lambda function'})

    except Exception as e:
        return jsonify({'error': 'Internal server error'})

# Get significant vars 95/99
@app.route('/get_sig_vars9599', methods=['GET'])
def get_sig_vars9599():
    global analysis_results
    # Send GET request to lambda

    var95_list = analysis_results.get('var95', [])[:20]
    var99_list = analysis_results.get('var99', [])[:20]
    # Create a new dictionary with 'var95' and 'var99' keys
    var_values = {'var95': var95_list, 'var99': var99_list}
    print("Extracted var95 and var99 values:", var_values)
    # Return values as Json response
    return jsonify(var_values)

# Get average vars 95/99
@app.route('/get_avg_vars9599', methods=['GET'])
def get_avg_vars9599():
    global analysis_results

    try:
        var95_avg = analysis_results.get('avg_var95', 0)
        var99_avg = analysis_results.get('avg_var99', 0)
        var_values = {'var95': var95_avg, 'var99': var99_avg}
        print("Extracted avg_var95 and avg_var99 values:", var_values)
        return jsonify(var_values)

    except Exception as e:
        return jsonify({'error': 'Internal server error'})

# Get significant profit/loss
@app.route('/get_sig_profit_loss', methods=['GET'])
def get_sig_profit_loss():
    global analysis_results
    try:
        if analysis_results:
            p_loss_list = analysis_results.get('profit_loss', [])[-20:]
            pl_values = {'profit_loss': p_loss_list}
            print("Extracted profit_loss", pl_values)
            return jsonify(pl_values)
        else:
            return jsonify({'error': 'No analysis results available'})

    except Exception as e:
        return jsonify({'error': 'Internal server error'})

# Get total profit/loss
@app.route('/get_tot_profit_loss', methods=['GET'])
def get_tot_profit_loss():
    global analysis_results

    try:
        tot_loss_profit = analysis_results.get('total_profit_loss', 0)
        prof_tot_loss = {'tot_loss_profit':  tot_loss_profit}
        return jsonify(prof_tot_loss)

    except Exception as e:
        return jsonify({'error': 'Internal server error'})

# Get time cost
@app.route('/get_time_cost', methods=['GET'])
def get_time_cost():
    global analysis_results

    try:
        tot_time = analysis_results.get('time', 0)
        tot_cost = analysis_results.get('cost', 0)
        cost_time = {'time':  tot_time, 'cost': tot_cost}
        print("Extracted avg_var95 and avg_var99 values:", cost_time)
        return jsonify(cost_time)

    except Exception as e:
        return jsonify({'error': 'Internal server error'})

# Reset analysis results
@app.route('/reset', methods=['GET'])
def reset_analysis():
    global analysis_results
    # Reset analysis variable to 0
    analysis_results = 0
    return jsonify({'result': 'ok'})

# Get chart URL
@app.route('/get_chart_url', methods=['GET'])
def get_chart_url():
    response = requests.get(get_chart_url_endpoint)
    data = response.json()
    print("Full Content:\n", response.content)
    chart_url = data['chart_url']
    return jsonify({'chart_url': chart_url})


# Get audit data
@app.route('/get_audit', methods=['GET'])
def get_audit():
    try:
        response = requests.get(get_audit_endpoint)

        if response.status_code == 200:
            audit_data = response.json()
            print("Audit Data:", audit_data)
            return jsonify(audit_data)
        else:
            return jsonify({'error': 'Failed to retrieve audit data'})

    except Exception as e:
        return jsonify({'error': 'Internal server error'})

# Terminate instances
@app.route('/terminate', methods=['GET'])
def terminate_instances():
    response = requests.get(terminate_endpoint)

    if response.status_code == 200:
        return jsonify({'result': 'ok'})
    else:
        return jsonify({'result': 'ok'})

    return jsonify({'result': 'ok'})

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
