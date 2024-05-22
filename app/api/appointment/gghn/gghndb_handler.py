

from fastapi import APIRouter, HTTPException, Request
import boto3
from app.services.appointment.common_service.update_AFReport_service import UpdateFile
from app.services.appointment.gghn_service.gghn_login_service import GghnUserLogin 
from app.services.appointment.gghn_service.gghn_patient_code_service import ExtractPatientCode
from app.services.appointment.gghn_service.read_reply_report import GGHNReadReport
from app.services.appointment.common_service.login_service import UserLogin

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
    
async def update_gghn_reply_by_ph(filename, file_path, phone_number, new_data):
    try:
        updatefile =  UpdateFile()
        updated_data = updatefile.update_reply_by_phone(filename,file_path, phone_number,new_data)
        return(updated_data)
    except Exception as e:
         raise e

async def read_appointment_file(file_path):
    try:
        reportfile = GGHNReadReport()
        filecontent = reportfile.gghn_read_appointment_file(file_path)
        return(filecontent)
    except Exception as e:
         raise e
    
async def readfile_summary(file_path,filename):
    try:
        reportfile = GGHNReadReport()
        filesummary = reportfile.gghn_read_appointment_summary(file_path,filename)
        return(filesummary)
    except Exception as e:
         raise e
   