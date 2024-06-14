import shutil
from fastapi import File, UploadFile
from app.common.reancareapi.rc_login_service import RCLogin
from app.common.utils import is_date_valid
from app.services.appointment_service.gghn_service.gghn_read_report import GGHNReadReport
from app.services.appointment_service.gmu_service.gmu_pdf_reader_service import GMUPdfReader
from app.services.appointment_service.gmu_service.gmu_app_reminder_service import GMUAppointmentReminder
from app.services.appointment_service.gmu_service.gmu_admin_notification_service import GMUAdminNotification
import os
from app.services.appointment_service.gmu_service.gmu_read_report import GMUReadReport
from app.services.common_service.recent_file_service import RecentFile
from app.services.common_service.update_reply_service import UpdateReply
###############################################################################

async def handle(file: UploadFile = File(...)):

    file_path = await store_uploaded_file(file)

    # 1. Login as tenant-admin or tenant-user
    login = RCLogin()
    await login.login()

    # 2. Extract the date from the PDF file
    reader = GMUPdfReader()
    reminder_date = await reader.extract_reminder_date(file_path)
    if not reminder_date:
        return ('Unable to find or unable to parse the date')
    # Compare file date with the todays date
    is_valid_date = await is_date_valid(reminder_date); 
    # 3. Extract the PDF file
    if is_valid_date:
        # 3. Extract the PDF file
        appointments = await reader.extract_appointments_from_pdf(file_path)
        
        # 4. Send one-time-reminders
        reminder = GMUAppointmentReminder()
        # reminder_date = '2023-11-08'
        await reminder.create_reminder(reminder_date, appointments)
        reminder_summary = await reminder.summary()

        admin_notification = GMUAdminNotification()
        await admin_notification.admin_notify(reminder_date,reminder_summary)

        return {
            "Message" : "Reminders created successfully",
            "Data" : reminder_summary,
        }

    return {
            "Message" : "Can not process appontment pdf with previous dates",
            "Data": None 
        }
async def store_uploaded_file(file: UploadFile):
    current_path = os.getcwd()
    folder_path = os.path.join(current_path, "temp")
    exists = os.path.exists(folder_path)
    if not exists:
        os.mkdir(folder_path)
    file_path = os.path.join(folder_path, file.filename)
    # print(file_path)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return file_path

async def read_appointment_file(filename):
    try:
        reportfile = GMUReadReport()
        filecontent = await reportfile.read_appointment_file(filename)
        return(filecontent)
    except Exception as e:
         raise e

async def readfile_content_by_phone(filename,phone_number):
    try:
        reportfile = GMUReadReport()
        filecontent = await reportfile.readfile_content_by_ph(filename, phone_number)
        return(filecontent)
    except Exception as e:
         raise e


async def readfile_summary(filename):
    try:
        reportfile = GMUReadReport()
        filesummary = await reportfile.read_appointment_summary(filename)
        return(filesummary)
    except Exception as e:
         raise e

async def update_reply_by_ph(filename, phone_number, new_data):
    try:
        updatefile = UpdateReply()
        updated_data = await updatefile.update_reply_by_phone(filename, phone_number,new_data)
        return(updated_data)
    except Exception as e:
         raise e

async def recent_file(file_prefix):
    recentfile = RecentFile()
    filename = await recentfile.find_recent_file(file_prefix)   
    return filename