from ast import Dict
import json
import os
import requests
from app.common.cache import cache

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
        self.access_token = ''
        self.url = str(reancare_base_url)

    async def login(self):
        base_url = self.url
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
        self.access_token = result['Data']['AccessToken']

        cache.set('access_token', self.access_token)
        print('Login successful')
        return (result)

    def get_access_token(self):
        return self.access_token

