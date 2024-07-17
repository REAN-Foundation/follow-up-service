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
   

    
async def is_date_valid(date_string):
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
        
async def format_date_(date_string):
    try: 
        print("in date",date_string)
        d_str = date_string.split('-')
        if(d_str[0].startswith('0') or d_str[2].startswith('0')):
            datefirst = int(d_str[0])
            datelast =  int(d_str[2])
            date_str = (f"{datefirst}-{d_str[1]}-{datelast}")
            return(date_str)
        else: 
            date_str = date_string 
            return(date_str) 
    except Exception as e:
        print(e)
        return(None)
        
          
    
async def format_phone_number(phone):
    try:
        ph_number = (f"+{phone}")
        number = ph_number.replace(' ', '')
        return(number)
    except Exception as e:
        print(e)
        return(None)