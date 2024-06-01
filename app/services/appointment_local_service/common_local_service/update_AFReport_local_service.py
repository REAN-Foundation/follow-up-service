import json
from app.common.enumclasses import PatientReplyEnum

from app.common.appointment.appointment_utils import valid_patient_reply
from app.common.utils import get_temp_filepath
class UpdateFile:
        
    async def update_reply_by_phone(self,filename, phone_number, new_data):
        file_path = get_temp_filepath(filename)
        print('Reply From WhatsApp',phone_number , ":", str(new_data))
        print("filename",filename)
        number = phone_number.replace(' ', '')
        print(number)
        with open(file_path, 'r') as file:
            data = json.load(file)
        patient_reply = valid_patient_reply(new_data['Patient_replied'])
        
        if filename.startswith('gmu_followup_file_'):
        # Updating patient reply for status Pending arrival
            for item in data:
                if item['Patient_status'] == 'Pending arrival':
                    if item['Phone_number'] == number:
                        #Once the reply is set to Yes/No we cannot set to Not replied
                        if patient_reply != PatientReplyEnum.Invalid_Patient_Reply:
                            item['Patient_replied'] =patient_reply
                            item['WhatsApp_message_id'] =new_data['WhatsApp_message_id']
        else:
        # Updating patient reply for status ANY
            for item in data:
                if item['Phone_number'] == number:
                    #Once the reply is set to Yes/No we cannot set to Not replied
                    if patient_reply != PatientReplyEnum.Invalid_Patient_Reply:
                        item['Patient_replied'] =patient_reply
                        item['WhatsApp_message_id'] =new_data['WhatsApp_message_id']

        with open(file_path, 'w') as file:
            json.dump(data, file, indent=7)
        
        with open(file_path, 'r') as file:
            data = json.load(file)

        return(data)
    