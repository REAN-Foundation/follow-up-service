import json
import os
import uuid
from pygments import highlight, lexers, formatters
from app.common.enumclasses import AppStatusEnum,PatientReplyEnum
from datetime import datetime
import pytz
from datetime import *
from app.common.cache import cache
import urllib.parse
import requests
###############################################################################

def find_patient_by_mobile(mobile):
    reancare_base_url = os.getenv("REANCARE_BASE_URL")
    url = str(reancare_base_url + "/patients/")
    headers = get_headers()
    formatted = urllib.parse.quote(mobile)
    search_url = url + "search?phone={}".format(formatted)
    response = requests.get(search_url, headers=headers)
    search_result = response.json()
    if search_result['Message'] == 'No records found!':
        return None
    else:
        return search_result['Data']['Patients']['Items'][0]['UserId']

def get_headers(create_user = False):
        if create_user:
            return {
                'x-api-key': os.getenv("REANCARE_API_KEY"),
                'Content-Type': 'application/json'
            }
        return {
            'Authorization': "Bearer " +  cache.get('access_token'),
            'x-api-key': os.getenv("REANCARE_API_KEY"),
            'Content-Type': 'application/json'
        }