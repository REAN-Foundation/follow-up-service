import os
import json
import shutil
import requests

from app.common.appointment_api.appointment_utils import validate_mobile
from app.common.logtime import log_execution_time


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
    async def case_manager_notify(self,changed_data,date_str,case_manager_name):
        print('Sending message to admins')
        file_name = 'Case_manager_contact.json'
        current_path = os.getcwd()
        folder_path = os.path.join(current_path, "assets")
        exists = os.path.exists(folder_path)
        if exists:
            file_path = os.path.join(folder_path,file_name)
            print(file_path)
            file=open(file_path,"r")
            file_content=file.read()
            file_data=json.loads(file_content)
            for line in file_data:
                if case_manager_name.lower() in line['name'].lower():
                    admin_phone = (line['phone'])
                    # is_valid_mobile = validate_mobile(admin_phone)
                    # if not is_valid_mobile:
                    #      print('*Invalid phone-number - ', admin_phone)
                    phone_nos=self.reform(admin_phone)
                    print(phone_nos)
                    await self.send_msg_to_case_manager(phone_nos,changed_data,date_str)  

    async def send_msg_to_case_manager(self,phone_nos,changed_data,date_str):
        print(changed_data)
        participant_code= changed_data[0]['participant_code']
        date_str= date_str
        facility_name = changed_data[0]['facility_name']
        msg = self.reform_message(changed_data[0]['followup_assessment_reply'])
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
        response = requests.post(self.notification_base_url, headers=header, data=json.dumps(body))
        if response:
            print(response.json())
        else:
            print('Unable  ', response.json())

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