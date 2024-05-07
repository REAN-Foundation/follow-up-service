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

def print_colorized_json(obj):
    jsonStr = json.dumps(obj.__dict__, default=str, indent=2)
    colored = highlight(jsonStr, lexers.JsonLexer(), formatters.TerminalFormatter())
    print(colored)

def generate_uuid4():
    return str(uuid.uuid4())

def get_temp_filepath(file_name):
    temp_folder = os.path.join(os.getcwd(), "temp")
    if not os.path.exists(temp_folder):
        os.mkdir(temp_folder)
    return os.path.join(temp_folder, file_name)

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
   
def find_recent_file_with_prefix(folder_path, prefix):
    # Get a list of all files in the folder that start with the specified prefix
    files = [f for f in os.listdir(folder_path) if f.startswith(prefix) and os.path.isfile(os.path.join(folder_path, f))]
    
    # If files are found, get the most recently modified file
    if files:
        most_recent_file = max(files, key=lambda x: os.path.getmtime(os.path.join(folder_path, x)))
        return most_recent_file
    else:
        return None
    
def is_date_valid(date_string):
    # Convert date string to date object using EST time zone 
    date_object = datetime.strptime(date_string, "%Y-%m-%d")

    est_timezone = pytz.timezone('America/New_York')
    est_date_object = est_timezone.localize(date_object)

    # Create todays date object using EST time zone

    # Define the UTC datetime object
    utc_datetime = datetime.utcnow()

    # Convert UTC datetime to EST timezone
    utc_timezone = pytz.timezone('UTC')
    est_timezone = pytz.timezone('America/New_York')

    utc_datetime = utc_timezone.localize(utc_datetime)
    est_datetime = utc_datetime.astimezone(est_timezone)

    est_today = est_datetime.replace(hour=0, minute=0, second=0, microsecond=0)

    if est_date_object < est_today:
        return False
    return True

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

def open_file_in_readmode(filename):        
        try:
            filepath = get_temp_filepath(filename)
            with open(filepath, 'r') as file:
                file_data = json.load(file)
            return(file_data)
        except Exception as e:
            # Handle other exceptions
            print(f"An unexpected error occurred in open file in readmode{filename}: {e}")
            return None
        

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