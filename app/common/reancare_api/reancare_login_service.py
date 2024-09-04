from ast import Dict
from datetime import datetime
import json
import os
import requests
from app.common.cache import cache
from app.common.logtimeing import log_execution_time

###############################################################

class ReanCareLogin:
    def __init__(self):

        reancare_base_url = os.getenv("REANCARE_BASE_URL")
        if reancare_base_url == None:
            raise Exception('REANCARE_BASE_URL is not set')

        self.login_url = str(reancare_base_url +"/users/login-with-password")
        self.username = os.getenv("USER_NAME")
        self.password = os.getenv("PASSWORD")
        self.API_KEY = os.getenv("REANCARE_API_KEY")
        # self.access_token
        self.url = str(reancare_base_url)
    @log_execution_time
    async def login(self):
        base_url = self.url
        token_validtill = ''
        reancare_access_token = ''
        health_check_resp = requests.get(base_url)
        print("health check resp", health_check_resp)
        headers = {
            'x-api-key': self.API_KEY,
            'Content-Type': 'application/json'
        }
        body = {
            'UserName': self.username,
            'Password': self.password
        }
        response = requests.post(
            self.login_url, headers = headers, data = json.dumps(body))

        result = response.json()
        if result['Status'] == 'failure':
            raise Exception(result['Message'])
        reancare_access_token = result['Data']['AccessToken']
        token_validtill = result['Data']['SessionValidTill']
        print("validtill..",token_validtill)
        cache.set('Valid_rc_token_date', token_validtill)
        cache.set('access_token', reancare_access_token)
        print('Login successful')
        return (result)

   
    async def get_access_token(self):
        token = cache.get('access_token')
        validtill_date = cache.get('Valid_rc_token_date')
        date = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        if(token == None or validtill_date < date or validtill_date == None):
            print('need to login')
            await self.login()
        # print('token valid no need to login')
        access_token = cache.get('access_token')
        return access_token

