import json
import time
import logging
import requests
from urllib.parse import urlparse, parse_qs
import pyotp
from fyers_apiv3 import fyersModel
import base64
import datetime
import pandas as pd
from datetime import datetime, timedelta, date
from time import sleep
import json
import math
import pytz
import warnings
pd.set_option('display.max_columns', None)
warnings.filterwarnings('ignore')
import os
# Constants
BROKER_APID = "OGS4N9MW72-100"
BROKER_SECRETKEY = "T7ED0IDY1L"
BROKER_ACC = "FA2060"  # Your fyers ID
REDIRECT_URL = "https://127.0.0.1:8080/"

# Authentication Details
TOTP_KEY = "FTJEBP37ZFWVUTGOBAJEXTS7D3CUPE7M"  # TOTP secret for 2Factor
PIN = "5417"  # User pin for fyers account

GRANT_TYPE = "authorization_code"
RESPONSE_TYPE = "code"
STATE = "sample"
class FyersLogin:
    def __init__(self):
        self.client_id = BROKER_APID
        self.secret_key =BROKER_SECRETKEY
        self.redirect_uri = REDIRECT_URL
        self.fy_id = BROKER_ACC
        self.totp_key = TOTP_KEY
        self.pin = PIN
        self.grant_type = GRANT_TYPE
        self.response_type= RESPONSE_TYPE
        self.state = STATE
    def getEncodedString(self, string):
        """Encode string to base64"""
        string = str(string)
        base64_bytes = base64.b64encode(string.encode("ascii"))
        return base64_bytes.decode("ascii")



    def generate_new_token(self):
        """Generate new access token - alias for generate_access_token"""
        return self.generate_access_token()

    def generate_access_token(self):
        """Generate new access token"""
        try:
            # Send login OTP
            URL_SEND_LOGIN_OTP = "https://api-t2.fyers.in/vagator/v2/send_login_otp_v2"
            res = requests.post(
                url=URL_SEND_LOGIN_OTP, 
                json={"fy_id": self.getEncodedString(self.fy_id), "app_id": "2"}
            ).json()

            if datetime.now().second % 30 > 27: 
                sleep(5)

            # Verify OTP
            URL_VERIFY_OTP = "https://api-t2.fyers.in/vagator/v2/verify_otp"
            res2 = requests.post(
                url=URL_VERIFY_OTP, 
                json={"request_key": res["request_key"], "otp": pyotp.TOTP(self.totp_key).now()}
            ).json()

            # Verify PIN
            ses = requests.Session()
            URL_VERIFY_PIN = "https://api-t2.fyers.in/vagator/v2/verify_pin_v2"
            payload2 = {
                "request_key": res2["request_key"],
                "identity_type": "pin",
                "identifier": self.getEncodedString(self.pin)
            }
            res3 = ses.post(url=URL_VERIFY_PIN, json=payload2).json()
            
            ses.headers.update({
                'authorization': f"Bearer {res3['data']['access_token']}"
            })

            # Get token
            TOKENURL = "https://api-t1.fyers.in/api/v3/token"
            payload3 = {
                "fyers_id": self.fy_id,
                "app_id": self.client_id[:-4],
                "redirect_uri": self.redirect_uri,
                "appType": "100",
                "code_challenge": "",
                "state": "None",
                "scope": "",
                "nonce": "",
                "response_type": "code",
                "create_cookie": True
            }
            res3 = ses.post(url=TOKENURL, json=payload3).json()
            print("token generated")

            # Parse auth code from URL
            url = res3['Url']
            parsed = urlparse(url)
            auth_code = parse_qs(parsed.query)['auth_code'][0]

            # Generate access token
            session = fyersModel.SessionModel(
                client_id=self.client_id,
                secret_key=self.secret_key,
                redirect_uri=self.redirect_uri,
                response_type=self.response_type,
                grant_type=self.grant_type
            )
            session.set_token(auth_code)
            response = session.generate_token()
            print("message Access token generated")

            access_token = response['access_token']


            # Also save to file as backup
            with open("fyers_token.txt", "w") as f:
                f.write(access_token)

            return access_token

        except Exception as e:
            print("some error")
            return 
    def run_function(self):
        """Run the function to generate a new access token."""
        self.generate_access_token()

if __name__ == "__main__":
    fyers_login = FyersLogin()
    fyers_login.run_function()