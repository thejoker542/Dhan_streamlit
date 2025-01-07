from datetime import datetime, timedelta, date
from  time import sleep
import os
from fyers_apiv3 import fyersModel
from fyers_apiv3.FyersWebsocket import data_ws
import time 
import pyotp
import requests
import json
import math
import pytz
from urllib.parse import parse_qs,urlparse
import warnings
import pandas as pd
pd.set_option('display.max_columns', None)
warnings.filterwarnings('ignore')

import base64
def getEncodedString(string):
    string = str(string)
    base64_bytes = base64.b64encode(string.encode("ascii"))
    return base64_bytes.decode("ascii")

redirect_uri = "https://127.0.0.1:5000/"

client_id= "OGS4N9MW72-100"
secret_key= "T7ED0IDY1L"
FY_ID = "FA2060"  # Your fyers ID
# Authentication Details
TOTP_KEY = "FTJEBP37ZFWVUTGOBAJEXTS7D3CUPE7M"  # TOTP secret for 2Factor
PIN = "5417"  # User pin for fyers account

URL_SEND_LOGIN_OTP="https://api-t2.fyers.in/vagator/v2/send_login_otp_v2"
res = requests.post(url=URL_SEND_LOGIN_OTP, json={"fy_id":getEncodedString(FY_ID),"app_id":"2"}).json()   
print(res) 

if datetime.now().second % 30 > 27 : sleep(5)
URL_VERIFY_OTP="https://api-t2.fyers.in/vagator/v2/verify_otp"
res2 = requests.post(url=URL_VERIFY_OTP, json= {"request_key":res["request_key"],"otp":pyotp.TOTP(TOTP_KEY).now()}).json()  
print(res2) 


ses = requests.Session()
URL_VERIFY_OTP2="https://api-t2.fyers.in/vagator/v2/verify_pin_v2"
payload2 = {"request_key": res2["request_key"],"identity_type":"pin","identifier":getEncodedString(PIN)}
res3 = ses.post(url=URL_VERIFY_OTP2, json= payload2).json()  
print(res3) 


ses.headers.update({
    'authorization': f"Bearer {res3['data']['access_token']}"
})


TOKENURL="https://api-t1.fyers.in/api/v3/token"
payload3 = {"fyers_id":FY_ID,
           "app_id":client_id[:-4],
           "redirect_uri":redirect_uri,
           "appType":"100","code_challenge":"",
           "state":"None","scope":"","nonce":"","response_type":"code","create_cookie":True}

res3 = ses.post(url=TOKENURL, json= payload3).json()  
print(res3)


url = res3['Url']
print(url)
parsed = urlparse(url)
auth_code = parse_qs(parsed.query)['auth_code'][0]
auth_code


grant_type = "authorization_code" 

response_type = "code"  

session = fyersModel.SessionModel(
    client_id=client_id,
    secret_key=secret_key, 
    redirect_uri=redirect_uri, 
    response_type=response_type, 
    grant_type=grant_type
)

# Set the authorization code in the session object
session.set_token(auth_code)

# Generate the access token using the authorization code
response = session.generate_token()

# Print the response, which should contain the access token and other details
#print(response)


access_token = response['access_token']
with open('access_token.txt', 'w') as f:
    f.write(access_token)
# Initialize the FyersModel instance with your client_id, access_token, and enable async mode
fyers = fyersModel.FyersModel(client_id=client_id, is_async=False, token=access_token, log_path=os.getcwd())

# Make a request to get the user profile information
a= fyers.get_profile()
print(a)

def download_master_instruments():
    try:
        instrument_url = "https://public.fyers.in/sym_details/NSE_FO_sym_master.json"
        response = requests.get(instrument_url)
        data = response.json()

        df = pd.DataFrame.from_dict(data, orient='index')
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'symbol'}, inplace=True)

        important_cols = ['symbol', 'fyToken', 'exToken', 'exSymbol', 'symbolDesc', 
                        'segment', 'exchange', 'exchangeName', 'expiryDate', 
                        'strikePrice', 'optType', 'minLotSize', 'tickSize']
        other_cols = [col for col in df.columns if col not in important_cols]
        final_cols = important_cols + other_cols
        df = df[final_cols]

        # Also save to CSV as backup
        df.to_csv("master_file.csv", index=False)


    except Exception as e:
        print("error", e)
        return False

def download_master_instruments():
    try:
        # URL to fetch the master instruments data
        instrument_url = "https://public.fyers.in/sym_details/NSE_FO_sym_master.json"
        response = requests.get(instrument_url)
        data = response.json()

        # Convert the JSON data to a DataFrame
        df = pd.DataFrame.from_dict(data, orient='index')
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'symbol'}, inplace=True)

        # Define the columns to keep in the final CSV
        columns_to_keep = ['symbol', 'exSymbol', 'segment', 'exchange', 'expiryDate', 'strikePrice','exSymName']

        # Filter the DataFrame to keep only the required columns
        df = df[columns_to_keep]

        # Save the filtered DataFrame to a CSV file
        df.to_csv("master_file.csv", index=False)
        print("Master instruments data saved to master_file.csv")

    except Exception as e:
        print("Error:", e)
        return False

# Example usage
download_master_instruments()


download_master_instruments()

data = {
    "symbol":"NSE:NIFTY50-INDEX",
    "resolution":"5",
    "date_format":"1",
    "range_from":"2025-01-01",
    "range_to":"2025-01-10",
    "cont_flag":"1"
}

response = fyers.history(data=data)
df = pd.DataFrame(response)
df.to_csv('SBIN.csv', index=False)

def historical_data(symbol):
    # Calculate date range
    today = datetime.today()
    range_from = (today - timedelta(days=10)).strftime('%Y-%m-%d')  # Today - 10 days
    range_to = (today + timedelta(days=1)).strftime('%Y-%m-%d')     # Today + 1 day

    # Prepare the data payload
    data = {
        "symbol": symbol,
        "resolution": "5",
        "date_format": "1",
        "range_from": range_from,
        "range_to": range_to,
        "cont_flag": "1"
    }

    # Fetch historical data (replace with your actual API call)
    response = fyers.history(data=data)

    # Check if the response contains valid data
    if "candles" not in response:
        print("No data found in the response.")
        return

    # Extract the candles data
    candles = response["candles"]

    # Convert the data into a DataFrame with proper columns
    df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])

    # Convert timestamp to a readable date format
    df["date"] = pd.to_datetime(df["timestamp"], unit="s")

    # Reorder columns
    df = df[["date", "open", "high", "low", "close", "volume"]]

    # Save the DataFrame to a CSV file
    filename = f"{symbol.replace(':', '_')}.csv"  # Replace ':' with '_' in filename
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

# Example usage
historical_data("NSE:NIFTY50-INDEX")

