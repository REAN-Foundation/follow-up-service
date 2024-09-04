from ast import Dict
import json
import os
from fastapi import HTTPException
import requests
from app.common.cache import cache
from app.common.logtimeing import log_execution_time
from app.services.common_service.db_service import DatabaseService

class GGHNReadReport:
    def __init__(self):
        self.patients_count = 0
        self.arrived_patient_count = 0
        self.pending_arrival_patient_count = 0
        self.patient_reply_yes_count = 0
        self.patient_reply_no_count = 0
        self.patient_not_replied_count = 0
        self.patient_data=[]
        # self.db_data = DatabaseService()
       
    @log_execution_time
    async def gghn_read_appointment_file(self,filename,storage_service):
        try:
            data = await storage_service.search_file(filename)
            return(data)
            
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="File not found")
        
    @log_execution_time    
    async def gghn_read_appointment_summary(self,filename,storage_service):
        file_name = filename.split('_')
        f_date  = '_'.join(file_name[2:])
        file_date = f_date.split('.')
        date_of_file = file_date[0]
        print(date_of_file)
         
        data = await storage_service.search_file(filename)    
        for item in data:
            self.patients_count = self.patients_count + 1
            if item['patient_replied'] == 'Yes':
                self.patient_reply_yes_count = self.patient_reply_yes_count + 1
            if item['patient_replied'] == 'No':
                self.patient_reply_no_count = self.patient_reply_no_count + 1
            if item['patient_replied'] == 'Not replied':
                self.patient_not_replied_count = self.patient_not_replied_count + 1
        file_summary = {
            'Date': date_of_file,
            'Total patient': self.patients_count,
            'Patient replied Yes' : self.patient_reply_yes_count,
            'Patient replied No' :  self.patient_reply_no_count,
            'Patient Not replied' : self.patient_not_replied_count
                }
        return(file_summary) 
     
    