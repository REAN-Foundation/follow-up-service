
import json
import os

import requests
from app.common.cache import cache
###########################################################
class ExtractPatientCode:
    def __init__(self):

        gghn_base_url = os.getenv("GGHN_BASE_URL")
        if gghn_base_url == None:
            raise Exception('GGHN_BASE_URL is not set')
        
        self.patient_code_url = str(gghn_base_url + "/api/PharmacyPickup")
        self.token = cache.get('gghn_access_token')
        print("gghn token",self.token)
       
    def read_content(self, date):
        self.token = cache.get('gghn_access_token')
        suburl = str(f'/QueryPatientByNextAppointment?startdate={date}T00:00:00&endDate={date}T23:59:59')
        url=str(self.patient_code_url+suburl)
        summary_data = []
        headers = {
            'Authorization': "Bearer " + self.token,
            # 'Content-Type': 'application/json'
        }
        response = requests.post(
        url,headers = headers)
        result = response.json()
        print("result",result)
        return (result)