
import json
import os

import requests
from app.common.appointment.appointment_utils import isPatientAlreadyReplied, time_of_first_reminder
from app.common.cache import cache
from app.common.exceptions import HTTPError, NotFound
from app.common.reancareapi.reancareapi_utils import find_patient_by_mobile, get_headers
from app.common.utils import get_temp_filepath, open_file_in_readmode
class ExtractPatientCode:
    def __init__(self):
        summary_data=[]
        reancare_base_url = os.getenv("REANCARE_BASE_URL")
        self.reminder_url = str(reancare_base_url + "/reminders/one-time")
        self.search_by_emrid = str(reancare_base_url + "/patients/search")
        self.patient_code_count = 0
        self.reminders_sent_count = 0
        self.appointment_details= []

        gghn_base_url = os.getenv("GGHN_BASE_URL")
        if gghn_base_url == None:
            raise Exception('GGHN_BASE_URL is not set')
        
        self.patient_code_url = str(gghn_base_url + "/api/PharmacyPickup")
        self.token = cache.get('gghn_access_token')
        print("gghn token----",self.token)

    #Get Paitient details using gghn api   
    def read_content(self, date):
        try:
            self.token = cache.get('gghn_access_token')
            suburl = str(f'/QueryPatientByNextAppointment?startdate={date}T00:00:00&endDate={date}T23:59:59')
            url=str(self.patient_code_url+suburl)
            print("Patient code url----",url)
       
            headers = {
            'Authorization': "Bearer " + self.token,
            # 'Content-Type': 'application/json'
            }
            try:
                response = requests.post(url,headers = headers)
                result = response.json()
            except HTTPError as e:
                print(f"HTTP Error {e.status_code}: {e.message}")

            print("result of post---",result)
            prefix="gghn_details_"
            file_name = self.create_data_file(result,date,prefix)
            appointment_file = self.extract_appointment(file_name,date)
            # appointment_file = "add example phone numer file here"
            updated_appointment_file = self.update_phone_by_EMRId(appointment_file,date)
            resp = self.send_reminder(updated_appointment_file,date)
            
            return(resp)
        except HTTPError:
            raise NotFound(status_code=404, detail="Resource not found")

    #Create/update a detail file of api out put 
    def create_data_file(self,resp_data,enquiry_date,prefix):
        filename=str(prefix+enquiry_date+'.json')
        f_path=(os.getcwd()+"/temp/"+filename)
        if os.path.exists(f_path):
            print(f"The file {filename} already exists!")
            if(prefix=='gghn_details_'):
                self.update_content(filename,resp_data,enquiry_date,prefix)
            else:
                self.update_appointment_content(filename,resp_data,enquiry_date,prefix)
                # with open(f_path, 'w') as json_file:
                #          json.dump(resp_data, json_file, indent=25)
                # return(filename)
        else: 
            temp_folder = os.path.join(os.getcwd(), "temp")
            if not os.path.exists(temp_folder):
                os.mkdir(temp_folder)
            filepresent  = os.path.join(temp_folder, filename)
            with open(filepresent, 'w') as json_file:
                json.dump(resp_data, json_file, indent=25)
        return(filename)        
      
    #Create a file with only necessary details for appointment    
    def extract_appointment(self, file_name,date):

        filepath = get_temp_filepath(file_name)
        if not os.path.exists(filepath):
            raise Exception(file_name + " does not exist.")

        file=open(filepath,"r")
        file_content=file.read()
        appointment_data=json.loads(file_content)
        appointment_details= []
        for data in appointment_data:
            patient_code_details={
                "Facilityname":data['facilityname'],
                "Next_appointment_date":data['next_appointment_date'],
                "Participant_code":data['participant_code'],
                "Phone_number":"",
                "WhatsApp_message_id": "",
                "Patient_replied":"Not replied"
            }
            appointment_details.append(patient_code_details)
            self.patient_code_count= self.patient_code_count+1
        print("patient_code_count",self.patient_code_count)
        # print("appointments-----",appointment_details)  
        prefix = "gghn_appointment_"  
        file_name = self.create_data_file(appointment_details,date,prefix)
        return(file_name)
      
    def update_content(self,filename,resp_data,enquiry_date,prefix):
        additional_data=[]
        file_data = open_file_in_readmode(filename)
        if(file_data == None):
            print(f"An unexpected error occurred while reading file{filename}")
        # print("file data...",file_data)
        # print("resp_data...",resp_data)
        flag=0
        for rdata in resp_data:
            flag=0
            for fdata in file_data:
                if rdata['participant_code'] == fdata['participant_code']:
                    flag=1
                # print("value of flag",flag)  
            if flag==0:
                additional_paitient={
                                 "state": rdata['state'],
                                 "facilityname": rdata['facilityname'],
                                 "sex": rdata['sex'],
                                 "age":rdata['age'],
                                 "art_start_date": rdata['art_start_date'],
                                 "last_pickup_date": rdata['last_pickup_date'],
                                 "months_of_arv_refill": rdata['months_of_arv_refill'],
                                 "next_appointment_date":rdata['next_appointment_date'],
                                 "current_art_regimen": rdata['current_art_regimen'],
                                 "clinical_staging_at_last_visit": rdata['clinical_staging_at_last_visit'],
                                 "last_cd4_count": rdata['last_cd4_count'],
                                 "current_viral_load":rdata['current_viral_load'],
                                 "viral_load_status": rdata['viral_load_status'],
                                 "current_art_status": rdata['current_art_status'],
                                 "outcome_of_last_tb_screening":rdata['outcome_of_last_tb_screening'],
                                 "date_started_on_tb_treatment":rdata['date_started_on_tb_treatment'],
                                 "tb_treatment_type":rdata['tb_treatment_type'],
                                 "tb_treatment_completion_date": rdata['tb_treatment_completion_date'],
                                 "tb_treatment_outcome":rdata['tb_treatment_outcome'],
                                 "date_of_commencement_of_eac":rdata['date_of_commencement_of_eac'],
                                 "number_of_eac_sessions_completed": rdata['number_of_eac_sessions_completed'],
                                 "result_of_cervical_cancer_screening": rdata['result_of_cervical_cancer_screening'],
                                 "fingerprint_captured":rdata['fingerprint_captured'],
                                 "fingerprint_recaptured":rdata['fingerprint_recaptured'], 
                                 "participant_code":rdata['participant_code']
                                 }
                # print(type(additional_paitient))
                # print(type(additional_data))
                additional_data.append(additional_paitient)
           
        print("additional paitients are",additional_data)
        print(type(file_data))
        length_of_list = len(additional_data)
        print("Length of the additional_data:", length_of_list)
        file_data.extend(additional_data)
        try:
            filepath = get_temp_filepath(filename)
            with open(filepath, 'w') as json_file:
                json.dump(file_data, json_file, indent=25)
            return(filename)
        except Exception as e:
        # Handle other exceptions
            print(f"An unexpected error occurred while writing into file{filename}: {e}")

    def update_appointment_content(self,filename,resp_data,enquiry_date,prefix):
        additional_appointment=[]
        file_data = open_file_in_readmode(filename)
        if(file_data == None):
            print(f"An unexpected error occurred while reading file {filename}")
        # print("file data...",file_data)
        # print("resp_data...",resp_data)
        flag=0
        for rdata in resp_data:
            flag=0
            for fdata in file_data:
                if rdata['Participant_code'] == fdata['Participant_code']:
                    flag=1
                # print("value of flag",flag)  
            if flag==0:
                additional_app={
                                "Facilityname": rdata['Facilityname'],
                                "Next_appointment_date":rdata['Next_appointment_date'],
                                "Participant_code":rdata['Participant_code'],
                                "Phone_number": "",
                                "WhatsApp_message_id": "",
                                "Patient_replied": "Not replied",
                                }
                # print(type(additional_paitient))
                # print(type(additional_data))
                additional_appointment.append(additional_app)
           
        print("additional paitients are",additional_appointment)
        print(type(file_data))
        length_of_list = len(additional_appointment)
        print("Length of the additional_appointment:", length_of_list)
        file_data.extend(additional_appointment)
        try:
            filepath = get_temp_filepath(filename)
            with open(filepath, 'w') as json_file:
                json.dump(file_data, json_file, indent=25)
            return(filename)
        except Exception as e:
        # Handle other exceptions
            print(f"An unexpected error occurred while writing into file{filename}: {e}")


    def send_reminder(self,appointment_file,date):
        count = 0
        filedata = open_file_in_readmode(appointment_file) 
        if(filedata == None):
            print(f"An unexpected error occurred while reading file{appointment_file}")
        for item in filedata:
            try:
                phone_number = item['Phone_number']
                patient_code = item['Participant_code']
                print("GGHN patient phone number is:",phone_number)
                patient_data = find_patient_by_mobile(phone_number)
                print("GGHN patient user id is:",patient_data)
                if(patient_data == None):
                    print(f"An error occurred while searching a patient")
                first_reminder = time_of_first_reminder(phone_number)
                if(first_reminder != None):
                    print("first reminder time for GGHN patient",first_reminder)
                    prefix_str = 'gghn_appointment_'
                    #for trial date made static
                    # date = '2024-05-2'
                    already_replied = isPatientAlreadyReplied(prefix_str, phone_number, date)
                    if not already_replied:
                        schedule_model = self.get_schedule_create_model(patient_data,patient_code,first_reminder,date)
                        response = self.schedule_reminder(schedule_model)
                        print("reminder response",response)
                        count = response
                    else:
                        print(f"patient with {phone_number}has already replied hence reminder not sent!")
                else:
                    print("No phone number found to set remnder")
            except Exception as e:
                print(f"an error occured: {e}")
        return{'reminders_sent_count':count}
             
            

    def get_schedule_create_model(self, patient_user_id,patient_code, reminder_time, when_date):
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
            "ClientName": "REAN_BOT",
            "AppointmentDate": when_date
        }

        return {
            'UserId': patient_user_id,
            # 'Name': 'Hey {}, you have an appointment schedule at {} with {}'.format(patient_name, patient['AppointmentTime'], patient['Provider']),
            'Name': 'appointment reminder',
            'WhenDate': when_date,
            'WhenTime': '18:00:00',
            'NotificationType': 'WhatsApp',
            'RawContent':json.dumps(raw_content)
        }

    def schedule_reminder(self, schedule_create_model):
        header = get_headers()
        response = requests.post(self.reminder_url, headers=header, data=json.dumps(schedule_create_model))
        if response.status_code == 201:
            self.reminders_sent_count = self.reminders_sent_count + 1
        else:
            print('Unable to schedule reminder ', response.json())  
        return(self.reminders_sent_count)
          

    def update_phone_by_EMRId(self, file_name, date):
        recent_data=[]
        filepath = get_temp_filepath(file_name)
        if not os.path.exists(filepath):
            raise Exception(file_name + " does not exist.")

        file=open(filepath,"r")
        file_content=file.read()
        appointment_data=json.loads(file_content)
        print("appointment file data",appointment_data)
        for app_data in appointment_data:
            EMRId=app_data['Participant_code']
            phone_nos = self.search_phone_by_EMRId(file_name, date, EMRId)
            if(phone_nos != None):
                app_data['Phone_number'] = phone_nos
            else:
                app_data['Phone_number'] = ''

        with open(filepath, 'w') as file:
            json.dump(appointment_data, file, indent=6)
        
        with open(filepath, 'r') as file:
            retrived_data = json.load(file)

        return(file_name)

            
    def search_phone_by_EMRId(self, file_name, date, EMRId):
        print("search url",self.search_by_emrid)
        header = get_headers()
        print("header",header)
        params = {
        'externalMedicalRegistrationId': EMRId
        }
        response = requests.get(self.search_by_emrid, headers = header, params=params)
        result = response.json()
        if response.status_code == 200 and not result['Message'] == 'No records found!':
            phone_no_retrived = str(result['Data']['Patients']['Items'][0]['Phone'])
            print(f"phone retrived for {EMRId} is {phone_no_retrived}")
            return (phone_no_retrived)
        else:
            # print(result['Message'])
             return(None)