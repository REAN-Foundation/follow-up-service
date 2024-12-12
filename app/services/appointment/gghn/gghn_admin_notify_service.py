import os
import json
import shutil
import requests
from difflib import SequenceMatcher
from app.common.appointment_api.appointment_utils import validate_mobile
from app.common.logtime import log_execution_time
from fuzzywuzzy import fuzz
from fuzzywuzzy import process


class GGHNCaseManagerNotification:
    def __init__(self):
      
        bot_url = os.getenv("BOT_URL") 
        self.client = os.getenv("DEV_BOT")
        whatsapp_token = os.getenv("WHATSAPP_TOKEN")
        self.notification_base_url = str(bot_url+"/"+self.client+"/whatsappMeta/"+self.client+"/send")
        if self.notification_base_url == None:
            raise Exception('notification_base_url is not set')
        
        # self.notification_token = "Bearer " + whatsapp_token

    @log_execution_time
    async def case_manager_notify(self,changed_data,date_str):
        print('Sending message to admins')
        flag = 0
        file_name = 'case_manager_contact.json'
        current_path = os.getcwd()
        folder_path = os.path.join(current_path, "assets")
        exists = os.path.exists(folder_path)
        if exists:
            file_path = os.path.join(folder_path,file_name)
            print(file_path)
            file=open(file_path,"r")
            file_content=file.read()
            file_data=json.loads(file_content)
            # cm_file_data = file_data
            if changed_data:
                for data in changed_data:
                    matched_record = self.find_matching_record(data['case_manager'],file_data)
                    print("match..",matched_record)
                    if matched_record == None or matched_record['phone'] == None or matched_record['phone'] == '':
                        print('phone number not found') 
                    else:  
                        admin_phone = (matched_record['phone'])
                        phone_nos=self.reform(admin_phone)
                        print(phone_nos)
                        resp = await self.send_msg_to_case_manager(phone_nos,data,date_str)  
                        print(resp)
               
                    

    async def send_msg_to_case_manager(self,phone_nos,changed_data,date_str):
        # print(changed_data)
        participant_code= changed_data['participant_code']
        date_str= date_str
        facility_name = changed_data['facility_name']
        msg = self.reform_message(changed_data['followup_assessment_reply'])
        header = self.get_notification_headers()
        body ={
            "userId": phone_nos,
            "agentName": "postman",
            "type": "template",
            "templateName": "case_manager_notify",
            "provider": "REAN",
            "message": {
                "Variables": {
                    "en": [
                        {
                            "type": "text",
                            "text": participant_code
                        },
                        {
                            "type": "text",
                            "text": facility_name
                        },
                        {
                            "type": "text",
                            "text": msg
                        }
                    ]
                }
            }
        }
        print("case manager message..",body)
        # return(body)
        response = requests.post(self.notification_base_url, headers=header, data=json.dumps(body))
        if response:
            print(response.json())
            return('Message sent')
        else:
            print('Unable to send message', response.json())

    def get_notification_headers(self): 
        return {    
            # 'Authorization':self.notification_token,
            'Content-Type': 'application/json'
            }
        
    def reform(self,phone):
        temp = phone.replace("+", "")
        temp = temp.replace("-","")
        temp = temp.replace("(","")
        temp = temp.replace(")","")
        return temp
    
    def reform_message(self,msg):
        temp = msg.replace("_"," ")
        return temp
    
    def normalize_name(self,name):
        return ' '.join(sorted(name.split()))

    def find_matching_record(self,name, records, threshold=80):
        normalized_query = self.normalize_name(name)

        best_match = None
        highest_score = 0

        for record in records:
            # Skip records where the 'name' field is missing or None
            if not record.get('name'):
                continue

            # Remove common prefixes and suffixes (e.g., Mr., Dr., etc.) from both query and record names
            cleaned_record_name = ' '.join([word for word in record['name'].split() if word.lower() not in ['mr', 'mrs', 'dr', 'sir']])
            normalized_record_name = self.normalize_name(cleaned_record_name)
            similarity_score = fuzz.ratio(normalized_query, normalized_record_name)

            if similarity_score > highest_score and similarity_score >= threshold:
                highest_score = similarity_score
                best_match = record

        return best_match
