import json
class UpdateFile:
    # def update_content_by_id(self,file_path, patient_userid, new_data):
    #     with open(file_path, 'r') as file:
    #         data = json.load(file)

    #     for item in data:
    #         if item['patient_userid'] == patient_userid:
                
    #             item['patient_name'] = new_data['patient_name']
    #             item['phone_number'] = new_data['phone_number']
    #             item['appointment_time'] = new_data['appointment_time']
    #             item['appointment_status'] = new_data['appointment_status']
    #             item['WhatsApp_id'] = new_data['WhatsApp_id']
    #             item['reply'] = new_data['reply']
                
    #             break

    #     with open(file_path, 'w') as file:
    #         json.dump(data, file, indent=7)

    #     return(data)
        

    # def update_whatsapp_by_ph(self,file_path, phone_number, new_data):
    #     ph_number = (f"+{phone_number}")
    #     number = ph_number.replace(' ', '')
    #     print(number)
    #     with open(file_path, 'r') as file:
    #         data = json.load(file)

    #     for item in data:
    #         if item['phone_number'] == number:
    #             item['WhatsApp_id'] =new_data['WhatsApp_id']
    #             break

    #     with open(file_path, 'w') as file:
    #         json.dump(data, file, indent=7)
        
    #     with open(file_path, 'r') as file:
    #         data = json.load(file)

    #     return(data)
    
    def update_reply_by_phone(self,file_path, phone_number, new_data):
        number = phone_number.replace(' ', '')
        print(number)
        with open(file_path, 'r') as file:
            data = json.load(file)

        for item in data:
            if item['appointment_status'] == 'Pending arrival':
                if item['phone_number'] == number:
                    item['reply'] =new_data['reply']
                    item['WhatsApp_id'] =new_data['WhatsApp_id']
                    break

        with open(file_path, 'w') as file:
            json.dump(data, file, indent=7)
        
        with open(file_path, 'r') as file:
            data = json.load(file)

        return(data)
    