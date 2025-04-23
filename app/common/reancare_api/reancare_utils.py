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

from app.common.reancare_api.reancare_login_service import ReanCareLogin
###############################################################################

from app.common.logtime import log_execution_time
###############################################################################
@log_execution_time
async def find_patient_by_mobile(mobile, tenant_code):
    reancare_base_url = os.getenv("REANCARE_BASE_URL")
    url = f"{reancare_base_url}/patients/"
    # url = str(reancare_base_url + "/patients/")
    headers = await get_headers()
    formatted = urllib.parse.quote(mobile)
    # search_url = url + "search?phone={}".format(formatted)
    search_url = f"{url}search?tenantCode={tenant_code}&phone={formatted}"
    response = requests.get(search_url, headers=headers)
    search_result = response.json()
    if search_result['Message'] == 'No records found!':
        return None
    else:
        return search_result['Data']['Patients']['Items'][0]['UserId']

async def get_headers(create_user = False):
        login = ReanCareLogin()
        access_token = await login.get_access_token()
        if create_user:
            return {
                'x-api-key': os.getenv("REANCARE_API_KEY"),
                'Content-Type': 'application/json'
            }
        return {
            'Authorization': "Bearer " +  access_token,
            'x-api-key': os.getenv("REANCARE_API_KEY"),
            'Content-Type': 'application/json'
        }
        
async def get_tenant_by_code(tenant_code):
    url = f"{os.getenv('REANCARE_BASE_URL')}/tenants/search?code={tenant_code}"
    headers = await get_headers()
    # params = {'tenantCode': tenant_code} 

    response = requests.get(url, headers=headers)
    result = response.json()

    if response.status_code == 200 and 'Data' in result:
        tenant_data = result['Data']["TenantRecords"]['Items'][0]
        return tenant_data.get('id') 
    else:
        print(f"Failed to fetch tenant info for code {tenant_code}: {result}")
        return None
    
async def get_tenant_settings(tenant_code):
    tenant_code = tenant_code.upper()
    tenant_id = await get_tenant_by_code(tenant_code)
    url = f"{os.getenv('REANCARE_BASE_URL')}/tenant-settings/{tenant_id}"
    headers = await get_headers()

    response = requests.get(url, headers=headers)
    result = response.json()

    if response.status_code == 200 and 'Data' in result:
        return result['Data'] ["TenantSettings"]
    # Adjust based on actual response format
    else:
        print(f"Failed to fetch tenant settings for ID {tenant_id}: {result}")
        return None

async def get_appointment_followup_settings(tenant_settings: dict) -> str | None:
    if not tenant_settings:
        return None

    chatbot = tenant_settings.get("ChatBot")
    if not chatbot:
        return None

    followup = chatbot.get("AppointmentFollowup")
    if not followup:
        return None

    ehr_api_details = followup.get("AppointmentEhrApiDetails")
    if not ehr_api_details:
        return None

    mechanism = ehr_api_details.get("FollowupMechanism")
    if not mechanism:
        return None

    return mechanism.get("MessageFrequency")