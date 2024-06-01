from ast import Dict
import json
import os
import requests
from app.common.cache import cache
from app.common.exceptions import HTTPError

###############################################################

class GghnUserLogin:
    def __init__(self):

        gghn_base_url = os.getenv("GGHN_BASE_URL")
        if gghn_base_url == None:
            raise Exception('GGHN_BASE_URL is not set')

        self.login_url = str(gghn_base_url +"/account/JWTAuthentication")
        self._username = os.getenv("GGHN_USERNAME")
        self._password = os.getenv("GGHN_PASSWORD")
        self._clientname = os.getenv("CLIENT_NAME")
        
        self.gghn_access_token = ''
        self._url = str(gghn_base_url)

    async def gghnlogin(self):
        base_url_ = self._url
        try:
            health_check_resp = requests.get(base_url_)
            print("health check resp", health_check_resp)
        except HTTPError as e:
                print(f"HTTP Error {e.status_code}: {e.message}")

        headers = {
            # 'x-api-key': self.API_KEY,
            'Content-Type': 'application/json'
        }
        body = {
            'UserName': self._username,
            'Password': self._password
        }
        try:
            response = requests.post(
            self.login_url,headers = headers, data = json.dumps(body))
        except HTTPError as e:
                print(f"HTTP Error {e.status_code}: {e.message}")
        print("Login Response",response)
        result = response.json()
        print("response",result)
        if result['fullName'] != self._clientname:
            raise Exception(result['Message'])
        self.gghn_access_token = result['token']

        cache.set('gghn_access_token', self.gghn_access_token)
        print('Login successful')
        # print('gghn_access_token',self.gghn_access_token)
        return (result)