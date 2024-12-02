from ast import Dict
import json
import os
from fastapi import HTTPException
import requests
from app.common.cache import cache
# from app.services.common_service.db_service import DatabaseService
class ReadReport:
    def __init__(self):
        self.patients_count = 0
        self.arrived_patient_count = 0
        self.pending_arrival_patient_count = 0
        self.patient_reply_yes_count = 0
        self.patient_reply_no_count = 0
        self.patient_not_replied_count = 0
        self.patient_data=[]
        # self.db_data = DatabaseService()
        
    async def read_appointment_file(self,filename,storage_service):
        try:
            data = await storage_service.search_file(filename)
            if(data!= None):
                return(data)
            else:
                raise HTTPException(status_code=404, detail="File not found")
            
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="File not found")
        
    async def read_appointment_summary(self,filename,storage_service):
        file_name = filename.split('_')
        f_date  = '_'.join(file_name[2:])
        file_date = f_date.split('.')
        date_of_file = file_date[0]
        print(date_of_file) 
               
        data = await storage_service.search_file(filename)
        if(data!= None):
            for item in data:
                self.patients_count = self.patients_count + 1
                if item['patient_status'] == 'Pending arrival':
                    self.pending_arrival_patient_count = self.pending_arrival_patient_count + 1
                if item['patient_status'] == 'In lobby':
                    self.arrived_patient_count = self.arrived_patient_count + 1
                if item['patient_replied'] == 'Yes':
                    self.patient_reply_yes_count = self.patient_reply_yes_count + 1
                if item['patient_replied'] == 'No':
                    self.patient_reply_no_count = self.patient_reply_no_count + 1
                if item['patient_replied'] == 'Not replied':
                    self.patient_not_replied_count = self.patient_not_replied_count + 1
            
            file_summary = {
                'Date': date_of_file,
                'Total patient': self.patients_count,
                'Arrived patient' : self.arrived_patient_count,
                'Patient not arrived' : self.pending_arrival_patient_count,
                'Patient replied Yes' : self.patient_reply_yes_count,
                'Patient replied No' :  self.patient_reply_no_count,
                'Patient Not replied' : self.patient_not_replied_count
            }
        
            return(file_summary) 
        else:
                print("No file found")
                raise HTTPException(status_code=404, detail="File not found") 
    
    async def readfile_content_by_ph(self, filename, phone_number,storage_service):
        try:
            data = await storage_service.search_file(filename)
            
            if(data!= None):
                for item in data:
                    if item['phone_number'] == phone_number:
                        data={
                            'name_of_patient': item['name_of_patient'],
                            'facility_name': item['facility_name'],
                            'rean_patient_userid': item['rean_patient_userid'],
                            'appointment_time':item['appointment_time'],
                            'participant_code': item['participant_code'],
                            'patient_status': item['patient_status'],
                            'whatsapp_message_id':item['whatsapp_message_id'],
                            'patient_replied':item['patient_replied'],
                            'followup_assessment_reply':item['followup_assessment_reply'],
                            'case_manager':item['case_manager'],

                        }
                        self.patient_data.append(data)
                return(self.patient_data)
            
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Data not found")
        
    async def readfile_content_by_reply(self,filename,reply,storage_service):
        try:
            patient_reply_count = 0
            count = 0
            patient_reply_data=[]

            file_data = await storage_service.search_file(filename)
            if(file_data!= None):
                if(reply != None):
                    for item in file_data:
                        if item['patient_replied'] == reply:
                            patient_reply_count =patient_reply_count + 1
                            data={
                                'name_of_patient': item['name_of_patient'],
                                'facility_name': item['facility_name'],
                                'phone_number': item['phone_number'],
                                'appointment_time':item['appointment_time'],
                                'participant_code': item['participant_code'],
                                'patient_status': item['patient_status'],
                                'whatsapp_message_id':item['whatsapp_message_id'],
                                'patient_replied':item['patient_replied'],
                                'followup_assessment_reply':item['followup_assessment_reply'],
                                'case_manager':item['case_manager'],

                            }
                            patient_reply_data.append(data)
                    detail_data = {
                        'reply_count': patient_reply_count,
                        'reply_details' : patient_reply_data
                    }
                else: 
                    for item in file_data:
                        count = count + 1
                        data={
                            'name_of_patient': item['name_of_patient'],
                            'facility_name': item['facility_name'],
                            'phone_number': item['phone_number'],
                            'appointment_time':item['appointment_time'],
                            'participant_code': item['participant_code'],
                            'patient_status': item['patient_status'],
                            'whatsapp_message_id':item['whatsapp_message_id'],
                            'patient_replied':item['patient_replied'],
                            'followup_assessment_reply':item['followup_assessment_reply'],
                            'case_manager':item['case_manager'],
                        }
                        patient_reply_data.append(data)
                    detail_data = {
                        'reply_count': count,
                        'reply_details' : patient_reply_data
                    }
                return(detail_data)
            
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Data not found")