from datetime import *
from ast import Dict
import json
import os
import requests
import urllib.parse
from app.common.appointment_api.appointment_utils import has_patient_replied, time_of_first_reminder, valid_appointment_status, validate_mobile
from app.common.enumclasses import AppStatusEnum, PatientReplyEnum
from app.common.cache import cache
import pytz

from app.common.logtime import log_execution_time
from app.common.reancare_api.reancare_login_service import ReanCareLogin
from app.common.reancare_api.reancare_utils import find_patient_by_mobile, get_headers
from app.interfaces.appointment_reminder_interface import AppointmentReminderI
from app.services.common_service.db_service import DatabaseService


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
        # self.access_token = cache.get('access_token')
        self.recent_file = ''
        self.gmu_bot_client_name = os.getenv("GMU_BOT_CLIENT_NAME")
        self.tenant_id = tenant_id

        self.new_patients_added_count = 0
        self.reminders_sent_count = 0
        self.pending_arrival_count = 0
        self.appointments_processed_count = 0
        self.appointments_skipped_count = 0
        # self.db_data = DatabaseService()
    @log_execution_time
    async def create_reminder(self, reminder_date, appointments,storage_service):
        login = ReanCareLogin()
        self.access_token = await login.get_access_token()
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
                "name_of_patient":appointment['PatientName'],
                "facility_name":"",
                "rean_patient_userid":user_id,
                "phone_number":patient_mobile_number,
                "appointment_time":appointment['AppointmentTime'],
                "participant_code":"",
                "patient_status":valid_appointment_status(appointment['Status']),
                "whatsapp_message_id":"",
                "patient_replied": "N/A" if valid_appointment_status(appointment['Status'])!=AppStatusEnum.Pending_Arrival else "Not replied",
                "followup_assessment_reply":"",
                "case_manager": appointment['Provider'],
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
                prefix_string = 'gmu_appointment_'
                already_replied = await has_patient_replied(prefix_string, patient_mobile_number, reminder_date,storage_service)
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
                     print("Patient have already replied hence no reminder set")
            else:
                print("Patient phone number not set!")
        await self.create_reports(summary_data,reminder_date,storage_service)

    @log_execution_time
    async def create_reports(self,summary_data,reminder_date,storage_service):
        print('SUMMARY:',summary_data)
        filename=str('gmu_appointment_'+reminder_date+'.json')
        data = await storage_service.search_file(filename)
        # f_path=(os.getcwd()+"/temp/"+filename)
        if(data != None):
            print(f"The file {filename} already exists. ")
            json_string = json.dumps(summary_data, indent=7)
            json_object = json.loads(json_string)
            data_replaced = await self.replace_file(json_object,filename,storage_service)
            content_data = await storage_service.update_file(filename, data_replaced)
            # print(content_data)
            return(content_data)
        else:
            json_string = json.dumps(summary_data, indent=7)
            json_object = json.loads(json_string)
            content_data = await storage_service.store_file(filename, json_object)
            # temp_folder = os.path.join(os.getcwd(), "temp")
            # if not os.path.exists(temp_folder):
            #     os.mkdir(temp_folder)
            # filepresent  = os.path.join(temp_folder, filename)
            # with open(filepresent, 'w') as json_file:
            #     json.dump(summary_data, json_file, indent=7)

            # json_string = json.dumps(summary_data, indent=7)

            # code to set recent file in cache
            # self.recent_file = filename
            # cache.set('recent_file', self.recent_file)
            # recent_file = cache.get('recent_file')
            # print("RECENT FILE IN CACHE",recent_file)
            print(content_data)
            return(content_data)

    @log_execution_time
    async def replace_file(self,json_object,filename,storage_service):
        # with open(f_path, 'r') as file:
        data = await storage_service.search_file(filename)
        for item in data:
            if item['patient_status'] == 'Pending arrival':
               for record in json_object:
                    if record['phone_number'] == item['phone_number']:
                       if item['name_of_patient'] == record['name_of_patient']:
                           item['patient_status'] = record['patient_status']
                        #    item['Patient_replied'] = record['Patient_replied']

        flag = 0
        for item in json_object:
            for record in data:
                if item['phone_number'] == record['phone_number']:
                    flag = 1
            if flag != 1:
                data.append(item)
                flag = 0
            flag = 0
  
        return(data)


    @log_execution_time
    async def search_reminder(self, patient_user_id, reminder_date, reminder_time):
        url = self.reminder_search_url
        headers = await get_headers()
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


    @log_execution_time    
    async def create_patient(self, mobile):
        self.url = self.patient_url
        header = await get_headers(create_user=True)
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

    @log_execution_time
    async def update_patient(self, patient_user_id, update_patient_model):
        header = await get_headers()
        response = requests.put(self.patient_url+patient_user_id, headers=header, data=json.dumps(update_patient_model))
        if response.status_code != 200:
            raise Exception('Unable to update patient')

    async def get_schedule_create_model(self, patient_user_id, patient_name, patient, reminder_time, when_date):
        appointment_time = patient['AppointmentTime'].split(' ')
        hour, minute = appointment_time[0].split(':')
        rest = appointment_time[1]
        print("when date..",when_date)
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
            "ClientName": self.gmu_bot_client_name, 
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
    @log_execution_time
    async def schedule_reminder(self, schedule_create_model):
        header = await get_headers()
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
        # print(type(time_object))
        # print(time_object)
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
