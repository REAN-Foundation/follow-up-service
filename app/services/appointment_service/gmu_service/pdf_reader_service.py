from datetime import datetime
import os
import json
import camelot
import pdfplumber
from dateutil import parser
from app.common.utils import get_temp_filepath
from app.services.appointment_service.common_service.db_service import DatabaseService
import pandas as pd

###############################################################

months = {
    'January'  : '01',
    'February' : '02',
    'March'    : '03',
    'April'    : '04',
    'May'      : '05',
    'June'     : '06',
    'July'     : '07',
    'August'   : '08',
    'September': '09',
    'October'  : '10',
    'November' : '11',
    'December' : '12'
}

###############################################################

class PdfReader:
    def __init__(self):
        self.count = 0
        self.invalid_record_count = 0
        self.all_appointments = []
        self.invalid_appointments = []
        self.total_table_count = 0
        self.total_rows = 0
        self.data = {}
        self.db_data = DatabaseService()
        self.collect_prefix = 'gmu'


    def extract_appointments_from_pdf(self, input_file_path):
        try:
            if not os.path.exists(input_file_path):
                raise Exception(input_file_path + " does not exist.")

            tables = camelot.read_pdf(filepath=input_file_path, pages="all", suppress_stdout=True)
            self.total_table_count = tables.n
            if self.total_table_count == 0:
                raise Exception("No tables inside the pdf.")

            all_appointments_ = []
            invalid_data_ = []

            for i in range(self.total_table_count):
                row_count, column_count = self.get_shape(tables[i].df)
                self.total_rows = self.total_rows + row_count
                filename = "temp_appointments_" + str(i) + ".json"
                # Convert the Camelot Table to a pandas DataFrame
                df = tables[i].df
                # Convert the DataFrame to a JSON string
                json_string = df.to_json(orient='records')
                # json_string = tables[i].to_json()
                print("json_string..",json_string)
                content = self.db_data.search_file(filename, self.collect_prefix)
                if(content != None):
                    self.db_data.update_file(filename, json_string, self.collect_prefix)
                else:
                    self.db_data.store_file(filename, json_string, self.collect_prefix)
                # temp_filepath = get_temp_filepath(filename)
                # tables[i].to_json(temp_filepath)
                appointments = self.extract_table_appointments(filename)
                all_appointments_.extend(appointments)
               

            self.all_appointments = all_appointments_
            # self.debug_log(self.all_appointments)
            print('All Appointments extracted successfully')
            return self.all_appointments

        except Exception as e:
            print(e)
            return None

    def extract_table_appointments(self, filename):
        file_content = self.db_data.search_file(filename,self.collect_prefix)
        # filepath = get_temp_filepath(file_name)
        # if not os.path.exists(filepath):
        #     raise Exception(filepath + " does not exist.")

        # file=open(filepath,"r")
        # file_content=file.read()
        table_data=json.loads(file_content)
        print("...", table_data)

        all_appointments = []

        for row in table_data:
            if row['0']!='STATUS':
                status = row['0']
                patient_info = row['1']
                time = row['2']
                provider = row['3']
                type_of_visit = row['4']
                cheif_compliant = row['5']

                patient_details = patient_info.split('\n')
                if len(patient_details) == 3:
                    patient_name = patient_details[0]
                    patient_mobile = patient_details[2]
                    patient = {
                        "Status": status,
                        "PatientName": patient_name,
                        "PatientMobile": self.sanitize_mobile(patient_mobile),
                        "AppointmentTime": time,
                        "Provider": provider,
                        "TypeofVisit": type_of_visit,
                        "ChiefComplaint": cheif_compliant
                    }
                    all_appointments.append(patient)
                    self.count = self.count + 1
                else:
                    self.invalid_record_count = self.invalid_record_count + 1
                    print('*Invalid record found: ', row)
                    self.invalid_appointments.append(row)
        # self.create_file_for_invalid_record(self.invalid_appointments)
        return all_appointments
        # return (self.data)
    
    def create_file_for_invalid_record(self,invalid_appointments):
        filename=str('Invalid_Record.json')
        temp_folder = os.path.join(os.getcwd(), "temp")
        if not os.path.exists(temp_folder):
            os.mkdir(temp_folder)
        filepresent  = os.path.join(temp_folder, filename)
        with open(filepresent, 'w') as json_file:
                json.dump(invalid_appointments, json_file)
        json_string = json.dumps(invalid_appointments)
        return(json_string)

    def get_shape(self, df):
        return [df.count()[0],len(df.columns)]

    def sanitize_mobile(self, phone):
        temp = phone.replace("M.", "")
        if temp.startswith('+91'):
            return temp
        temp = temp.replace("(", "")
        temp = temp.replace(")", "")
        temp = temp.replace("-", "")
        temp = temp.replace(" ", "")
        temp = "+1-" + temp
        return temp

    def extract_reminder_date(self, filepath):
        # filepath = get_temp_filepath(file_name)
        if not os.path.exists(filepath):
            raise Exception(filepath + " does not exist.")
        with pdfplumber.open(filepath) as pdf:
            page_data = pdf.pages[0].extract_text().split('\n')[0].split(',')
            if len(page_data) >= 2:
                mmdd = page_data[1].strip().split(' ')
                dd = mmdd[1].strip()
                mm = months[mmdd[0]]
                yyyy = page_data[2].strip()
                date = yyyy+'-'+mm+'-'+dd
                try:
                    if bool(parser.parse(date)):
                        print('Date is extracted correctly & It is valid')
                        return date
                except:
                    return None
            else:
                return None

    def debug_log(self, all_appointments):

        # Dump the extraction into a json file
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        extracted_appointments =  json.dumps(all_appointments, indent=4)
        filepath = get_temp_filepath("extracted_appointments_" + timestamp + ".json")
        with open(filepath, "w") as outfile:
            outfile.write(extracted_appointments)

        # Summarize the extraction
        summary = {
            "Total tables in pdf ": self.total_table_count,
            "Total numbers of rows including columns headers ": self.total_rows,
            "Total patients records extracted into json ": self.count,
            "Total invalid records ": self.invalid_record_count,
            "Invalid Patient Conversion": self.invalid_appointments
        }
        print(summary)
