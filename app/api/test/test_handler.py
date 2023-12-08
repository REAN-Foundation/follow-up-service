import shutil
from fastapi import File, UploadFile
from app.services.login_service import UserLogin
from app.services.pdf_reader_service import PdfReader
from app.services.reminder_service import Reminder
from app.services.notification_service import AdminNotification
import os
from app.services.read_report import ReadReport
from  app.services.update_service import UpdateFile
###############################################################################

async def handle(file: UploadFile = File(...)):

    file_path = store_uploaded_file(file)

    # 1. Login as tenant-admin or tenant-user
    login = UserLogin()
    login.login()

    # 2. Extract the date from the PDF file
    reader = PdfReader()
    reminder_date = reader.extract_reminder_date(file_path)
    if not reminder_date:
        return ('Unable to find or unable to parse the date')

    # 3. Extract the PDF file
    appointments = reader.extract_appointments_from_pdf(file_path)

    # 4. Send one-time-reminders
    reminder = Reminder()
    # reminder_date = '2023-11-08'
    reminder.create_one_time_reminders(reminder_date, appointments)
    reminder_summary = reminder.summary()

    admin_notification = AdminNotification()
    admin_notification.admin_notify(reminder_date,reminder_summary)

    return {
        "Message" : "Reminders created successfully",
        "Data" : reminder_summary,
    }

def store_uploaded_file(file: UploadFile):
    current_path = os.getcwd()
    folder_path = os.path.join(current_path, "../", "temp")
    exists = os.path.exists(folder_path)
    if not exists:
        os.mkdir(folder_path)
    file_path = os.path.join(folder_path, file.filename)
    # print(file_path)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return file_path

async def readfile(file_path):
    reportfile = ReadReport()
    filecontent = reportfile.read_report_file(file_path)
    return(filecontent)

async def readfile_summary(file_path,filename):
    reportfile = ReadReport()
    filesummary = reportfile.read_report_summary(file_path,filename)
    return(filesummary)

async def updatefile(file_path, patient_userid, new_data):
    updatefile = UpdateFile()
    updated_data = updatefile.update_content_by_id(file_path, patient_userid, new_data)
    return(updated_data)

async def update_whatsappid(file_path, phone_number, new_data):
    updatefile = UpdateFile()
    updated_data = updatefile.update_whatsapp_by_ph(file_path, phone_number,new_data)
    return(updated_data)

async def update_reply_by_ph(file_path, phone_number, new_data):
    updatefile = UpdateFile()
    updated_data = updatefile.update_reply_by_phone(file_path, phone_number,new_data)
    return(updated_data)

