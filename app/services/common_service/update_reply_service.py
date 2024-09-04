import json
from app.common.appointment_api.appointment_utils import valid_patient_reply
from app.common.enumclasses import PatientReplyEnum
from app.services.common_service.db_service import DatabaseService
from app.services.common_service.read_report import ReadReport
class UpdateReply:
    def __init__(self): 
        # self.db_data = DatabaseService()
        pass

    async def update_reply_by_phone(self, filename, phone_number, new_data,storage_service):
        print('Reply From WhatsApp',phone_number , ":", str(new_data))
        print("filename",filename)
        number = phone_number.replace(' ', '')
        print(number)
       
        # if filename.startswith('gmu_appointment_'):
        data = await storage_service.search_file(filename)
        patient_reply = await valid_patient_reply(new_data['Patient_replied'])
            
        # Updating patient reply for status Pending arrival
        for item in data:
            if (item['patient_status'] == 'Pending arrival' or item['patient_status'] == ''):
                if item['phone_number'] == number:
                    #Once the reply is set to Yes/No we cannot set to Not replied
                    if patient_reply != PatientReplyEnum.Invalid_Patient_Reply:
                        item['patient_replied'] = patient_reply
                        item['whatsapp_message_id'] = new_data['WhatsApp_message_id']

        try:
            content = await storage_service.update_file(filename, data)
            read_data = ReadReport()
            changed_data =await read_data.readfile_content_by_ph(filename, number,storage_service)
            print("change...",changed_data)
            return(changed_data)
        except Exception as e:
            # Handle other exceptions
                print(f"An unexpected error occurred while updating{filename}: {e}")
                return(e)
            
        # if filename.startswith('gghn_appointment_'):
        #     data = await storage_service.search_file(filename)
        #     patient_reply = await valid_patient_reply(new_data['Patient_replied'])
        # # Updating patient reply for status ANY
        #     for item in data:
        #         if item['phone_number'] == number:
        #             #Once the reply is set to Yes/No we cannot set to Not replied
        #             if patient_reply != PatientReplyEnum.Invalid_Patient_Reply:
        #                 item['patient_replied'] =patient_reply
        #                 item['whatsapp_message_id'] =new_data['WhatsApp_message_id']

        #     try:
        #         content = await storage_service.update_file(filename,data)
        #         return(content)
        #     except Exception as e:
        #     # Handle other exceptions
        #         print(f"An unexpected error occurred while updating{filename}: {e}")
        #         return(e)
        