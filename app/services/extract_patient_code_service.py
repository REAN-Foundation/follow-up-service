
import json
import os

import requests
from app.common.cache import cache
from app.common.utils import get_temp_filepath
###########################################################
class ExtractPatientCode:
    def __init__(self):
        summary_data=[]
        self.patient_code_count = 0
        self.appointment_details= []

        gghn_base_url = os.getenv("GGHN_BASE_URL")
        if gghn_base_url == None:
            raise Exception('GGHN_BASE_URL is not set')
        
        self.patient_code_url = str(gghn_base_url + "/api/PharmacyPickup")
        self.token = cache.get('gghn_access_token')
        print("gghn token----",self.token)
       
    def read_content(self, date):
        self.token = cache.get('gghn_access_token')
        suburl = str(f'/QueryPatientByNextAppointment?startdate={date}T00:00:00&endDate={date}T23:59:59')
        url=str(self.patient_code_url+suburl)
        print("Patient code url----",url)
       
        headers = {
            'Authorization': "Bearer " + self.token,
            # 'Content-Type': 'application/json'
        }
        response = requests.post(url,headers = headers)
        result = response.json()
        # print("result",result)
        prefix="gghn_details_"
        file_name = self.create_data_file(result,date,prefix)
        self.extract_appointment(file_name,date)
        return (result)

    def create_data_file(self,resp_data,enquiry_date,prefix):
        filename=str(prefix+enquiry_date+'.json')
        f_path=(os.getcwd()+"/temp/"+filename)
        if os.path.exists(f_path):
            print(f"The file {filename} already exists. Please choose a different name.")
        else: 
            temp_folder = os.path.join(os.getcwd(), "temp")
            if not os.path.exists(temp_folder):
                os.mkdir(temp_folder)
            filepresent  = os.path.join(temp_folder, filename)
            with open(filepresent, 'w') as json_file:
                json.dump(resp_data, json_file, indent=25)
        return(filename)        
        # =json.dumps(result,indent=25)
        # print("summary data=",summary_data) 
    def extract_appointment(self, file_name,date):

        filepath = get_temp_filepath(file_name)
        if not os.path.exists(filepath):
            raise Exception(file_name + " does not exist.")

        file=open(filepath,"r")
        file_content=file.read()
        appointment_data=json.loads(file_content)
        appointment_details= []
        for data in appointment_data:
            patient_code_details={
                "facilityname":data['facilityname'],
                "next_appointment_date":data['next_appointment_date'],
                "participant_code":data['participant_code']
            }
            appointment_details.append(patient_code_details)
            self.patient_code_count= self.patient_code_count+1
        print("patient_code_count",self.patient_code_count)
        # print("appointments-----",appointment_details)  
        prefix = "gghn_appointment_"  
        file_name = self.create_data_file(appointment_details,date,prefix)
       