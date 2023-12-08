from ast import Dict
import json
import os
from fastapi import HTTPException
import requests
from app.common.cache import cache
class ReadReport:
    def __init__(self):
        self.patients_count = 0
        self.arrived_patient_count = 0
        self.pending_arrival_patient_count = 0
        self.patient_reply_yes_count = 0
        self.patient_reply_no_count = 0
        self.patient_not_replied_count = 0

    def read_report_file(self,file_path):
        try:
            with open(file_path, "r") as file:
                json_content = json.load(file)
            print(f"filename{ file_path}, content{ json_content}")
            return(json_content)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="File not found")
        
    def read_report_summary(self,file_path,filename):
        file_name = filename.split('.')
        f_name = file_name[0].split('e')
        file_date = f_name[1]
        # reverse str but no use wrong answer
        # filedate = str(filedate_obj)
        # file_date = filedate[::-1]
        print(file_date) 
               
        with open(file_path, 'r') as file:
            data = json.load(file)

        for item in data:
            self.patients_count = self.patients_count + 1
            if item['appointment_status'] == 'Pending arrival':
                self.pending_arrival_patient_count = self.pending_arrival_patient_count + 1
            if item['appointment_status'] == 'In lobby':
                self.arrived_patient_count = self.arrived_patient_count + 1
            if item['reply'] == 'Yes':
                self.patient_reply_yes_count = self.patient_reply_yes_count + 1
            if item['reply'] == 'No':
                self.patient_reply_no_count = self.patient_reply_no_count + 1
            if item['reply'] == 'Not replied':
                self.patient_not_replied_count = self.patient_not_replied_count + 1
        
        file_summary = {
            'Date': file_date,
            'Patients_in_lobby' : self.arrived_patient_count,
            'Pending_arrival' : self.pending_arrival_patient_count,
            'Patient_replied_Yes' : self.patient_reply_yes_count,
            'Patient_replied_No' :  self.patient_reply_no_count,
            'Patient_Not_replied' : self.patient_not_replied_count
        }
      
        return(file_summary) 
        