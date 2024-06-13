from fastapi import APIRouter, HTTPException, Request
import boto3
# from app.common.utils import get_temp_filepath
from app.services.appointment_local_service.common_local_service.update_reply_local_service import UpdateReply
from app.common.appointment.gghn_login_local_service import GGHNLogin
from app.services.appointment_local_service.gghn_local_service.gghn_app_reminder_local_service import  GGHNAppointmentReminder
from app.services.appointment_local_service.common_local_service.recent_file_local_service import RecentFile
from app.services.appointment_local_service.gghn_local_service.gghn_read_report_local_service import GGHNReadReport
from app.common.reancareapi.rc_login_service import RCLogin


async def readfile_content(date):
    try:
        print (date)
        login = GGHNLogin()
        await login.gghnlogin()
        login = RCLogin()
        await login.login()
        patientextraction = GGHNAppointmentReminder()
        appointmentcontent = await patientextraction.read_content(date)
        return(appointmentcontent)
        # return()
    except Exception as e:
         raise e
    
async def update_gghn_reply_by_ph(filename,phone_number, new_data):
    try:
        
        updatefile =  UpdateReply()
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