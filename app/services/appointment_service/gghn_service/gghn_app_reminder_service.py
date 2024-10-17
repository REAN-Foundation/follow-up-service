import json
import os
import time
import requests
from app.common.appointment_api.appointment_utils import has_patient_replied, time_of_first_reminder
from app.common.cache import cache
from app.common.exceptions import HTTPError, NotFound
from app.common.logtime import log_execution_time
from app.common.reancare_api.reancare_utils import find_patient_by_mobile, get_headers
from app.interfaces.appointment_reminder_interface import AppointmentReminderI
from app.services.appointment_service.gghn_service.gghn_login_local_service import GGHNLogin
from app.services.common_service.db_service import DatabaseService


class GGHNAppointmentReminder(AppointmentReminderI):
    def __init__(self):
        summary_data=[]
        reancare_base_url = os.getenv("REANCARE_BASE_URL")
        self.reminder_url = str(reancare_base_url + "/reminders/one-time")
        self.search_by_emrid = str(reancare_base_url + "/patients/search")
        self.patient_code_count = 0
        self.reminders_sent_count = 0
        self.appointment_details= []
        self.db_data = ''
        self.client_name = os.getenv("DEV_BOT")
        gghn_base_url = os.getenv("GGHN_BASE_URL")
        if gghn_base_url == None:
            raise Exception('GGHN_BASE_URL is not set')
        
        self.patient_code_url = str(gghn_base_url + "/api/PharmacyPickup")
        self.token = ''
    #Get Paitient details using gghn api 
    @log_execution_time
    async def read_content(self, date,storage_service):
        try:
            login = GGHNLogin()
            await login.gghnlogin()
            self.token = cache.get('gghn_access_token')
            # print("gghn token--",self.token)
            suburl = str(f'/QueryPatientByNextAppointment?startdate={date}T00:00:00&endDate={date}T23:59:59')
            url=str(self.patient_code_url+suburl)
            print("Patient code url----",url)
       
            headers = {
            'Authorization': "Bearer " + self.token,
            # 'Content-Type': 'application/json'
            }
            try:
                response = requests.post(url, headers = headers)
                result = response.json()
                if not result:
                    return(None)
            except HTTPError as e:
                print(f"HTTP Error {e.status_code}: {e.message}")

            print("received GGHn data")
            # prefix="gghn_details_"
            # file_name = await self.create_reports(result,date,prefix,storage_service)
            # appointment_file = await self.extract_appointment(file_name,date,storage_service)
            appointment_file = await self.extract_appointment(result,date,storage_service)

            updated_appointment_file = await self.update_phone_by_EMRId(appointment_file,date,storage_service)
            resp = await self.create_reminder(updated_appointment_file,date,storage_service)
            # resp = await self.send_reminder(appointment_file,date) 
            return(resp)
        except HTTPError:
            raise NotFound(status_code=404, detail="Resource not found")

    @log_execution_time
    #Create/update a detail file of api out put 
    async def create_reports(self,resp_data,enquiry_date,prefix,storage_service):
        filename=str(prefix+enquiry_date+'.json')
        response = await storage_service.search_file(filename)
        if response == None:
            await storage_service.store_file(filename,resp_data)
        else:
            print(f"The file {filename} already exists!")
            # if(prefix=='gghn_details_'):
            #    await self.update_content(filename,resp_data,enquiry_date,prefix,storage_service)
            # else:
            await self.update_appointment_content(filename,resp_data,enquiry_date,prefix,storage_service)
            
        return(filename)        
      
    @log_execution_time
    #Create a file with only necessary details for appointment    
    async def extract_appointment(self, result,date,storage_service):
        # response = await storage_service.search_file(file_name)
        # if response == None:
        #     raise Exception(file_name + " does not exist.")
       
        appointment_data = result
        appointment_details= []
        for data in appointment_data:
            patient_code_details={
                "name_of_patient":"",
                "facility_name":data['facilityname'],
                "rean_patient_userid":"",
                "phone_number":"",
                "appointment_time":data['next_appointment_date'],
                "participant_code":data['participant_code'],
                "patient_status":"",
                "whatsapp_message_id": "",
                "patient_replied":"Not replied"
            }
            appointment_details.append(patient_code_details)
            self.patient_code_count= self.patient_code_count+1
        print("patient_code_count",self.patient_code_count)  
        prefix = "gghn_appointment_"  
        file_name = await self.create_reports(appointment_details,date,prefix,storage_service)
        return(file_name)


    
    async def update_appointment_content(self,filename,resp_data,enquiry_date,prefix,storage_service):
        additional_appointment=[]
        file_content = await storage_service.search_file(filename)
        if(file_content == None):
            print(f"An unexpected error occurred while reading {filename}")
        
        file_data = (file_content)     
        # print("file data...",file_data)
        
        flag=0
        for rdata in resp_data:
            flag=0
            for fdata in file_data:
                if rdata['participant_code'] == fdata['participant_code']:
                    flag=1
                # print("value of flag",flag)  
            if flag==0:
                additional_app={
                                "name_of_patient":"",                  
                                "facility_name": rdata['facility_name'],
                                "rean_patient_userid":"",
                                "phone_number": "",
                                "appointment_time":rdata['appointment_time'],
                                "participant_code":rdata['participant_code'],
                                "patient_status":"",
                                "whatsapp_message_id": "",
                                "patient_replied": "Not replied",
                                }
               
                additional_appointment.append(additional_app)
           
        print("additional paitients are",additional_appointment)
        print(type(file_data))
        length_of_list = len(additional_appointment)
        print("Length of the additional_appointment:", length_of_list)
        file_data.extend(additional_appointment)
        
        try:
            await storage_service.update_file(filename,file_data)
            return(filename)
        except Exception as e:
        # Handle other exceptions
            print(f"An unexpected error occurred while writing into{filename}: {e}")

    @log_execution_time
    async def create_reminder(self,appointment_file,date,storage_service):
        count = 0
        filedata = await storage_service.search_file(appointment_file)
        if(filedata == None):
            print(f"An unexpected error occurred while reading{appointment_file}")
        for item in filedata:
            try:
                    phone_number = item['phone_number']
                    patient_code = item['participant_code']
                    # print("GGHN patient phone number is:",phone_number)
                    if(phone_number != ''):
                        patient_data = await find_patient_by_mobile(phone_number)
                        # print("GGHN patient user id is:",patient_data)
                        first_reminder = await time_of_first_reminder(phone_number)
                        print("first reminder time for GGHN patient",first_reminder)
                        prefix_str = 'gghn_appointment_'
                        #for trial date made static
                        # date = '2024-05-2'

                        already_replied = await has_patient_replied(prefix_str, phone_number, date,storage_service)
                        if not already_replied:
                            schedule_model = await self.get_schedule_create_model(patient_data,patient_code,first_reminder,date)
                            response = await self.schedule_reminder(schedule_model)
                            print("reminder response",response)
                            count = response
                        else:
                            print(f"patient with {phone_number}has already replied hence reminder not sent!")
                    else:
                        print("No phone number found to set reminder")
            except Exception as e:
                print(f"an error occured: {e}")
        return{'reminders_sent_count':count}
             

    async def get_schedule_create_model(self, patient_user_id,patient_code, reminder_time, when_date):
        print("when date..",when_date)
        raw_content = {
            "TemplateName": "appointment_rem_question",
            "Variables": {
                "en": [
                    {
                        "type": "text",
                        "text": patient_code
                    },
                    {
                        "type": "text",
                        "text": "appointment"
                    },
                    {
                        "type": "text",
                        "text":  when_date
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
            "ClientName": self.client_name,
            "AppointmentDate": when_date
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
    # As GGHN do not provide when time so the when time is trial testing time

    
    async def schedule_reminder(self, schedule_create_model):
        header = await get_headers()
        response = requests.post(self.reminder_url, headers=header, data=json.dumps(schedule_create_model))
        if response.status_code == 201:
            self.reminders_sent_count = self.reminders_sent_count + 1
        else:
            print('Unable to schedule reminder ', response.json())  
        return(self.reminders_sent_count)
          
    
    # Update phone number in appointment file of GGHN
    async def update_phone_by_EMRId(self, file_name, date,storage_service):
        recent_data=[]
        file_data = await storage_service.search_file(file_name)
        if(file_data == None):
            print(f"An unexpected error occurred in update_phone_by_EMRId while reading {file_name}")
        
        appointment_data = file_data
        # print("appointment file data",appointment_data)
        for app_data in appointment_data:
            EMRId=app_data['participant_code']
            patient_detail = await self.search_phone_by_EMRId(file_name, date, EMRId)
            if(patient_detail != None):
                app_data['phone_number'] = patient_detail['phone']
                app_data['rean_patient_userid'] = patient_detail['userId']
            else:
                app_data['phone_number'] = ''
                app_data['rean_patient_userid'] = ''

        retrived_data = await storage_service.update_file(file_name,appointment_data)
        data = retrived_data
        return(file_name)


    #Search patient phone number from baseservice database corresponding to EMRId 
    
    async def search_phone_by_EMRId(self, file_name, date, EMRId):
        # print("search url",self.search_by_emrid)
        header = await get_headers()
        # print("header",header)
        params = {
        'externalMedicalRegistrationId': EMRId
        }
        url = self.search_by_emrid
        response = requests.get(url, headers = header, params=params)
        result = response.json()
        # print('searched emrid', result)
        if response.status_code == 200 and not result['Message'] == 'No records found!':
            phone_no_retrived = str(result['Data']['Patients']['Items'][0]['Phone'])
            user_id = str(result['Data']['Patients']['Items'][0]['UserId'])
            print(f"phone retrived for {EMRId} is {phone_no_retrived}")
            print(f"userId retrived for {EMRId} is {user_id}")
            patient_data = {
                'phone': phone_no_retrived,
                'userId': user_id
            }
            return (patient_data)
        else:
            # print(result['Message'])
            return(None)