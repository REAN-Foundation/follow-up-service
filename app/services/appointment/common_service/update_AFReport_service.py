import json
from app.common.enumclasses import PatientReplyEnum

from app.common.appointment.appointment_utils import valid_patient_reply
from app.services.appointment.common_service.db_service import DatabaseService
class UpdateFile:
    def __init__(self): 
         self.db_data = DatabaseService()
         self.collection_prefix = ''

    def update_reply_by_phone(self, filename, phone_number, new_data):

        print('Reply From WhatsApp',phone_number , ":", str(new_data))
        print("filename",filename)
        number = phone_number.replace(' ', '')
        print(number)
        # with open(file_path, 'r') as file:
        #     data = json.load(file)
        if filename.startswith('gmu_followup_file_'):
            self.collection_prefix = 'gmu'
            data = self.db_data.search_file(filename,self.collection_prefix)
            patient_reply = valid_patient_reply(new_data['Patient_replied'])
        
        
        # Updating patient reply for status Pending arrival
            for item in data:
                if item['Patient_status'] == 'Pending arrival':
                    if item['Phone_number'] == number:
                        #Once the reply is set to Yes/No we cannot set to Not replied
                        if patient_reply != PatientReplyEnum.Invalid_Patient_Reply:
                            item['Patient_replied'] = patient_reply
                            item['WhatsApp_message_id'] = new_data['WhatsApp_message_id']

            try:
                content = self.db_data.update_file(filename, data, self.collection_prefix)
                return(content)
            except Exception as e:
            # Handle other exceptions
                print(f"An unexpected error occurred while updating{filename}: {e}")
                return(e)
            
        if filename.startswith('gghn_appointment_'):
            self.collection_prefix = 'gghn'
            data = self.db_data.search_file(filename, self.collection_prefix)
            patient_reply = valid_patient_reply(new_data['Patient_replied'])
        # Updating patient reply for status ANY
            for item in data:
                if item['Phone_number'] == number:
                    #Once the reply is set to Yes/No we cannot set to Not replied
                    if patient_reply != PatientReplyEnum.Invalid_Patient_Reply:
                        item['Patient_replied'] =patient_reply
                        item['WhatsApp_message_id'] =new_data['WhatsApp_message_id']

            try:
                content = self.db_data.update_file(filename,data,self.collection_prefix)
                return(content)
            except Exception as e:
            # Handle other exceptions
                print(f"An unexpected error occurred while updating{filename}: {e}")
                return(e)
        