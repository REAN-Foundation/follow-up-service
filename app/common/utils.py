import json
import os
import uuid
from pygments import highlight, lexers, formatters
from app.common.enumclasses import AppStatusEnum,PatientReplyEnum
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
   
def find_recent_file_with_prefix(folder_path, prefix):
    # Get a list of all files in the folder that start with the specified prefix
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.startswith(prefix) and os.path.isfile(os.path.join(folder_path, f))]
    
    # Sort files by modification time (most recent first)
    files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    # Return the most recently modified file with the specified prefix
    if files:
        return files[0]
    else:
        return None

 
