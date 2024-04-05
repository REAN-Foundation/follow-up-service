
import json
import os

import requests
from app.common.cache import cache
from app.common.exceptions import HTTPError, NotFound
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

    #Get Paitient details using gghn api   
    def read_content(self, date):
        try:
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
        except HTTPError:
            raise NotFound(status_code=404, detail="Resource not found")

    #Create/update a detail file of api out put 
    def create_data_file(self,resp_data,enquiry_date,prefix):
        filename=str(prefix+enquiry_date+'.json')
        f_path=(os.getcwd()+"/temp/"+filename)
        if os.path.exists(f_path):
            print(f"The file {filename} already exists.Now getting updated")
            flag = 0
            additional_appoints= []
            if prefix == 'gghn_details_':
                print("in file--",prefix)
                with open(f_path, 'r') as file:
                    file_data = json.load(file)
                    for entry in resp_data:
                        for item in file_data:
                        # for entry in resp_data:
                            if entry['participant_code'] == item['participant_code']:
                                flag = 1
                            else:
                                pass
                        if flag == 0:
                            additional_paitient={
                                "state": entry['state'],
                                "facilityname": entry['facilityname'],
                                "sex": entry['sex'],
                                "age":entry['age'],
                                "art_start_date": entry['art_start_date'],
                                "last_pickup_date": entry['last_pickup_date'],
                                "months_of_arv_refill": entry['months_of_arv_refill'],
                                "next_appointment_date":entry['next_appointment_date'],
                                "current_art_regimen": entry['current_art_regimen'],
                                "clinical_staging_at_last_visit": entry['clinical_staging_at_last_visit'],
                                "last_cd4_count": entry['last_cd4_count'],
                                "current_viral_load":entry['current_viral_load'],
                                "viral_load_status": entry['viral_load_status'],
                                "current_art_status": entry['current_art_status'],
                                "outcome_of_last_tb_screening":entry['outcome_of_last_tb_screening'],
                                "date_started_on_tb_treatment":entry['date_started_on_tb_treatment'],
                                "tb_treatment_type":entry['tb_treatment_type'],
                                "tb_treatment_completion_date": entry['tb_treatment_completion_date'],
                                "tb_treatment_outcome":entry['tb_treatment_outcome'],
                                "date_of_commencement_of_eac":entry['date_of_commencement_of_eac'],
                                "number_of_eac_sessions_completed": entry['number_of_eac_sessions_completed'],
                                "result_of_cervical_cancer_screening": entry['result_of_cervical_cancer_screening'],
                                "fingerprint_captured":entry['fingerprint_captured'],
                                "fingerprint_recaptured":entry['fingerprint_recaptured'],                                   
                                "participant_code":entry['participant_code']
                            }
                            additional_appoints.append(additional_paitient)
                        else:
                            flag=0
                    print("additional paitients are",additional_appoints)
                    file_data.append(additional_appoints)
                    with open(f_path, 'w') as json_file:
                        json.dump(resp_data, json_file, indent=25)
            else:
                if prefix == 'gghn_appointment_':
                    print("in file--",prefix)
                    with open(f_path, 'r') as file:
                        file_data = json.load(file)
                    for entry in resp_data:    
                        for item in file_data:
                            if entry['participant_code'] == item['participant_code']:
                                flag = 1
                            else:
                                pass
                        if flag == 0:
                            additional_paitient={
                                "facilityname": entry['facilityname'],
                                "next_appointment_date":entry['next_appointment_date'],                                                         
                                "participant_code":entry['participant_code'],
                                "paitient_phone":""
                                 }
                            additional_appoints.append(additional_paitient)
                        else:
                            flag=0
                    print("additional paitients are",additional_appoints)
                    file_data.append(additional_appoints)
                    with open(f_path, 'w') as json_file:
                        json.dump(resp_data, json_file, indent=25)
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

    #Create a file with only necessary details for appointment    
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
                "participant_code":data['participant_code'],
                "paitient_phone":""
            }
            appointment_details.append(patient_code_details)
            self.patient_code_count= self.patient_code_count+1
        print("patient_code_count",self.patient_code_count)
        # print("appointments-----",appointment_details)  
        prefix = "gghn_appointment_"  
        file_name = self.create_data_file(appointment_details,date,prefix)
      
       