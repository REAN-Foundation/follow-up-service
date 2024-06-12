from datetime import *
from ast import Dict
import json
import os
import requests
import urllib.parse
from app.common.appointment.appointment_utils import has_patient_replied_infile, time_of_first_reminder, valid_appointment_status, validate_mobile
from app.common.enumclasses import AppStatusEnum, PatientReplyEnum
from app.common.reancareapi.reancareapi_utils import find_patient_by_mobile, get_headers
from app.common.utils import  get_temp_filepath
from app.common.cache import cache
import pytz

from app.interfaces.appointment_reminder_interface import AppointmentReminderI
from app.services.appointment_local_service.common_local_service.file_service import FileStorageService

###############################################################

PENDING_ARRIVAL = 'Pending arrival'

###############################################################

class GMUAppointmentReminder(AppointmentReminderI):
    def __init__(self):

        reancare_base_url = os.getenv("REANCARE_BASE_URL")
        if reancare_base_url == None:
            raise Exception('REANCARE_BASE_URL is not set')
        tenant_id = os.getenv("TENANT_ID")

        self.patient_url = str(reancare_base_url + "/patients/")
        self.reminder_url = str(reancare_base_url + "/reminders/one-time")
        self.reminder_search_url = str(reancare_base_url + "/reminders/search")
        self.api_key = os.getenv("REANCARE_API_KEY")
        self.access_token = cache.get('access_token')
        self.recent_file = ''
        self.tenant_id = tenant_id

        self.new_patients_added_count = 0
        self.reminders_sent_count = 0
        self.pending_arrival_count = 0
        self.appointments_processed_count = 0
        self.appointments_skipped_count = 0
        self.file_storage = FileStorageService()

    async def create_reminder(self, reminder_date, appointments):

        self.access_token = cache.get('access_token')
        summary_data = []
        for appointment in appointments:

            patient_mobile_number = appointment['PatientMobile']
            is_valid_mobile = validate_mobile(patient_mobile_number)
            if not is_valid_mobile:
                print('*Invalid phone-number - ', patient_mobile_number)
                self.appointments_skipped_count = self.appointments_skipped_count + 1
                continue

            self.appointments_processed_count = self.appointments_processed_count + 1

            user_id = await find_patient_by_mobile(patient_mobile_number)
            user_model = await self.get_update_patient_model(appointment)
            appointment_time = await self.get_time_in_24hrs(appointment)
            first_time = appointment_time['FirstTime']
            second_time = appointment_time['SecondTime']
            first_name = user_model['FirstName']
            last_name = user_model['LastName']

            # Create patient if does not exist
            if user_id == None:
                user_id = await self.create_patient(patient_mobile_number)
                if user_id == None:
                    raise Exception('Unable to create patient')
                self.new_patients_added_count = self.new_patients_added_count  + 1
                await self.update_patient(user_id, user_model)

            data = {
                "Name_of_patient":appointment['PatientName'],
                "Rean_patient_userid":user_id,
                "Phone_number":patient_mobile_number,
                "Appointment_time":appointment['AppointmentTime'],
                "Patient_status":valid_appointment_status(appointment['Status']),
                "WhatsApp_message_id":"",
                "Patient_replied": "N/A" if valid_appointment_status(appointment['Status'])!=AppStatusEnum.Pending_Arrival else "Not replied",
                  }
            summary_data.append(data)

            if appointment['Status'] != PENDING_ARRIVAL:
               continue

            self.pending_arrival_count = self.pending_arrival_count + 1

            # First reminder set as soon as pdf upload
            print(f'patient phone number {patient_mobile_number}')
            first_reminder = await time_of_first_reminder(patient_mobile_number)
            if(first_reminder != None):
                print(f'time of reminder after pdfupload {first_reminder}')
                schedule_model = await self.get_schedule_create_model(user_id, first_name, appointment,first_reminder, reminder_date)
                
                # Check the patient replied status
                prefix_string = 'gmu_followup_file_'
                already_replied = await has_patient_replied_infile(prefix_string, patient_mobile_number, reminder_date)
                # already_replied = self.isPatientAlreadyReplied(patient_mobile_number, reminder_date)
                
                if not already_replied:
                    response = await self.schedule_reminder(schedule_model)

            #  Send reminders 10 min before and after

            # is_reminder_set = self.search_reminder(user_id, reminder_date, first_time)
            # if not is_reminder_set:
            #     schedule_model = self.get_schedule_create_model(user_id, first_name, appointment, first_time, reminder_date)
            #     self.schedule_reminder(schedule_model)
            # is_reminder_set = self.search_reminder(user_id, reminder_date, second_time)
            # if not is_reminder_set:
            #     schedule_model = self.get_schedule_create_model(user_id, first_name, appointment, second_time, reminder_date)
            #     self.schedule_reminder(schedule_model)
            else:
                print("No phone number found to set remnder")
        await self.create_reports(summary_data,reminder_date)

   
    async def create_reports(self,summary_data,reminder_date):
        print('SUMMARY:',summary_data)
        filename=str('gmu_followup_file_'+reminder_date+'.json')
        data = await self.file_storage.search_file(filename)
        if(data != None):
            print(f"The file {filename} already exists. Please choose a different name.")
            json_string = json.dumps(summary_data, indent=7)
            json_object = json.loads(json_string)
            data_replaced = await self.replace_file(json_object,filename)
            content_data = await self.file_storage.update_file(filename, data_replaced,7)
            print(content_data)
            return(content_data)
        else:
            json_string = json.dumps(summary_data, indent=7)
            json_object = json.loads(json_string)
            content_data = await self.file_storage.store_file(filename, json_object,7)
            
            print(content_data)
            return(content_data)

    async def replace_file(self,json_object,filename):
        # with open(f_path, 'r') as file:
        #     data = json.load(file)
        data = await self.file_storage.search_file(filename)
        for item in data:
            if item['Patient_status'] == 'Pending arrival':
               for record in json_object:
                    if record['Phone_number'] == item['Phone_number']:
                       if item['Name_of_patient'] == record['Name_of_patient']:
                           item['Patient_status'] = record['Patient_status']
                        #    item['Patient_replied'] = record['Patient_replied']

        flag = 0
        for item in json_object:
            for record in data:
                if item['Phone_number'] == record['Phone_number']:
                    flag = 1
            if flag != 1:
                data.append(item)
                flag = 0
            flag = 0
      
        return(data)



    async def search_reminder(self, patient_user_id, reminder_date, reminder_time):
        url = self.reminder_search_url
        headers = get_headers()
        params = {
            'userId': patient_user_id,
            'whenDate': reminder_date,
            'whenTime': reminder_time
        }
        # +'?userId={}&whenDate={}&whenTime={}'.format(patient_user_id,reminder_date,reminder_time)
        response = requests.get(url, headers=headers, params=params)
        result = response.json()
        if response.status_code == 200 and not result['Message'] == 'No records found!':
            return True
        else:
            # print(result['Message'])
            return False


    async def create_patient(self, mobile):
        self.url = self.patient_url
        header = get_headers(create_user=True)
        body = json.dumps({'Phone': mobile, 'TenantId': self.tenant_id})
        response = requests.post(self.url, headers = header, data = body)
        result = response.json()
        if not result['HttpCode'] == 201:
            print('Unable to create patient ', result['Message'])
            return None
        else:
            created_patient_info = response.json()
            user_id = created_patient_info['Data']['Patient']['UserId']
            return user_id

    async def get_update_patient_model(self, patient):
        body = {}
        name = patient['PatientName'].split(' ')
        if len(name) == 2:
            body['FirstName'] = name[0]
            body['LastName'] = name[1]
        elif len(name) == 3:
            body['FirstName'] = name[0]
            body['MiddleName'] = name[1]
            body['LastName'] = name[2]
        elif len(name) == 4:
            body['FirstName'] = name[0]
            body['MiddleName'] = name[1] + ' ' + name[2]
            body['LastName'] = name[3]

        if patient['PatientMobile'].startswith('+1'):
            body['CurrentTimeZone'] = '-05:00'
            body['DefaultTimeZone'] = '-05:00'
        return body

    async def update_patient(self, patient_user_id, update_patient_model):
        header = get_headers()
        response = requests.put(self.patient_url+patient_user_id, headers=header, data=json.dumps(update_patient_model))
        if response.status_code != 200:
            raise Exception('Unable to update patient')

    async def get_schedule_create_model(self, patient_user_id, patient_name, patient, reminder_time, when_date):
        appointment_time = patient['AppointmentTime'].split(' ')
        hour, minute = appointment_time[0].split(':')
        rest = appointment_time[1]
        # appointment_time= '{}:{}:{}'.format(hour,minute,'00')
        raw_content = {
            "TemplateName": "appointment_rem_question",
            "Variables": {
                "en": [
                    {
                        "type": "text",
                        "text": patient_name
                    },
                    {
                        "type": "text",
                        "text": "appointment"
                    },
                    {
                        "type": "text",
                        "text":  reminder_time
                    },
                    {
                        "type": "text",
                        "text": "attend"
                    }

                ]
            },
            "ButtonsIds": [
                "Reminder_Reply_Yes",
                "Reminder_Reply_No"
            ],
            # "ClientName": "GMU"
            "ClientName": "REAN_BOT",
            "AppointmentDate": patient['AppointmentTime']
        }

        return {
            'UserId': patient_user_id,
            # 'Name': 'Hey {}, you have an appointment schedule at {} with {}'.format(patient_name, patient['AppointmentTime'], patient['Provider']),
            'Name': 'appointment reminder',
            'WhenDate': when_date,
            'WhenTime': reminder_time,
            'NotificationType': 'WhatsApp',
            'RawContent':json.dumps(raw_content)
        }

    async def schedule_reminder(self, schedule_create_model):
        header = get_headers()
        response = requests.post(self.reminder_url, headers=header, data=json.dumps(schedule_create_model))
        if response.status_code == 201:
            self.reminders_sent_count = self.reminders_sent_count + 1
        else:
            print('Unable to schedule reminder ', response.json())

    async def get_time_in_24hrs(self, i):
        patient_ap_time = i['AppointmentTime']
        ap_time = patient_ap_time.split(' ')
        appointment_time = ap_time[0].split(':')
        rest = appointment_time[1]
        if ap_time[1] == "PM":
            new_app_time = int(appointment_time[0]) + int(12)
            newtime = str(new_app_time)
            if newtime.startswith('24'):
                newtime = '12'
                appointment = (str(newtime)+":"+rest+":00")
                # print("PM",appointment)
                return await self.get_appointment_time(appointment)
            else:
                appointment = (str(newtime)+":"+rest+":00")
                # print("PM",appointment)
                return await self.get_appointment_time(appointment)
        else:
            if appointment_time[0] == "12" or appointment_time[0] == "00":
                new_app_time = '00'
                appointment = (str(new_app_time)+":"+rest+":00")
                return await self.get_appointment_time(appointment)
                # print("AM",appointment)
            else:
                appointment = str(appointment_time[0]+":"+rest+":00")
                # print("AM",appointment)
                return await self.get_appointment_time(appointment)

    async def get_appointment_time(self, time):
        appoint = str(time)
        time_str = appoint
        time_object = datetime.strptime(time_str, '%H:%M:%S').time()
        
        timestr = str(time_object)
        # print(type(timestr))
        t = timestr.split(':')
        hr = int(t[0])
        mn = int(t[1])
        sc = int(t[2])
        # second part
        time_1 = timedelta(hours=hr, minutes=mn, seconds=sc)
        time_2 = timedelta(hours=hr, minutes=mn, seconds=sc)
        delta = timedelta(minutes=10)
        return {'FirstTime': str(time_1 - delta), 'SecondTime': str(time_2 + delta)}
        # print(appoint)
        # print(time_1 - delta)
        # print(time_2 + delta)

    async def summary(self):

        print('Appointments processed : ', self.appointments_processed_count)
        print('Appointments skipped   : ', self.appointments_skipped_count)
        print('Pending arrivals       : ', self.pending_arrival_count)
        print('Newly added patients   : ', self.new_patients_added_count)
        print('Reminders sent         : ', self.reminders_sent_count)

        result = {
            "Appointments processed": self.appointments_processed_count,
            "Appointments skipped"  : self.appointments_skipped_count,
            "Pending arrivals"      : self.pending_arrival_count,
            "Newly added patients"  : self.new_patients_added_count,
            "Reminders sent"        : self.reminders_sent_count,
        }
        return (result)

###############################################################
