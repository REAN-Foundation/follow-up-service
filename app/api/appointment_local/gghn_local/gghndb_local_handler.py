from fastapi import APIRouter, HTTPException, Request
import boto3
# from app.common.utils import get_temp_filepath
from app.services.appointment_local_service.common_local_service.update_AFReport_local_service import UpdateFile
from app.services.appointment_local_service.gghn_local_service.gghn_login_local_service import GghnUserLogin 
from app.services.appointment_local_service.gghn_local_service.gghn_patient_code_local_service import ExtractPatientCode
from app.services.appointment_local_service.common_local_service.recent_file_local_service import RecentFile
from app.services.appointment_local_service.gghn_local_service.read_reply_report_local_service import GGHNReadReport
from app.services.appointment_local_service.common_local_service.login_service import UserLogin

async def readfile_content(date):
    try:
        print (date)
        login = GghnUserLogin()
        await login.gghnlogin()
        login = UserLogin()
        await login.login()
        patientextraction = ExtractPatientCode()
        appointmentcontent = await patientextraction.read_content(date)
        return(appointmentcontent)
        # return()
    except Exception as e:
         raise e
    
async def update_gghn_reply_by_ph(filename,phone_number, new_data):
    try:
        
        updatefile =  UpdateFile()
        updated_data = await updatefile.update_reply_by_phone(filename, phone_number,new_data)
        return(updated_data)
    except Exception as e:
         raise e

async def read_appointment_file(filename):
    try:
        reportfile = GGHNReadReport()
        filecontent = await reportfile.gghn_read_appointment_file(filename)
        return(filecontent)
    except Exception as e:
         raise e
    
async def readfile_summary(filename):
    try:
        reportfile = GGHNReadReport()
        filesummary = await reportfile.gghn_read_appointment_summary(filename)
        return(filesummary)
    except Exception as e:
         raise e

async def recent_file(file_prefix):
    recentfile = RecentFile()
    filename = await recentfile.find_recent_file(file_prefix)   
    return filename