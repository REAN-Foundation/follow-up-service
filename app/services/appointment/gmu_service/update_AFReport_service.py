import json
from app.common.enumclasses import PatientReplyEnum

from app.common.appointment.appointment_utils import valid_patient_reply
class UpdateFile:
        
    def update_reply_by_phone(self,file_path, phone_number, new_data):
        print('Reply From WhatsApp',phone_number , ":", str(new_data))
        number = phone_number.replace(' ', '')
        print(number)
        with open(file_path, 'r') as file:
            data = json.load(file)
        patient_reply = valid_patient_reply(new_data['Patient_replied'])

        # Updating patient reply for status Pending arrival
        for item in data:
            if item['Patient_status'] == 'Pending arrival':
                if item['Phone_number'] == number:
                    if patient_reply != PatientReplyEnum.Invalid_Patient_Reply:
                        item['Patient_replied'] =patient_reply
                        item['WhatsApp_message_id'] =new_data['WhatsApp_message_id']

        # # Updating patient reply for status ANY
        # for item in data:
        #    if item['Phone_number'] == number:
        #         if patient_reply != PatientReplyEnum.Invalid_Patient_Reply:
        #             item['Patient_replied'] =patient_reply
        #             item['WhatsApp_message_id'] =new_data['WhatsApp_message_id']

        with open(file_path, 'w') as file:
            json.dump(data, file, indent=7)
        
        with open(file_path, 'r') as file:
            data = json.load(file)

        return(data)
    