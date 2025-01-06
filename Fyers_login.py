import pandas as pd
from fyers_apiv3 import fyersModel
from datetime import datetime, timedelta, date
from time import sleep
import pyotp
import requests
import json
import math
import pytz
from urllib.parse import parse_qs, urlparse
import warnings
pd.set_option('display.max_columns', None)
warnings.filterwarnings('ignore')
import base64
import os
import redis
import time
from logger import logger
from config import fyersconfig, RedisConfig

class FyersLogin:
    def __init__(self):
        self.client_id = fyersconfig.BROKER_APID
        self.secret_key = fyersconfig.BROKER_SECRETKEY
        self.redirect_uri = fyersconfig.REDIRECT_URL
        self.fy_id = fyersconfig.BROKER_ACC
        self.totp_key = fyersconfig.TOTP_KEY
        self.pin = fyersconfig.PIN
        self.grant_type = fyersconfig.GRANT_TYPE
        self.response_type = fyersconfig.RESPONSE_TYPE
        self.state = fyersconfig.STATE
        self.redis_client = redis.Redis(
            host=RedisConfig.REDIS_HOST,
            port=RedisConfig.REDIS_PORT,
            db=RedisConfig.REDIS_DB
        )
        
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
            logger.debug({"message": "Login OTP sent", "response": res})

            if datetime.now().second % 30 > 27: 
                sleep(5)

            # Verify OTP
            URL_VERIFY_OTP = "https://api-t2.fyers.in/vagator/v2/verify_otp"
            res2 = requests.post(
                url=URL_VERIFY_OTP, 
                json={"request_key": res["request_key"], "otp": pyotp.TOTP(self.totp_key).now()}
            ).json()
            logger.debug({"message": "OTP verified", "response": res2})

            # Verify PIN
            ses = requests.Session()
            URL_VERIFY_PIN = "https://api-t2.fyers.in/vagator/v2/verify_pin_v2"
            payload2 = {
                "request_key": res2["request_key"],
                "identity_type": "pin",
                "identifier": self.getEncodedString(self.pin)
            }
            res3 = ses.post(url=URL_VERIFY_PIN, json=payload2).json()
            logger.debug({"message": "PIN verified", "response": res3})

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
            logger.debug({"message": "Token URL generated", "response": res3})

            # Parse auth code from URL
            url = res3['Url']
            parsed = urlparse(url)
            auth_code = parse_qs(parsed.query)['auth_code'][0]
            logger.debug({"message": "Auth code extracted", "auth_code": auth_code})

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
            logger.debug({"message": "Access token generated", "response": response})

            access_token = response['access_token']
            
            # Store in Redis
            self.redis_client.set('access_token', access_token)
            self.redis_client.set('token_timestamp', str(int(time.time())))
            
            # Also save to file as backup
            with open("fyers_token.txt", "w") as f:
                f.write(access_token)
                
            logger.info({"message": "New access token generated and stored"})
            return access_token

        except Exception as e:
            logger.error({"error": f"Failed to generate access token: {str(e)}"})
            return None

    def getEncodedString(self, string):
        """Encode string to base64"""
        string = str(string)
        base64_bytes = base64.b64encode(string.encode("ascii"))
        return base64_bytes.decode("ascii")

    def download_master_instruments(self):
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

            # Save to Redis
            redis_client = redis.Redis(
                host=RedisConfig.REDIS_HOST,
                port=RedisConfig.REDIS_PORT,
                db=RedisConfig.REDIS_DB
            )
            redis_client.set('master_instruments', df.to_json())
            logger.debug({"message": "Master instruments saved to Redis"})

            # Also save to CSV as backup
            df.to_csv("master_instruments_file.csv", index=False)
            logger.info({"message": "Master instruments file downloaded and saved"})
            return True

        except Exception as e:
            logger.error({"error": f"Failed to download master instruments: {str(e)}"})
            return False
