# ############gghn############
import json
import os
import shutil
import boto3
from fastapi import File, HTTPException, Request, UploadFile
import httpx
from app.common.appointment_api.appointment_utils import form_file_name, get_client_name
from app.common.reancare_api.reancare_login_service import ReanCareLogin
from app.common.utils import format_date_, format_phone_number, get_temp_filepath, is_date_valid
from app.services.appointment_service.gghn_service.gghn_app_reminder_service import GGHNAppointmentReminder
from app.services.appointment_service.gghn_service.gghn_login_local_service import GGHNLogin
from app.services.appointment_service.gmu_service.gmu_admin_notification_service import GMUAdminNotification
from app.services.appointment_service.gmu_service.gmu_app_reminder_service import GMUAppointmentReminder
from app.services.appointment_service.gmu_service.gmu_pdf_reader_service import GMUPdfReader
from app.services.common_service.read_report import ReadReport
from app.services.common_service.recent_file_service import RecentFile
from app.services.common_service.update_reply_service import UpdateReply


  
#####################gmu########
async def handle_aws(message: Request,storage_service):
    try:
        message_data = await message.json()
        subscription_confirmation = 'Type' in message_data and message_data['Type'] == 'SubscriptionConfirmation'
        if subscription_confirmation:
            return await handle_subscription_confirmation(message_data)
        else:
            print('handling s3 event')
            return await handle_s3_event(message,storage_service)
    except KeyError:
            raise HTTPException(status_code=400, detail='Unable to handle SNS notification')

async def handle_subscription_confirmation(message_data):
    token = message_data['Token']
    topic_arn = message_data['TopicArn']
    subscribe_url = message_data['SubscribeURL']
        # Confirm the subscription by sending a GET request to the SubscribeURL
    async with httpx.AsyncClient() as client:
        response = await client.get(subscribe_url)
    if response.status_code == 200:
            # Subscription confirmed successfully
        return {
                'Token': token,
                'TopicArn': topic_arn,
                'Message': 'SubscriptionConfirmed'
            }
    else:
            # Subscription confirmation failed
        raise HTTPException(status_code=400, detail='Subscription confirmation failed')

async def handle_s3_event(message: Request,storage_service):

    file_path = await download(message)

    # 1. Login as tenant-admin or tenant-user
    # login = ReanCareLogin()
    # await login.login()

    # 2. Extract the date from the PDF file
    reader = GMUPdfReader()
    reminder_date = await reader.extract_reminder_date(file_path)
    if not reminder_date:
        return ('Unable to find or unable to parse the date')

    # Compare file date with the todays date
    is_valid_date = await is_date_valid(reminder_date); 
    # 3. Extract the PDF file
    if is_valid_date:
        print('Extracting pdf data')
        appointments = await reader.extract_appointments_from_pdf(file_path,storage_service)

        # 4. Send one-time-reminders
        reminder = GMUAppointmentReminder()
        await reminder.create_reminder(reminder_date, appointments,storage_service)
        reminder_summary = await reminder.summary()

        
        admin_notification = GMUAdminNotification()
        await admin_notification.admin_notify(reminder_date,reminder_summary)

        return {
            "message" : "Reminders created successfully",
            "summary" : reminder_summary,
        }
    return {
        "message" : "Can not process appointment pdf with previous dates",
        "summary" : None
    }
async def download(message: Request):
    webhook_data = await message.json()
    s3_event_notification = json.loads(webhook_data['Message'])
    s3_records = s3_event_notification['Records']
    for record in s3_records:
        event_name = record['eventName']
        s3_bucket = record['s3']['bucket']['name']
        s3_object_key = record['s3']['object']['key']
        # print("s3_object_key",s3_object_key)
        # Download the PDF file from AWS S3
    local_file_path = await download_pdf_from_s3(s3_bucket, s3_object_key)
    if local_file_path == None:
        raise HTTPException(status_code=400, detail='Unable to download PDF from S3')
    return local_file_path

async def download_pdf_from_s3(bucket_name, object_key):
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=str(os.getenv("AWS_ACCESS_KEY")),
            aws_secret_access_key=str(os.getenv("AWS_SECRET_ACCESS_KEY"))
        )
        s3_object = object_key.split('/')
     
        s3_file = s3_object[1]
        print("s3_file",s3_file)
        local_file_path = get_temp_filepath(s3_file)
       
        s3.download_file(bucket_name, object_key, local_file_path)
        return local_file_path
    except Exception as e:
        print("exception",e)
        return None

############################gmu_test################
async def handle(storage_service,file: UploadFile = File(...)):

    file_path = await store_uploaded_file(file)

    # 1. Login as tenant-admin or tenant-user
    # login = ReanCareLogin()
    # await login.login()

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
        appointments = await reader.extract_appointments_from_pdf(file_path,storage_service)
        
        # 4. Send one-time-reminders
        reminder = GMUAppointmentReminder()
        # reminder_date = '2023-11-08'
        await reminder.create_reminder(reminder_date, appointments,storage_service)
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
###########################other routes#######################################
async def readfile_content(date, storage_service):
    try:
        in_date = date
        date_str =  await format_date_(in_date)
        if(date_str == 'None'):
            print("date returned null")              
        print("formated_date...",date_str)
        
        patientextraction = GGHNAppointmentReminder()
        appointmentcontent = await patientextraction.read_content(date_str,storage_service)
        print(appointmentcontent)
        # return()
    except Exception as e:
        raise e
    
    
async def update_reply_by_ph(client_bot_name,date_str, phone_number, content,storage_service):
    try:
        in_date = date_str
        client_name = await get_client_name(client_bot_name)
        client = (client_name).lower()
        print("client name--",client)
        date_str = await format_date_(in_date)
        if(date_str == 'None'):
            print("date returned null")
        
        print("formated_date...",date_str)
        number = await format_phone_number(phone_number)
        if(number == 'None'):
            print("number returned null")
        filename = await form_file_name(client,date_str)
        if(filename == 'None'):
            print("filename returned null")
        updatefile = UpdateReply()
        updated_data = await updatefile.update_reply_by_phone(filename, number, content,storage_service)
        return(updated_data)
    except Exception as e:
         raise e


async def recent_file(file_prefix,storage_service):
    fileprefix = file_prefix
    print(f"fileprefix {fileprefix}")
    recentfile = RecentFile()
    filename = await recentfile.find_recent_file(fileprefix,storage_service)   
    return filename


async def read_appointment_file(filename,storage_service):
    try:
        reportfile = ReadReport()
        filecontent = await reportfile.read_appointment_file(filename,storage_service)
        return(filecontent)
    except Exception as e:
         raise e

async def readfile_content_by_phone(client_bot_name, phone_number,date_string,storage_service):
    try:    
        client_name = await get_client_name(client_bot_name)
        client = (client_name).lower()
        date_str = await format_date_(date_string)
        if(date_str == 'None'):
            print("date returned null")
        number = await format_phone_number(phone_number)
        if(number == 'None'):
            print("number returned null")
        filename = await form_file_name(client,date_str)
        if(filename == 'None'):
            print("filename returned null")
        reportfile = ReadReport()
        filecontent = await reportfile.readfile_content_by_ph(filename,number,storage_service)
        return(filecontent)
    except Exception as e:
        raise e


async def readfile_summary(filename,storage_service):
    try:
        reportfile = ReadReport()
        filesummary = await reportfile.read_appointment_summary(filename,storage_service)
        return(filesummary)
    except Exception as e:
         raise e


