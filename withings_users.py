import json
import time
import urllib.parse
import http.client
import sys
import os
import requests

# Constants
API_ENDPOINT = "https://wbsapi.withings.net"
OAUTH2_GRANT_TYPE_AUTHORIZATION_CODE = "authorization_code"
CLIENT_ID = '83070902596cc1b9be5c11254f1641d015fa5e996c237d52b77f473b34b9a5f4'
CLIENT_SECRET = 'c9adde79fbe7ba4210c442f16a5ba2c63246a5f004fcee438488937c04ef56d1'
MEASURE_TYPE_HEIGHT = 4
MEASURE_TYPE_WEIGHT = 1
UNIT_HEIGHT_M = 6
UNIT_HEIGHT_IN = 7
UNIT_WEIGHT_KG = 1
UNIT_WEIGHT_LB = 2
UNIT_WEIGHT_STLB = 14
UNIT_DISTANCE_KM = 6
UNIT_DISTANCE_YD = 8
UNIT_TEMPERATURE_C = 11
UNIT_TEMPERATURE_F = 13

import json
import time
import urllib.parse
import http.client
import sys
import os
import requests

# Constants
API_ENDPOINT = "https://wbsapi.withings.net"
OAUTH2_GRANT_TYPE_AUTHORIZATION_CODE = "authorization_code"
CLIENT_ID = 'XXXXXX'
CLIENT_SECRET = 'YYYYYY'
MEASURE_TYPE_HEIGHT = 4
MEASURE_TYPE_WEIGHT = 1
UNIT_HEIGHT_M = 6
UNIT_HEIGHT_IN = 7
UNIT_WEIGHT_KG = 1
UNIT_WEIGHT_LB = 2
UNIT_WEIGHT_STLB = 14
UNIT_DISTANCE_KM = 6
UNIT_DISTANCE_YD = 8
UNIT_TEMPERATURE_C = 11
UNIT_TEMPERATURE_F = 13

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the functions from signature.py
from yapi.utilities.signature import get_nonce, sign

def activate(nonce, user, mac_addresses=None):
    params = {
        "action": "activate",
        "client_id": CLIENT_ID,
        "nonce": nonce,
        "email": user["email"],
        "shortname": user["shortname"],
        "gender": user["gender"],
        "birthdate": user["birthdate"],
        "measures": json.dumps(user["measures"]),
        "external_id": user["external_id"],
        "mailingpref": user["mailingpref"],
        "unit_pref": json.dumps(user["unit_pref"]),
        "preflang": user["preflang"],
        "timezone": user["timezone"]
    }
    
    if mac_addresses:
        params["mac_addresses"] = json.dumps(mac_addresses)

    if "firstname" in user:
        params["firstname"] = user["firstname"]
    if "lastname" in user:
        params["lastname"] = user["lastname"]
    if "phonenumber" in user:
        params["phonenumber"] = user["phonenumber"]
    if "goals" in user:
        params["goals"] = user["goals"]
    if "recovery_code" in user:
        params["recovery_code"] = user["recovery_code"]

    params["signature"] = sign(params, CLIENT_SECRET)

    conn = http.client.HTTPSConnection("wbsapi.withings.net")
    conn.request("POST", "/v2/user", urllib.parse.urlencode(params),
                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    response = conn.getresponse()
    data = json.loads(response.read())
    conn.close()
    return data

def link(mac_addresses, at):
  
    params = {
        "action": "link",
        "mac_addresses": json.dumps(mac_addresses)
    }
    
    r = requests.post(
        API_ENDPOINT + "/v2/user",
        headers = {"Authorization": "Bearer " + at},
        data = params
    )
    
    print(r)
    print(r.json())
    
def get_user(email):
    
    nonce = get_nonce(int(time.time()))
    
    params = {
        "action": "get",
        "client_id": CLIENT_ID,
        "nonce": nonce,
        "email": email
    }

    params["signature"] = sign(params, CLIENT_SECRET)

    conn = http.client.HTTPSConnection("wbsapi.withings.net")
    conn.request("POST", "/v2/user", urllib.parse.urlencode(params),
                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    response = conn.getresponse()
    data = json.loads(response.read())
    conn.close()
    return data

def get_users(email = None):
    
    nonce = get_nonce(int(time.time()))
    
    params = {
        "action": "listusers",
        "client_id": CLIENT_ID,
        "nonce": nonce,
    }

    params["signature"] = sign(params, CLIENT_SECRET)

    conn = http.client.HTTPSConnection("wbsapi.withings.net")
    conn.request("POST", "/v2/oauth2", urllib.parse.urlencode(params),
                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    response = conn.getresponse()
    data = json.loads(response.read())
    conn.close()
    
    if email:
        for user in data["body"]["users"]:
            if user["email"] == email.lower():
                return user
        print("User not found")
        return None
    return data

def get_access_token(userid):
    nonce = get_nonce(int(time.time()))
    
    params = {
        "action": "recoverauthorizationcode",
        "client_id": CLIENT_ID,
        "nonce": nonce,
        "userid": userid
    }

    params["signature"] = sign(params, CLIENT_SECRET)

    conn = http.client.HTTPSConnection("wbsapi.withings.net")
    conn.request("POST", "/v2/oauth2", urllib.parse.urlencode(params),
                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    response = conn.getresponse()
    auth = json.loads(response.read())
    conn.close()
    
    try:
        code = auth["body"]["user"]["code"]
    except KeyError:
        print("Cannot get authorization code")
        print(json.dumps(auth, indent=4))
        return None
    
    params = {
        "action": "requesttoken",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": OAUTH2_GRANT_TYPE_AUTHORIZATION_CODE,
        "code": code
    }
    
    r = requests.post(API_ENDPOINT + "/v2/oauth2", data = params)
    data = r.json()
    
    return data

def get_devices(at):
    params = {
        "action": "getdevice"
    }

    headers = {
        "Authorization": f"Bearer {at}"
    }

    response = requests.post(
        API_ENDPOINT + "/v2/user",
        headers=headers,
        data=params
    )

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None
    
def get_user(email):
    nonce = get_nonce(int(time.time()))
    
    params = {
        "action": "get",
        "client_id": CLIENT_ID,
        "nonce": nonce,
        "email": email
    }

    params["signature"] = sign(params, CLIENT_SECRET)

    response = requests.post(
        API_ENDPOINT + "/v2/user",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=params
    )

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def main():
    scale_mac = "00:24:e4:ec:ac:f4"
    sleep_mac = "00:24:e4:fd:72:38"
    hub_mac = "00:24:e4:b1:15:be"
    mac_addresses = [hub_mac, sleep_mac]
    
    email = "jacksamuelmanners+CT1@gmail.com"
    
    user = get_users(email = email)
    print(json.dumps(user, indent=4))
    
    auth = get_access_token(user["userid"])
    print(json.dumps(auth, indent=4))
    if not auth:
        return
    
    at = auth["body"]["access_token"]
    
    link(mac_addresses, at)
    
    devices = get_devices(at)
    print(json.dumps(devices, indent=4))
        
    user_data = get_user(email)
    print(json.dumps(user_data, indent=4))
    
    return
    
    measures = [
        {"value": 179, "unit": -2, "type": MEASURE_TYPE_HEIGHT},  # 178cm
        {"value": 70, "unit": 0, "type": MEASURE_TYPE_WEIGHT}    # 70kg
    ]

    unit_pref = {
        "weight": UNIT_WEIGHT_KG,
        "height": UNIT_HEIGHT_M,
        "distance": UNIT_DISTANCE_KM,
        "temperature": UNIT_TEMPERATURE_C
    }
    
    # The birthdate should be in the format of Unix timestamp
    birthdate_string = "1997-01-03" # YYYY-MM-DD
    birthdate = int(time.mktime(time.strptime(birthdate_string, "%Y-%m-%d")))

    mandatory_params_user = {
        "mailingpref": 0,
        "birthdate": birthdate,
        "measures": measures,
        "gender": 0,
        "preflang": "en_US",
        "unit_pref": unit_pref,
        "email": "jacksamuelmanners+CT1@gmail.com",
        "timezone": "Australia/Adelaide",
        "shortname": "CT1",
        "external_id": "jackmanners-CT1",
    }

    optional_params_user = {
        "firstname": "Jack",
        "lastname": "Manners",
        "recovery_code": "jm1234",
    }

    user = {**mandatory_params_user, **optional_params_user}
    print(user)
    
    now = int(time.time())
    nonce = get_nonce(now)
    response = activate(nonce, user)

    print(json.dumps(response, indent=4))

if __name__ == "__main__":
    main()