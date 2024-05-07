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
    

def valid_patient_reply(reply):
    if reply == PatientReplyEnum.Patient_Replied_Yes:
        return(PatientReplyEnum.Patient_Replied_Yes)
    if reply == PatientReplyEnum.Patient_Replied_No:
        return(PatientReplyEnum.Patient_Replied_No)
    return(PatientReplyEnum.Invalid_Patient_Reply)

def time_of_first_reminder(patient_mobile_number):
        temp = str(patient_mobile_number)
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

        new_time = str(current_time + timedelta(minutes=6))
        date_element = new_time.split(' ')
        time_element = date_element[1].split('.')
        first_reminder_time = time_element[0]
        return first_reminder_time
