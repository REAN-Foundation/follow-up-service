import json
import os
import uuid
from pygments import highlight, lexers, formatters
from app.common.enumclasses import AppStatusEnum,PatientReplyEnum
from datetime import datetime
import pytz
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
