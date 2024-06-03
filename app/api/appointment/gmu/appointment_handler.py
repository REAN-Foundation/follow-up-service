from fastapi import APIRouter, HTTPException, Request
import boto3
import httpx
from app.common.utils import get_temp_filepath
from app.common.utils import is_date_valid
from app.services.appointment_service.common_service.recent_file_service import RecentFile
from app.services.appointment_service.common_service.update_AFReport_service import UpdateFile
from app.services.appointment_service.common_service.login_service import UserLogin
from app.services.appointment_service.gmu_service.pdf_reader_service import PdfReader
from app.services.appointment_service.gmu_service.reminder_service import Reminder
from app.services.appointment_service.gmu_service.notification_service import AdminNotification
import json
import os

from app.services.appointment_service.gmu_service.read_report import ReadReport


###############################################################################

async def handle(message: Request):
    try:
        message_data = await message.json()
        subscription_confirmation = 'Type' in message_data and message_data['Type'] == 'SubscriptionConfirmation'
        if subscription_confirmation:
            return await handle_subscription_confirmation(message_data)
        else:
            print('handling s3 event')
            return await handle_s3_event(message)
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

async def handle_s3_event(message: Request):

    file_path = await download(message)

    # 1. Login as tenant-admin or tenant-user
    login = UserLogin()
    await login.login()

    # 2. Extract the date from the PDF file
    reader = PdfReader()
    reminder_date = await reader.extract_reminder_date(file_path)
    if not reminder_date:
        return ('Unable to find or unable to parse the date')

    # Compare file date with the todays date
    is_valid_date = await is_date_valid(reminder_date); 
    # 3. Extract the PDF file
    if is_valid_date:
        print('Extracting pdf data')
        appointments = await reader.extract_appointments_from_pdf(file_path)

        # 4. Send one-time-reminders
        reminder = Reminder()
        await reminder.create_one_time_reminders(reminder_date, appointments)
        reminder_summary = await reminder.summary()

        
        admin_notification = AdminNotification()
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
        local_file_path = await get_temp_filepath(object_key)
        s3.download_file(bucket_name, object_key, local_file_path)
        return local_file_path
    except Exception as e:
        return None

#Other routes of file handling

async def read_appointment_file(filename):
    try:
        reportfile = ReadReport()
        filecontent = await reportfile.read_appointment_file(filename)
        return(filecontent)
    except Exception as e:
         raise e

async def readfile_content_by_phone(filename,phone_number):
    try:
        reportfile = ReadReport()
        filecontent = await reportfile.readfile_content_by_ph(filename, phone_number)
        return(filecontent)
    except Exception as e:
         raise e


async def readfile_summary(filename):
    try:
        reportfile = ReadReport()
        filesummary = await reportfile.read_appointment_summary(filename)
        return(filesummary)
    except Exception as e:
         raise e

async def update_reply_by_ph(filename, phone_number, new_data):
    try:
        updatefile = UpdateFile()
        updated_data = await updatefile.update_reply_by_phone(filename, phone_number,new_data)
        return(updated_data)
    except Exception as e:
         raise e

async def recent_file(file_prefix):
    recentfile = RecentFile()
    filename = await recentfile.find_recent_file(file_prefix)   
    return filename