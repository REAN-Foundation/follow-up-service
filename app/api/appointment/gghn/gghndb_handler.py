

from fastapi import APIRouter, HTTPException, Request
import boto3
from app.services.appointment_service.common_service.update_AFReport_service import UpdateFile
from app.services.appointment_service.gghn_service.gghn_login_service import GghnUserLogin 
from app.services.appointment_service.gghn_service.gghn_patient_code_service import ExtractPatientCode
from app.services.appointment_service.gghn_service.read_reply_report import GGHNReadReport
from app.services.appointment_service.common_service.login_service import UserLogin
from app.services.appointment_service.common_service.recent_file_service import RecentFile

def readfile_content(date):
    try:
        print (date)
        login = GghnUserLogin()
        login.gghnlogin()
        login = UserLogin()
        login.login()
        patientextraction = ExtractPatientCode()
        appointmentcontent = patientextraction.read_content(date)
        return(appointmentcontent)
        # return()
    except Exception as e:
         raise e
    
async def update_gghn_reply_by_ph(filename,phone_number, new_data):
    try:
        updatefile =  UpdateFile()
        updated_data = updatefile.update_reply_by_phone(filename,phone_number,new_data)
        return(updated_data)
    except Exception as e:
         raise e

async def read_appointment_file(filename):
    try:
        reportfile = GGHNReadReport()
        filecontent = reportfile.gghn_read_appointment_file(filename)
        return(filecontent)
    except Exception as e:
         raise e
    
async def readfile_summary(filename):
    try:
        reportfile = GGHNReadReport()
        filesummary = reportfile.gghn_read_appointment_summary(filename)
        return(filesummary)
    except Exception as e:
         raise e
   
def recent_file(file_prefix):
    fileprefix = file_prefix
    print(f"fileprefix {fileprefix}")
    recentfile = RecentFile()
    filename = recentfile.find_recent_file(fileprefix)   
    return filename