import requests
import hmac
import hashlib
import time

# Constants
API_ENDPOINT = 'https://wbsapi.withings.net'
OAUTH2_GRANT_TYPE_AUTHORIZATION_CODE = 'authorization_code'
CLIENT_ID = '83070902596cc1b9be5c11254f1641d015fa5e996c237d52b77f473b34b9a5f4'
CLIENT_SECRET = 'c9adde79fbe7ba4210c442f16a5ba2c63246a5f004fcee438488937c04ef56d1'

# Function to generate the HMAC signature
def sign(params, client_secret):
    params_to_sign = {
        'action': params['action'],
        'client_id': params['client_id']
    }
    if 'timestamp' in params:
        params_to_sign['timestamp'] = params['timestamp']
    if 'nonce' in params:
        params_to_sign['nonce'] = params['nonce']
    # Sort and join the values by a comma
    sorted_values = ','.join(str(value) for value in params_to_sign.values()) 
    # Create HMAC using SHA256
    hmac_obj = hmac.new(client_secret.encode(), sorted_values.encode(), hashlib.sha256) 
    return hmac_obj.hexdigest()

# Function to get the nonce from the API
def get_nonce(timestamp):
    params = {
        'action': 'getnonce',
        'client_id': CLIENT_ID,
        'timestamp': timestamp
    }
    
    # Add the HMAC signature to the parameters
    params['signature'] = sign(params, CLIENT_SECRET)

    # Make a POST request using the requests library
    response = requests.post(API_ENDPOINT + '/v2/signature', data=params)
    
    # Parse the JSON response
    data = response.json()
    
    return data['body']['nonce']

# Main function to get and display the nonce
def main():
    now = int(time.time())  # Current Unix timestamp
    nonce = get_nonce(now)
    print(nonce)

# Run the main function
if __name__ == "__main__":
    main()