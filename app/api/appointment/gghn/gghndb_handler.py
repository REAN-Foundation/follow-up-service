

from fastapi import APIRouter, HTTPException, Request
import boto3
from app.common.appointment.gghn_login_local_service import GGHNLogin
from app.common.reancareapi.rc_login_service import RCLogin
from app.services.appointment_service.gghn_service.gghn_app_reminder_service import GGHNAppointmentReminder
from app.services.appointment_service.gghn_service.gghn_read_report import GGHNReadReport
from app.services.common_service.recent_file_service import RecentFile
from app.services.common_service.update_reply_service import UpdateReply

async def readfile_content(date, storage_service):
    try:
        print (date)
        login = GGHNLogin()
        await login.gghnlogin()
        login = RCLogin()
        await login.login()
        patientextraction = GGHNAppointmentReminder()
        appointmentcontent = await patientextraction.read_content(date,storage_service)
        return(appointmentcontent)
        # return()
    except Exception as e:
         raise e
    
async def update_gghn_reply_by_ph(filename,phone_number, new_data,storage_service):
    try:
        updatefile =  UpdateReply()
        updated_data = await updatefile.update_reply_by_phone(filename,phone_number,new_data,storage_service)
        return(updated_data)
    except Exception as e:
         raise e

async def read_appointment_file(filename,storage_service):
    try:
        reportfile = GGHNReadReport()
        filecontent = await reportfile.gghn_read_appointment_file(filename,storage_service)
        return(filecontent)
    except Exception as e:
         raise e
    
async def readfile_summary(filename,storage_service):
    try:
        reportfile = GGHNReadReport()
        filesummary = await reportfile.gghn_read_appointment_summary(filename,storage_service)
        return(filesummary)
    except Exception as e:
         raise e
   
async def recent_file(file_prefix,storage_service):
    fileprefix = file_prefix
    print(f"fileprefix {fileprefix}")
    recentfile = RecentFile()
    filename = await recentfile.find_recent_file(fileprefix,storage_service)   
    return filename