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
        