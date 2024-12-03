import json
import os
import uuid
from fastapi import HTTPException
from pygments import highlight, lexers, formatters
from app.common.enumclasses import AppStatusEnum,PatientReplyEnum
from datetime import datetime
import pytz
from datetime import *
from app.common.cache import cache
import urllib.parse
import requests

from app.common.logtime import log_execution_time

# from app.services.common.db_service import DatabaseService


###############################################################################

def validate_mobile(mobile):
    # if not bool(mobile.strip()) or not mobile.startswith('+1-'):
        if not bool(mobile.strip()):
            print('Invalid Mobile Number ', mobile)
            return False
        ten_digit = mobile.split('-')[1]
        if len(ten_digit) == 10 and ten_digit.isnumeric():
            return True

def valid_appointment_status(status):
    if status == AppStatusEnum.Patient_In_Lobby:
        return(AppStatusEnum.Patient_In_Lobby)
    if status == AppStatusEnum.Patient_Seen:
        return(AppStatusEnum.Patient_Seen)
    if status  == AppStatusEnum.Patient_Cancelled:
        return(AppStatusEnum.Patient_Cancelled)
    if status == AppStatusEnum.Pending_Arrival:
        return(AppStatusEnum.Pending_Arrival)
    
async def valid_patient_reply(reply):
    if reply == PatientReplyEnum.Patient_Replied_Yes:
        return(PatientReplyEnum.Patient_Replied_Yes)
    if reply == PatientReplyEnum.Patient_Replied_No:
        return(PatientReplyEnum.Patient_Replied_No)
    return(PatientReplyEnum.Invalid_Patient_Reply)

async def time_of_first_reminder(patient_mobile_number):
        temp = str(patient_mobile_number)
        if(temp == ""):
             print("No phone number is allocated")
             first_reminder_time = None
             return first_reminder_time
        else:
            if(temp.startswith('+1')):
                desired_timezone = 'America/Cancun'
                utc_now = datetime.utcnow()
                # Convert UTC time to the desired time zone
                desired_timezone_obj = pytz.timezone(desired_timezone)
                current_time = utc_now.replace(tzinfo=pytz.utc).astimezone(desired_timezone_obj)
            if(temp.startswith('+91')):
                desired_timezone = 'Asia/Kolkata'
                utc_now = datetime.utcnow()
                # Convert UTC time to the desired time zone
                desired_timezone_obj = pytz.timezone(desired_timezone)
                current_time = utc_now.replace(tzinfo=pytz.utc).astimezone(desired_timezone_obj)
            if(temp.startswith('+234')):
                desired_timezone = 'Africa/Lagos'
                utc_now = datetime.utcnow()
                # Convert UTC time to the desired time zone
                desired_timezone_obj = pytz.timezone(desired_timezone)
                current_time = utc_now.replace(tzinfo=pytz.utc).astimezone(desired_timezone_obj)

            new_time = str(current_time + timedelta(minutes=20))
            date_element = new_time.split(' ')
            time_element = date_element[1].split('.')
            first_reminder_time = time_element[0]
            return first_reminder_time

async def has_patient_replied_infile(prefix_string, mobile, reminder_date):
        print(f'validating whether Patient already replyed for {mobile} : {reminder_date}')
        filename=str(prefix_string+reminder_date+'.json')
        f_path=(os.getcwd()+"/temp/"+filename)
        flag = 0
        
        if os.path.exists(f_path):
            with open(f_path, 'r') as file:
                data = json.load(file)

                for element in data:
                    if element['phone_number'] == mobile:
                        flag = 1

                if flag == 0:
                    return False
                
                for item in data:
                    if item['phone_number'] == mobile:
                        if item['patient_replied'] == PatientReplyEnum.Invalid_Patient_Reply:
                            return False
                return True
        return False

@log_execution_time
async def has_patient_replied(prefix_string, mobile, reminder_date,storage_service):
        # initial = prefix_string
        # ini_prefix = initial.split('_')
        # collect_prefix = ini_prefix[0]
        print(f'validating whether Patient already replyed for {mobile} : {reminder_date}')
        # db_connect = DatabaseService()
        filename=str(prefix_string+reminder_date+'.json')
        f_data= await storage_service.search_file(filename)
        flag = 0
        if(f_data == None):
            print(f"No file exsist with name{filename}")
        
        else:
            data = f_data
            for element in data:
                if element['phone_number'] == mobile:
                    flag = 1

            if flag == 0:
                return False
            
            for item in data:
                if item['phone_number'] == mobile:
                    if item['patient_replied'] == PatientReplyEnum.Invalid_Patient_Reply:
                        return False
            return True
        return False


async def form_file_name(client,date):
    try:
        file_name=(f"{client}_appointment_{date}.json").lower()
        filename = file_name.replace(' ', '')
        return(filename)
    except Exception as e:
        print(e)
        return(None)

async def get_client_name(client):
    try:
        dev_bot = os.getenv("DEV_BOT")
        if client == dev_bot:
            client_name = 'gghn'
            return client_name
        if client.__contains__('_'):
            client_init = client.split('_')
            return client_init[0]
        else:
            return client
              
    except Exception as e:
        print(e)
        return(None)    
    
async def map_reply(reply):
    try:
        reply_str = reply.lower()
        if(reply_str == 'yes'):
            reply = 'Yes'
            return(reply)
        if(reply_str == 'no'):
            reply = 'No'
            return(reply)
        if(reply_str == 'not replied'):
            reply = 'Not replied'
            return(reply)
    except Exception as e:
        print(e)
        return(None)