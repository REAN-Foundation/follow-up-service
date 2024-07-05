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
                            'Name of patient': item['name_of_patient'],
                            'Facility name':"",
                            'Rean patient userid': item['rean_patient_userid'],
                            'Appointment time':item['appointment_time'],
                            'Participant code':'',
                            'Patient status': item['patient_status'],
                            'WhatsApp message id':item['whatsapp_message_id'],
                            'Patient replied':item['patient_replied']
                        }
                        self.patient_data.append(data)
                return(self.patient_data)
            
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="File not found")